---
sidebarDepth: 2
---

# MeltanoData Guide

This will be the single source of truth for team members when it comes to creating and managing Meltano instances on MeltanoData.com.

## Creating a New Instance

### Prerequisites

- DigitalOcean Account
- Access to DigitalOcean Meltano team
- Client's tenant name (i.e., company name, etc.)
- Access to the [Controller Node](/handbook/engineering/meltanodata-guide/controller-node.html)

::: info
**DigitalOcean limits**

Our DigitalOcean account is currently limited to 500 droplets and 50 database clusters.
Since each Meltano instance requires one droplet and one cluster, our effective instance limit is 50.

When we get close to hitting either of these limits, we can get them increased by sending an email to one of our contacts at DigitalOcean.
:::

### Step 1: Create a New Droplet

1. Login to DigitalOcean
1. Access the Meltano project workspace
1. In the upper right, click on the `Create` button
1. Select `Droplets` from the dropdown menu

#### Choose an image

1. Select the `Snapshots` tab
1. Select the first image in the upper left corner (e.g., `Ubuntu meltano-123456789`)

#### Choose a plan

1. Leave it on `Standard`
1. Change machine plan cost to:
   - \$15 / month
   - 2 GB / 2 CPUs
   - 60 GB SSD Disk
   - 3 TB transfer

#### Add block storage

1. Leave empty

#### Choose a datacenter region

1. You can leave the default (e.g., New York 3), but make note which it is since you'll need it later on

#### Select additional options

1. Leave everything unselected

#### Authentication

1. Select `SSH keys` if it is not selected by default
1. Click `Select all` to provide all team members ability to access the droplet

::: warning
If your SSH key is not included in the list above, make sure to add it now through the `New SSH Key` button.
:::

#### Finalize and create

1. Leave droplet at `1 droplet`
1. For the hostname, use the desired URL for this client (i.e., `$TENANT_NAME.meltanodata.com`)
1. Under tags, add `production`

#### Select Project

1. Leave the default as `Meltano`

#### Add backups

1. Leave `Enable backups` unchecked

#### Create droplet

1. Click on `Create droplet` to start the process.

Once the droplet has completed setting up, you should see it in your `Droplets` table with an assigned IP address.

#### Verify droplet is working

1. Open your terminal
1. Ping the IP address with the command:

```bash
ping 123.456.789.01
```

If successful, you should see a message similar to:

```
PING 123.456.789.01: 56 data bytes
64 bytes from 123.456.789.01: icmp_seq=0 ttl=56 time=14.539 ms
64 bytes from 123.456.789.01: icmp_seq=1 ttl=56 time=13.931 ms
64 bytes from 123.456.789.01: icmp_seq=2 ttl=56 time=12.279 ms
64 bytes from 123.456.789.01: icmp_seq=3 ttl=56 time=19.898 ms
64 bytes from 123.456.789.01: icmp_seq=4 ttl=56 time=19.096 ms
64 bytes from 123.456.789.01: icmp_seq=5 ttl=56 time=18.507 ms
^C
--- 123.456.789.01 ping statistics ---
6 packets transmitted, 6 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 12.279/16.375/19.898/2.901 ms
```

### Step 2: Configure Network

1. Click on the `Networking` link on the left side menu
1. Under the **Domains** tab, click on `meltanodata.com` to access the DNS records dashboard

#### Create a new record for the client

1. The current tab should be `A` records
1. Under **Hostname**, fill in your client's `$TENANT_NAME`
1. Under **Will Direct To**, use the autocomplete to locate the new droplet you created (or paste in the IP address from the Droplets table if it is not appearing)
1. Leave **TTL (seconds)** with the default of `3600`
1. Click `Create Record`

#### Make sure everything works

1. Open your Terminal
1. Ping the URL with the command:

```bash
ping $TENANT_NAME.meltanodata.com
```

If everything works, you should see a message similar to before:

```bash
PING $TENANT_NAME.meltanodata.com (123.456.789.01): 56 data bytes
64 bytes from 123.456.789.01: icmp_seq=0 ttl=56 time=14.539 ms
64 bytes from 123.456.789.01: icmp_seq=1 ttl=56 time=13.931 ms
64 bytes from 123.456.789.01: icmp_seq=2 ttl=56 time=12.279 ms
64 bytes from 123.456.789.01: icmp_seq=3 ttl=56 time=19.898 ms
64 bytes from 123.456.789.01: icmp_seq=4 ttl=56 time=19.096 ms
64 bytes from 123.456.789.01: icmp_seq=5 ttl=56 time=18.507 ms
^C
--- $TENANT_NAME.meltanodata.com ping statistics ---
6 packets transmitted, 6 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 12.279/16.375/19.898/2.901 ms
```

If you are getting an error, give it a few more minutes since the records needs to propogate. If it is not working after 30 minutes though, please raise an issue with the team.

### Step 3: Create Database Cluster

1. Select `Databases` link in the left side menu
1. In the upper right, click on `Create` button
1. Select `Databases` from the dropdown

#### Choose a database engine

1. Leave default as `PostgreSQL 11`

#### Choose a cluster configuration

