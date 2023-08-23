---
title: "Platform Information"
layout: doc
sidebar_position: 5
redirect_from:
  - /cloud/reserved_variables
---

:::info

<p><strong>Meltano Cloud is currently in Beta.</strong></p>
<p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>

:::

## Cloud Platform

Meltano Cloud currently runs on AWS.

### Python Version

Meltano Cloud uses Python 3.9.
After our GA launch, we aim to support all active versions of Python that are not yet at their [end of life](https://devguide.python.org/versions/).

### Run Storage

Meltano Cloud enables up to 10GB of ephemeral disk storage during a run.

Future plans include making this configurable.

## Region

The primary AWS region hosting Meltano Cloud is `us-west-2` (Oregon, US).

Future plans include expanding into an EU region (timing is TBD).

## IP Addresses

We use the following IP addresses for all egress traffic.
Add the following IPs to your allow list if your Meltano Cloud workload requires access to your protected servers.

```
54.68.17.185/32
44.231.17.56/32
44.225.129.236/32
```

## Reserved Variables

There are specific environment variables that are reserved for certain use-cases.

### SSH Private Keys for Private Git Repository Package Access

`GIT_SSH_PRIVATE_KEY` is a reserved variable that should be set if you have private git repositories that are accessed during `meltano install` and can be accessed via SSH.

To specify it, set the ssh private key environment variable using `meltano cloud config env set`, which will look similar to this:

```sh
meltano cloud config env set --key GIT_SSH_PRIVATE_KEY --value '-----BEGIN OPENSSH PRIVATE KEY-----
therearelotsofprivatekeymaterialhere
onvariouslineslikethis
wecanjustcopypasteasitappearsinthefile
andusesinglequotesaroundthewholething
-----END OPENSSH PRIVATE KEY-----'
```

Note the quotes around the key value, which permits multi-line input.

Prior to setting your key via the CLI you can also validate that its formatted properly using the following command:

```console
foo@bar:~$ ssh-keygen -y -f <your_key_file>
ssh-ed25519 AAAAB3NzaC1yc2EAAAADAQABAAABAQCwK+DnOJItBOvbGbeqr0ts00aJGdN8vqD0ppq4 your_email@example.com
foo@bar:~$ ssh-keygen -y -f <your_key_file>
Load key "id_ed25519": invalid format
```
