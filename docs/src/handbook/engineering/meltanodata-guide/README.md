---
sidebarDepth: 2
---

# MeltanoData Guide

::: warning
We no longer offer hosted Meltano instances on MeltanoData.com, but the documentation below is preserved for historical context as long as some instances are still online.
:::

This will be the single source of truth for team members when it comes to creating and managing Meltano instances on MeltanoData.com.

## Creating a New Instance

::: warning
These steps (should) have been completed automatically after a user signs up on TypeForm, through the Zapier integration which calls an endpoint on the controller node which triggers the setup script.

Only follow these steps manually if automatic setup appears to have failed.
:::

1. Make sure ssh-agent is registered
2. [Access the Controller Node](/handbook/engineering/meltanodata-guide/controller-node.html#accessing-the-controller-node)
3. Ensure you can [connect to DigitalOcean](/handbook/engineering/meltanodata-guide/controller-node.html#connecting-to-digitalocean)

4. Change directory into `/var/meltano/infrastructure`

```shell
cd /var/meltano/infrastructure
```

5. Run the `setup` script.

```shell
./scripts/setup.sh "$FULL_NAME" "$EMAIL" "$SUBDOMAIN"
```

That's it! The script will automatically set up the instance and send the user their login info by email.

## Maintaining an Existing Instance

::: warning
Make sure to run all `meltano` commands using the `meltano` user account by doing

```shell
su meltano
```

Failing to do so could cause permissions problems and degrade the service.
:::

### Upgrade a Meltano instance manually

In the event you need to manually update the droplet's Meltano version:

1. SSH into the droplet
1. Switch to the `meltano` user

```shell
su meltano
```

::: warning
It is important to use the `meltano` user when upgrading because new files could be created with the wrong permissions.
:::

1. Activate the virtual environment

```shell
source /var/meltano/.venv/bin/activate
```

3. Change into the Meltano project directory

```shell
cd /var/meltano/project
```

4. Run Meltano upgrade command

```shell
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

   ```shell
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

```shell
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

```shell
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

```shell
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

```shell
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

```shell
HOSTNAME=$TENANT_NAME.meltanodata.com:443
```

(3) Restart Caddy manually

```shell
systemctl stop caddy
systemctl daemon-reload
systemctl start caddy
```

And verify that this worked, by running the following command:

```shell
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

```shell
cd /var/meltano/infrastructure
```

5. Run the `delete_instances` script. You can provide multiple subdomains in multiple arguments.

```shell
./scripts/delete_instances.sh $TENANT_NAME
```

1. If the database cluster was created in a "MeltanoData DBs" team that is currently marked "(full)", edit the team name to indicate it is no longer full
1. Delete the client's passwords in 1Password
