---
sidebarDepth: 2
---

# MeltanoData Guide

This will be the single source of truth for team members when it comes to creating and managing Meltano instances on MeltanoData.com.

## Creating a New Instance

### Prerequisites

- DigitalOcean Account
- Access to DigitalOcean teams "Meltano" and "MeltanoData DBs" 1 through 10
- Client's tenant name (i.e., company name, etc.)
- Access to the [Controller Node](/handbook/engineering/meltanodata-guide/controller-node.html)

### Step 1: Generate and store Meltano UI admin credentials

1. Clone the https://gitlab.com/meltano/infrastructure repository if you haven't already
2. Change directory into your local copy of the `meltano/infrastructure` repository
3. Ensure your local copy is up to date with the server

```sh
git checkout master
git pull
```

4. Run the `add_admin` script to add a new `$TENANT_NAME` admin user

```sh
./scripts/add_admin.py $TENANT_NAME $TENANT_NAME
```

5. Add the credentials to the 1Password `meltanodata.com` vault with title `$TENANT_NAME.meltanodata.com`

6. Run the `add_admin` script to add a new `meltano` admin user

```sh
./scripts/add_admin.py $TENANT_NAME meltano
```

7. Add the credentials to the 1Password `meltanodata.com` vault with title `meltano@$TENANT_NAME.meltanodata.com`

8. Commit the result and push to the server

```sh
git commit -am "Add admin users for new instance"
git push
```

### Step 2: Create new instance (droplet, domain record, and database)

