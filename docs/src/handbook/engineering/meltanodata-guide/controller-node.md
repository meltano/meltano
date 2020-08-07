---
sidebarDepth: 2
---

# Controller Node

`*.meltanodata.com` can be managed using the controller node available at `controller.int.meltanodata.com`.

The purpose of this node is to provide tools to enable team members to leverage _infrastructure-as-code_.

## Prerequisites

1. Verify SSH Agent is populated locally

```shell
ssh-add -L
```

If you see `No registered agent found`, you'll need to add your key.

```shell
# Register your id_rsa key as an agent
ssh-add ~/.ssh/id_rsa

# Verify key exists
ssh-add -L
```

2. [DigitalOcean API Key](https://www.digitalocean.com/docs/api/create-personal-access-token/) for the "Meltano" and "MeltanoData DBs" DO accounts with Read and Write Access

### Tools

The Controller Node has Ansible installed and the `meltano/infrastructure` project automatically synced.

## Accessing the Controller Node

::: warning
Access to this node is restricted to Meltano Team members.
:::

To access the controller, connect using SSH with your Meltano username (`<first initial><last name>`).

```shell
ssh -A <username>@controller.int.meltanodata.com
```

::: warning
The Controller Node cannot connect on the production nodes for security reasons, you **must** forward your SSH key so that it is available during the SSH session.

SSH Key forwarding is a process in which the SSH client's agent will yield its currently loaded SSH keys to the server's agent, thus enabling it to act as if the keys where loaded on the server.

To enable SSH key forwarding, use the `-A` switch when connecting to the Controller Node.
:::

## Using Ansible

::: tip
You can always refer to the [ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_getting_started.html).
:::

Ansible is a configuration management and provisioning tool that enable infrastructure-as-code.

The `meltano/infrastructure` project is located at `/var/meltano/infrastructure`.

```shell
cd /var/meltano/infrastructure
```

### Ensure it works properly

```shell
$ ansible controller -m ping

# there might be some warnings, just ignore them for now.

controller | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Connecting to DigitalOcean

Now, we need to connect DigitalOcean to enable ansible to pull nodes metadata for us.

This will enable us to target:

- Specific nodes with the droplet's `name`
- Groups of nodes with `tags`
- All the nodes with `*.meltanodata.com`
- and more

To do that, you will need to export the DigitalOcean API Token for the "Meltano" project as `DO_API_TOKEN`:

```shell
export DO_API_TOKEN=<access_token>
```

Additionally, you will need to export the DigitalOcean API Token for the "MeltanoData DBs" projects as `DO_DATABASE_API_TOKENS`.

```shell
export DO_DATABASE_API_TOKENS=<access_token>,<access_token>,...
```

::: tip
To save yourself some time, you can also save this to your `.bashrc` file (`/home/<username>/.bashrc`) as long as the API key only has read access.
:::

You can test that it works using:

```shell
ansible all --list-hosts
# you should see a long list of IDs, these are the Droplet ID.
```

## Playbooks

Playbooks describe the desired state of a node.

To invoke a playbook, use:

```shell
ansible-playbook /path/to/playbook

# example, to run the `controller` playbook, use
sudo ansible-playbook playbooks/controller.yml
```

::: tip
To speed things up, it is recommended to add a flag of `--limit=$TENANT.meltanodata.com` when running playbooks for a specific droplet.
:::

### playbooks/ssl.yml

Ensure the Meltano certificate is present on the `*.meltanodata.com` nodes.

### playbooks/caddy.yml

Manage the Caddy configuration, namely:

  - `/etc/caddy/environment`
  - `/etc/caddy/Caddyfile`
  - `caddy` service

Configurable using the `caddy` variable.

### playbooks/controller.yml

Ensure the Controller access control is properly setup, requires `root` access.

### playbooks/meltano.yml

Manage the Meltano configuration, namely:

  - `/etc/meltano/environment`
  - `/var/meltano/project/ui.cfg`
  - `meltano` service

It also ensure each node has proper access control setup, so that ansible can connect to it.

### playbooks/meltano-upgrade.yml

Runs, on each node:

  - `meltano upgrade`
  - `meltano install --include-related` (can be skipped using `--skip-tags=plugins`)

### migrations/meltano-auth.yml

::: warning
This playbook was created as a one-off and should not be run unless you know what you are doing.
:::

Creates the default user account for the node.

To add a user, add it to the `playbooks/vars/meltano/admins.yml.vlt`

> `.vlt` files are encrypted using `ansible-vault`.
> See https://gitlab.com/meltano/infrastructure#how-to-add-sensitive-data for more information on how to setup your vault access.

Using the `ansible-vault edit playbooks/vars/meltano/admins.yml.vlt`, add the following entry for your host:

```yaml
$TENANT.meltanodata.com:
  username: <username>
  password: <password>
```

### migrations/meltano-dotenv-as-feature.yml

::: warning
This playbook was created as a one-off and should not be run unless you know what you are doing.
:::

Moves the `/var/meltano/project/.env` to the `/etc/meltano/environment.d/postgres` file, so that we can use the `.env` for the feature flags.
