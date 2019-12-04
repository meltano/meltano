---
sidebar: auto
---

# New Client Setup Guide

This is the guide for team members to use when setting up a new Meltano instance for clients.

## Prerequisites

- DigitalOcean Account
- Access to DigitalOcean Meltano team
- Client's tenant name (i.e., company name, etc.)

## Step 1: Setup a new droplet

1. Login to DigitalOcean
1. Access the Meltano project workspace
1. In the upper right, click on the `Create` button
1. Select `Droplets` from the dropdown menu

### Choose an image

1. Select the `Snapshots` tab
1. Select the first image in the upper left corner (e.g., `Ubuntu meltano-123456789`)

### Choose a plan

1. Leave it on `Standard`
1. Change machine plan cost to:
   - \$15 / month
   - 2 GB / 2 CPUs
   - 60 GB SSD Disk
   - 3 TB transfer

### Add block storage

1. Leave empty

### Choose a datacenter region

1. You can leave the default (e.g., New York 3), but make note which it is since you'll need it later on

### Select additional options

1. Leave everything unselected

### Authentication

1. Select `SSH keys` if it is not selected by default
1. Click `Select all` to provide all team members ability to access the droplet

::: warning
If your SSH key is not included in the list above, make sure to add it now through the `New SSH Key` button.
:::

### Finalize and create

1. Leave droplet at `1 droplet`
1. For the hostname, use the desired URL for this client (i.e., `$TENANT_NAME.meltanodata.com`)
1. Under tags, add `production`

### Select Project

1. Leave the default as `Meltano`

### Add backups

1. Leave `Enable backups` unchecked

### Create droplet

1. Click on `Create droplet` to start the process.

Once the droplet has completed setting up, you should see it in your `Droplets` table with an assigned IP address.

### Verify droplet is working

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

## Step 2: Configure Network

1. Click on the `Networking` link on the left side menu
1. Under the **Domains** tab, click on `meltanodata.com` to access the DNS records dashboard

### Create a new record for the client

1. The current tab should be `A` records
1. Under **Hostname**, fill in your client's `$TENANT_NAME`
1. Under **Will Direct To**, use the autocomplete to locate the new droplet you created (or paste in the IP address from the Droplets table if it is not appearing)
1. Leave **TTL (seconds)** with the default of `3600`
1. Click `Create Record`

This will automatically trigger a process that will initiate a workflow with Let's Encrypt to issue a HTTPS certificate for the subdomain.

### Make sure everything works

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

## Step 3: Create Database Cluster

1. Select `Databases` link in the left side menu
1. In the upper right, click on `Create` button
1. Select `Databases` from the dropdown

### Choose a database engine

1. Leave default as `PostgreSQL 11`

### Choose a cluster configuration

1. Leave default on `$15/mo: 1 GB RAM / 1 vCPU / 10 GB Disk` plan

### Choose a datacenter

1. Choose the same geolocation as the droplet if possible

### Finalize and create

1. Under **Choose a unique database cluster name**, append the automatically generated name with `-$TENANT_NAME` (e.g., `db-postgresql-nyc3-52483-$TENANT_NAME`)
1. Under **Select project**, leave it as the default `Meltano`
1. Click on `Create a Database Cluster`

### Configure the database

1. Click `Getting Started` button
1. Restrict inbound connections by adding the recently created droplet under **Add trusted sources**
1. Click `Allow these inbound sources only` button

You should now be greeted by the `Connection details` tab which is important for later on. It contains your database credentials and will be referenced later on.

## Step 4: Configure Meltano Droplet

1. SSH into your newly created droplet

```bash
ssh $TENANT_NAME.meltanodata.com
```

### Configure Caddyfile

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

### Configure Caddy Environment

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

### Change Login Password

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

### Change FTP Login Password

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

### Restart Caddy

Now that the configurations are made, you need to restart Caddy by running the following command:

```bash
systemctl restart caddy
```

To verify this worked, you can run the following command:

```bash
systemctl status
```

And you should see a state of `running` in the return message.

## Step 5: Configure Meltano UI

1. Get database credentials from Digital Ocean
1. Install `Postgres` loader
1. Update `meltano.yml` with PostgreSQL host location through SSH
1. Make sure loader `Postgres` and has the correct host