1. Make sure ssh-agent is registered
2. [Access the Controller Node](/handbook/engineering/meltanodata-guide/controller-node.html#accessing-the-controller-node)
3. Ensure you can [connect to DigitalOcean](/handbook/engineering/meltanodata-guide/controller-node.html#connecting-to-digitalocean)

4. Change directory into `/var/meltano/infrastructure`

```sh
cd /var/meltano/infrastructure
```

5. Run the `create_instances` script. You can provide multiple subdomains in multiple arguments.

```sh
./scripts/create_instances.sh $TENANT_NAME
```

### Step 3: Store Postgres connection details

1. Ensure you are still in your local copy of the `meltano/infrastructure` repository

2. Run the `set_postgres_creds` script, where `$URI` is the database connection URI output by the `create_instances` script

```sh
./scripts/set_postgres_creds.py $TENANT_NAME $URI
```

8. Commit the result and push to the server

```sh
git commit -am "Add Postgres connection details for new instance"
git push
```

### Step 4: Configure instance

1. Ensure you are still SSHed into the controller node, in the `/var/meltano/infrastructure` directory

2. Run the Setup playbook. You can provide multiple hostnames to `--limit` separated using commas.

```sh
ansible-playbook playbooks/setup.yml --limit=$TENANT_NAME.meltanodata.com
```

3. Verify that the `meltano` service is working properly

```bash
systemctl status meltano
```

### Step 5: Validate Meltano UI

#### Ensure everything works

1. Visit `https://$TENANT_NAME.meltanodata.com` in your browser
1. Log in with credentials for the `meltano` user output by the `add_admin` script

And with that, we're good to go! 🎉

## Maintaining an Existing Instance

::: warning
Make sure to run all `meltano` commands using the `meltano` user account by doing

```bash
su meltano
```

Failing to do so could cause permissions problems and degrade the service.
:::

### Upgrade a Meltano instance manually

In the event you need to manually update the droplet's Meltano version:

1. SSH into the droplet
1. Switch to the `meltano` user

```bash
su meltano
```

::: warning
It is important to use the `meltano` user when upgrading because new files could be created with the wrong permissions.
:::

1. Activate the virtual environment

```bash
source /var/meltano/.venv/bin/activate
```

3. Change into the Meltano project directory

```bash
cd /var/meltano/project
```

4. Run Meltano upgrade command

```bash
meltano upgrade
```

And that's it. No need to restart the service at all!

### Wipe database in Meltano demo instance

#### Get credentials to access PostgreSQL

1. Login to DigitalOcean
1. Click on **Database** in left side menu
1. Open Meltano database cluster
   - This is tricky since the current cluster doesn't have meltano appended to it, but you can verify this by checking the trusted sources to verify it's the correct one
1. In the **Connection Details** section on the right, open the dropdown with the default label `Connection parameters`
1. Select `Flags`
1. Copy the snippet using the **Copy** button so it properly copies the password hash

#### Drop schemas in database

1. Open your terminal
1. Paste the snippet from `Flags` and press `Enter`

   - If you get an error regarding a missing `psql` installation, you'll need to install `psql-client`

   ```bash
   # We are looking for the current version
   apt search psql-client
   # Add the current version, which is 10 right now
   install psql-client-10
   ```

If you are successful, you should see be put in the psql prompt and see:

```
defaultdb=>
```

3. Check for the existing schemas:

```
\dn
```

4. For each schema EXCEPT `public`, run the following command:

```sql
DROP SCHEMA $EXISTING_SCHEMA_NAME CASCADE;
```

5. Once you're done, you can exit by pressing `Ctrl + D`

## Debugging an Existing Instance

### 500 error when accessing instance on browser

::: warning Error
{"error":"500 Internal Server Error: The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."}
:::

If you see this error, most likely this is due to an issue with Meltano itself. In order to access the logs to debug this:

1. SSH into the droplet
1. Check system status and processes with

```bash
systemctl status
```

- Under `meltano.service`, you will see a directory path that will provide you with a hint towards where things live

3. To check the logs, go to `/var/meltano/project/.meltano/run`
4. The log used to debug this last time was `meltano-ui.log`

### 500 error when FTPing into instance

::: warning Error
Response: 500 OOPS: vsftpd: refusing to run with writable root inside chroot()
:::

This means that the permissions on the root directory you are trying to access need to be changed. This should not be an issue on future images, but in case it is, you'll need a command similar to:

```bash
chmod g-w /var/meltano/project
```

### /var/meltano/project/.env has been overwritten

This file should only host the feature flags of Meltano, so that it can be hot-reloaded using `systemctl reload meltano` instead of having to reboot the whole worker fleet.

::: warning
Sensitive data should only be stored in `/etc/meltano/environment.d`, because its ACLs are exclusive to the `meltano` user.
:::

This file is managed by ansible, so you'll have to create an infrastructure issue, or create a new file in `/etc/meltano/environment.d`, which are loaded at every cold-boot.

### DNS Spoofing Error

If you get this error when you try to SSH into a droplet:

```
@       WARNING: POSSIBLE DNS SPOOFING DETECTED!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
The ECDSA host key for $TENANT_NAME.meltanodata.com has changed,
and the key for the corresponding IP address 12.345.6.78
is unknown. This could either mean that
DNS SPOOFING is happening or the IP address for the host
and its host key have changed at the same time.
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ECDSA key sent by the remote host is
SHA256:12345.
Please contact your system administrator.
Add correct host key in /Users/bencodezen/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in /Users/bencodezen/.ssh/known_hosts:34
ECDSA host key for emilygitlab.meltanodata.com has changed and you have requested strict checking.
Host key verification failed.
```

This means that you have an old entry in the `known_hosts` file. To fix this, simply open `/Users/$USERNAME/.ssh/known_hosts` in a text editor and delete the domain in question.

### Caddy Service Failed Error

If the `caddy.service` is not working, you'll get an error similar to the following during [Step 4: Restart Caddy](/handbook/engineering/meltanodata-guide/#restart-caddy):

```bash
# systemctl status

● $TENANT_NAME
    State: degraded
     Jobs: 0 queued
   Failed: 1 units
    Since: Tue 2019-12-10 11:24:40 UTC; 35min ago
   ... ... ...

# systemctl --failed

  UNIT          LOAD   ACTIVE SUB    DESCRIPTION
● caddy.service loaded failed failed Caddy HTTP/2 web server

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

1 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.

```

The reason may be that we have hit the [rate limit of 50 Certificates per Registered Domain per week](https://letsencrypt.org/docs/rate-limits/) in let's encrypt.

To investigate this, run caddy manually and check the output. If you get the following error, then the reason for the failure is that we have hit the 50 Certificates rate limit:

```bash
# systemctl stop caddy
# env $(< /etc/caddy/environment) /usr/local/bin/caddy -conf /etc/caddy/Caddyfile
Activating privacy features... 2019/12/10 12:03:47 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:48 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:49 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:50 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:51 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:52 [INFO] [$TENANT_NAME.meltanodata.com] acme: Obtaining bundled SAN certificate
2019/12/10 12:03:53 failed to obtain certificate: acme: error: 429 :: POST :: https://acme-v02.api.letsencrypt.org/acme/new-order :: urn:ietf:params:acme:error:rateLimited :: Error creating new order :: too many certificates already issued for: meltanodata.com: see https://letsencrypt.org/docs/rate-limits/, url:
```

There are two options:

- The call is in more than 2 days and you can wait
- You have to setup the instance ASAP

In the later case, the only option at the moment is to setup the instance with a self signed certificate.

(1) Revert the update we do in /etc/caddy/Caddyfile back to tls self_signed

(2) Add a :443 in the end of the /etc/caddy/environment

```bash
HOSTNAME=$TENANT_NAME.meltanodata.com:443
```

(3) Restart Caddy manually

```bash
systemctl stop caddy
systemctl daemon-reload
systemctl start caddy
```

And verify that this worked, by running the following command:

```bash
systemctl status
```

You can now directly access the instance by adding the https:// in front of the domain the first time you access it:

https://{$TENANT_NAME}.meltanodata.com/

You'll get a `Privacy Error: NET::ERR_CERT_AUTHORITY_INVALID`, but choose to `Proceed to $TENANT_NAME.meltanodata.com (unsafe)` (e.g. by first clicking on `Advanced` if you are using Chrome)

## Deleting an instance

When a client no longer needs a hosted instance of Meltano on meltanodata.com, you need to:

1. Make sure ssh-agent is registered
2. [Access the Controller Node](/handbook/engineering/meltanodata-guide/controller-node.html#accessing-the-controller-node)
3. Ensure you can [connect to DigitalOcean](/handbook/engineering/meltanodata-guide/controller-node.html#connecting-to-digitalocean)

4. Change directory into `/var/meltano/infrastructure`

```sh
cd /var/meltano/infrastructure
```

5. Run the `delete_instances` script. You can provide multiple subdomains in multiple arguments.

```sh
./scripts/delete_instances.sh $TENANT_NAME
```

1. If the database cluster was created in a "MeltanoData DBs" team that is currently marked "(full)", edit the team name to indicate it is no longer full
1. Delete the client's passwords in 1Password
