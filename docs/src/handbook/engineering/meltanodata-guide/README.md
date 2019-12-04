---
sidebar: auto
---

# MeltanoData Guide

This will be the single source of truth for team members when it comes to creating and managing Meltano instances on MeltanoData.com.

## Creating a New Instance

### Prerequisites

- DigitalOcean Account
- Access to DigitalOcean Meltano team
- Client's tenant name (i.e., company name, etc.)

### Step 1: Setup a new droplet

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

This will automatically trigger a process that will initiate a workflow with Let's Encrypt to issue a HTTPS certificate for the subdomain.

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
1. Click on `Create a Database Cluster`

#### Configure the database

1. Click `Getting Started` button
1. Restrict inbound connections by adding the recently created droplet under **Add trusted sources**
1. Click `Allow these inbound sources only` button

You should now be greeted by the `Connection details` tab which is important for later on. It contains your database credentials and will be referenced later on.

### Step 4: Configure Meltano Droplet

1. SSH into your newly created droplet

```bash
ssh $TENANT_NAME.meltanodata.com
```

#### Configure Caddyfile

1. Open `/etc/caddy/Caddyfile` in text editor (i.e., vim)

```bash
vim /etc/caddy/Caddyfile
```

::: tip
Navigate vim with arrow keys and press `I` key to enter Insert mode so you can modify the text
:::

2. Comment out `tls self_signed` by prepending it with a `#`

```
# tls self_signed
```

3. Uncomment `tls admin@meltano.com` by removing the `#` at the beginning of the line

4. Save and exit file

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
htpasswd -b /etc/caddy/htpasswd meltano $PASSWORD
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

And you should see a state of `running` in the return message.

### Step 5: Configure Meltano UI

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

#### Install PostgreSQL loader on Meltano UI

1. Visit `$TENANT_NAME.meltanodata.com` in your browser
1. Login with credentials you setup in 1Password for the username `meltano`
1. Install `tap-carbon-intensity` since you cannot configure loaders without installing an extractor first
1. Install `target-postgres` for the loader

When you see the configuration modal, you are ready for the next step.

#### Configure PostgreSQL loader in meltano.yml

1. SSH into droplet
1. Change into the Meltano project directory

```bash
cd /var/meltano/project
```

3. Open `meltano.yml` in a text editor

```bash
vim meltano.yml
```

4. Update `meltano.yml` loaders to configure the `config` > `host` property:

```yaml
- label: PostgreSQL
  name: target-postgres
  pip_url: git+https://github.com/meltano/target-postgres.git
  config:
    host: db-postgresql-nyc3-000-wwright-do-user-000-0.db.ondigitalocean.com
```

5. Save and quit text editor

You should now see your changes appear in for the `host` input for Meltano UI in the PostgreSQL loader configuration modal.

#### Finalize configurations

1. Using the credentials from the DigitalOcean Database instance to fill out:

- User
- Password
- Port
- Database

1. Click `Save` to save your changes.

### Step 6: Make sure everything works!

Now all your have to do is check to make sure we can see reports being generated in Analyze and we're good to go! 🎉

## Maintaining an Existing Instance

### Upgrade a Meltano instance manually

In the event you need to manually update the droplet's Meltano version:

1. SSH into the droplet
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
1. Activate the virtual environment

```bash
source /var/meltano/.venv/bin/activate
```

3. Check system status and processes with

```bash
systemctl status
```

- Under `meltano.service`, you will see a directory path that will provide you with a hint towards where things live

4. To check the logs, go to `/var/meltano/project/.meltano/run`

5. The log used to debug this last time was `meltano-ui.log`

### 500 error when FTPing into instance

::: warning Error
Response: 500 OOPS: vsftpd: refusing to run with writable root inside chroot()
:::

This means that the permissions on the root directory you are trying to access need to be changed. This should not be an issue on future images, but in case it is, you'll need a command similar to:

```bash
chmod g-w /var/meltano/project
```