1. Leave default on `$15/mo: 1 GB RAM / 1 vCPU / 10 GB Disk` plan

#### Choose a datacenter

1. Choose the same geolocation as the droplet if possible

#### Finalize and create

1. Under **Choose a unique database cluster name**, append the automatically generated name with `-$TENANT_NAME` (e.g., `db-postgresql-nyc3-52483-$TENANT_NAME`)
1. Under **Select project**, leave it as the default `Meltano`
1. Click `Add Tags` and add `production`
1. Click on `Create a Database Cluster`

#### Configure the database

1. Click the `Get Started` button
1. Restrict inbound connections by adding the recently created droplet under **Add trusted sources**
1. Click `Allow these inbound sources only` button
1. Click `Continue` to move past "Connection details"
1. Click `Great, I'm done` for "Next Steps" section

You should see `Connection details` on the right side of the page which is important for later on. It contains your database credentials and will be needed in the next section.

### Step 4: Configure Meltano Droplet Networking

1. SSH into your newly created droplet

```bash
ssh root@$TENANT_NAME.meltanodata.com
```

::: info
**Troubleshooting**

If you can't connect, make sure the SSH key you registered on you DigitalOcean account is loaded by using:

```bash
# by default, only `~/.ssh/id_rsa` is loaded into SSH agent
ssh-add /path/to/your/ssh-key
```

For more informations about using `ssh`, take a look at https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys#basic-connection-instructions
:::

#### Run Ansible Playbooks

1. Make sure ssh-agent is registered
1. Log in the Controller Node
1. Export DigialOcean token

```
export DO_API_TOKEN=200bc90fb6c8ad0ba904c1c3a8991e0701f7be8a4670afc2810420abc8c6ce43
```

##### Configure HTTPS Protocol

and run the `playbook/ssl.yml` playbook. To speed up the process, you can use `--limit=$TENANT_NAME.meltanodata.com`.

```
ansible-playbook playbooks/ssl.yml --limit=TENANT.meltanodata.com
```

You should get a response such as:

```
PLAY [*.meltanodata.com] *********************************************************************************************

TASK [Copy the `*.meltanodata.com` certificate] **********************************************************************
changed: [64.225.4.60]

TASK [Copy the `*.meltanodata.com` key] ******************************************************************************
changed: [64.225.4.60]

PLAY RECAP ***********************************************************************************************************
64.225.4.60                : ok=2    changed=2    unreachable=0    failed=0
```

##### Configure Caddyfile

1. Run caddy.yml playbook

```
PLAY [*.meltanodata.com] *********************************************************************************************

TASK [/etc/caddy/Caddyfile] ******************************************************************************************
changed: [64.225.4.60]

TASK [Restart caddy] *************************************************************************************************
changed: [64.225.4.60]

PLAY RECAP ***********************************************************************************************************
64.225.4.60                : ok=2    changed=2    unreachable=0    failed=0
```

##### Verify changes were made

1. SSH into droplet
1. Verify `/etc/caddy/Caddyfile` looks like:

```
{$HOSTNAME}:80, {$HOSTNAME}:443

# HTTP → HTTPS redirect
redir 301 {
  if {scheme} is http
  /  https://{host}{uri}
}

basicauth /static/js meltano htpasswd=/etc/caddy/htpasswd

# use a self-signed certificate if need be
# tls self_signed

# enable the Let's Encrypt certificate routine
# warning: only do this if the DNS is propagated
# or else you might blow the daily failure limit
tls /etc/caddy/com.meltanodata.crt /etc/caddy/com.meltanodata.key

proxy / localhost:5000 {
  transparent
}

gzip
```

Then restart caddy using:

```
systemctl restart caddy
```

::: tip
Navigate vim with arrow keys and press `I` key to enter Insert mode so you can modify the text
:::

::: tip
To exit Insert mode, press the `Esc` key, type `:wq`, and press `Enter` to save and quit vim
:::

#### Configure Caddy Environment

1. You should still be logged in to the droplet
1. Open `/etc/caddy/environment` in text editor

```bash
vim /etc/caddy/environment
```

3. Replace `$HOSTNAME` with the client's `$TENANT_NAME`

```
HOSTNAME=$TENANT_NAME.meltanodata.com
```

4. Save and quit file

#### Change Login Password

1. You should be logged in to the droplet
1. Create a new login in 1Password under the `meltanodata.com` vault
   - **Title** should be URL (e.g., `$TENANT_NAME.meltanodata.com`)
   - **Username** is `meltano`
   - **Password** should be randomly generated by 1Password
   - **Website** should be `$TENANT_NAME.meltanodata.com`
   - Save the newly created login
   - Leave this open because you will need the password shortly
1. In the terminal, run the following command with `$PASSWORD` replaced with the 1Password generated one:

```bash
htpasswd -b /etc/caddy/htpasswd meltano "$PASSWORD"
```

If you get the message `Updating password for user meltano`, you were successful in updating the login password.

#### Change FTP Login Password

