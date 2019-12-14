---
sidebar: auto
---

# Controller Node

`*.meltanodata.com` can be managed using the controller node available at `controller.int.meltanodata.com`.

The purpose of this node is to provide tools to enable team members to leverage _infrastructure-as-code_.

## Prerequisites

1. Verify SSH Agent is populated locally

```bash
ssh-add -L
```

If you see `No registered agent found`, you'll need to add your key.

2. DigitalOcean API Key (Ready Access)

### Tools

The Controller Node has Ansible installed and the `meltano/infrastructure` project automatically synced.

## Accessing the Controller Node

::: warning
Access to this node is restricted to Meltano Team members.
:::

To access the controller, connect using SSH with your Meltano username.

```bash
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

### Ensure it works properly

```bash
$ cd /var/meltano/infrastructure
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

To do that, you will need to export your DigitalOcean API Token as `DO_API_TOKEN`.

```bash
export DO_API_TOKEN=<access_token>
```

::: tip
You can also save this to your `.bashrc` file as long as the API key only has read access to save yourself some time.
:::

You can test that it works using:

```bash
ansible all --list-hosts
# you should see a long list of IP addresses
```

## Playbooks

Playbooks describe the desired state of a node.

To invoke a playbook, use:

```bash
ansible-playbook /path/to/playbook

# example, to run the `controller` playbook, use
sudo ansible-playbook playbooks/controller.yml
```

::: tip
To speed things up, it is recommended to add a flag of `--limit=$TENANT.meltanodata.com` when running playbooks for a specific droplet.
:::

### caddy.yml

Copies over Caddyfile to the droplet.

### controller.yml

Ensure the Controller access control is properly setup, requires `root` access.

### meltano.yml

Ensure each node has proper access control setup.

### meltano-upgrade.yml

Runs `meltano upgrade` in each node.

### ssl.yml

Ensure the Meltano certificate is present on the `*.meltanodata.com` nodes.