1. You should be logged in to the droplet
1. Create a new login in 1Password under the `meltanodata.com` vault
   - **Title** should be `meltano_ftp@$TENANT_NAME.meltanodata.com`
   - **Username** is `meltano_ftp`
   - **Password** should be randomly generated by 1Password
   - **Website** should be `$TENANT_NAME.meltanodata.com`
   - Save the newly created login
   - Leave this open because you will need the password shortly
1. In the terminal, run the following command:

```bash
passwd meltano_ftp
```

1. You will be prompted for a new UNIX password, copy and paste the 1Password generated password and press `Enter`
1. You will be prompted to confirm the password, copy and paste the 1Password generated password again and press `Enter`

Once you see `passwd: password updated successfully`, you are good to go!

#### Restart Caddy

Now that the configurations are made, you need to restart Caddy by running the following command:

```bash
systemctl restart caddy
```

To verify this worked, you can run the following command:

```bash
systemctl status
```

You should scan for the following services to make sure Meltano properly running:

- `caddy.service`
- `meltano.service`
- `vsftpd.service`

::: tip
If you see a state of `running` in the status output, that means all services are running.

If you see a state of `degraded`, that means something is wrong — use `systemctl --failed` to have a quick glance.

If the `caddy.service` is reported as failed, investigate if this is an issue with the [let's encrypt certificate](/handbook/engineering/meltanodata-guide/#debugging-tls-certificate)
:::

### Step 5: Configure PostgreSQL Database

#### Get credentials for database ready

1. Login to DigitalOcean
1. Click on `Database` in left side menu
1. Select database instance for `db-postgresql-nyc1-01234-$TENANT_NAME`

You should now be on the **Overview** tab and should see the **Connection Details** on the right side. It will contain critical information such as:

- username
- password
- host
- port
- database

Keep this tab open because you'll need to refer to it shortly.

#### Setup the Meltano environment variables

Because we manage the database instance for each tenant, we use environment variables to configure `target-postgres`as a simple and secure way of configuring the plugin.

To do this, you need to:

1. SSH into the droplet
1. Change directory into `/var/meltano/project`
1. If it doesn't exist already, create a new `.env` file and open it in a text editor

```bash
vim .env
```

4. Copy and paste the following template into the `.env` file

```bash
PG_USERNAME=doadmin # default DO credential
PG_PASSWORD=<password>
PG_ADDRESS=<host>
PG_PORT=25060 # default DO port
PG_DATABASE=defaultdb # default DO database name
```

5. Replace each field with the credentials from DigitalOcean

1. Secure the file by running the following commands:

```bash
# make the `meltano` user sole owner
chown meltano:meltano /var/meltano/project/.env

# make the file only readable by `meltano`, and `write-only` for FTP access
chmod 620 /var/meltano/project/.env
```

7. Reload the environment variables into Meltano by restarting the service

```bash
systemctl restart meltano
```

8. Verify that the `meltano` service is working properly by checking:

```bash
systemctl status
```

### Step 6: Validate Meltano UI

#### Ensure everything works

1. Visit `$TENANT_NAME.meltanodata.com` in your browser
1. Login with credentials you setup in 1Password for the username `meltano`
1. Install `tap-carbon-intensity` extractor
1. Install `target-postgres` loader
   - You can also this by visiting `/pipeline/load/target-postgres`
1. When the configuration model for `target-postgres` appears, you should see the correct variables already configured from your `.env` file
1. Create a simple pipeline
1. Verify Analyze page is pulling in data and generating charts correctly

#### Remove tap-carbon-intensity

To ensure clients are greeted with a fresh install, it's important to remove any tests we ran.

1. SSH into droplet
1. Change directory to `/var/meltano/project`
1. Edit `meltano.yml` in text editor
   - Delete `extractors` section
   - Delete `models` section
   - Delete `transforms` section
   - Delete `schedule` section
1. Change directory into `/var/meltano/project/.meltano`
1. Delete the contents of the following folders:
   - `.../.meltano/extractors`
     - `tap-carbon-intensity`
   - `.../.meltano/models`
     - `model-carbon-intensity`
     - `model-carbon-intensity-sqlite`
   - `.../.meltano/run`
     - `tap-carbon-intensity`
     - `models/model-carbon-intensity`
     - `models/model-carbon-intensity-sqlite`
     - `models/topics.index.m5oc`

### Step 7: Verify FTP Works

1. Connect using an FTP client to the instance
1. Make sure that the FTP username and password are correct
1. Verify you can see the meltano project

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

### DNS Spoofing Error

If you get this error when you try to SSH into a droplet:

```
@       WARNING: POSSIBLE DNS SPOOFING DETECTED!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
The ECDSA host key for TENANT.meltanodata.com has changed,
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

https://{TENANT}.meltanodata.com/

You'll get a `Privacy Error: NET::ERR_CERT_AUTHORITY_INVALID`, but choose to `Proceed to $TENANT_NAME.meltanodata.com (unsafe)` (e.g. by first clicking on `Advanced` if you are using Chrome)

## Deleting an instance

When a client no longer needs a hosted instance of Meltano on meltanodata.com, you need to:

1. Login to DigitalOcean
1. Delete the client's droplet
1. Delete the client's A record in networking
1. Delete the client's database cluster
1. Delete the client's passwords in 1Password
