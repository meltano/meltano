---
title: "Platform Information"
layout: doc
weight: 5
redirect_from:
  - /cloud/reserved_variables
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Cloud Platform

Meltano Cloud currently runs on AWS.

### Python Version

Meltano Cloud uses Python 3.9.
After our GA launch, we aim to support all active versions of Python that are not yet at their [end of life](https://devguide.python.org/versions/).

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

`GIT_SSH_PRIVATE_KEY` is a reserved variable that should be set if you have private repository packages.

To encrypt, set the ssh private key env variable into your `.env` file as-is in the private key file with single quotes
around them.

Example `.env` file to be encrypted:

```
GIT_SSH_PRIVATE_KEY='-----BEGIN OPENSSH PRIVATE KEY-----
therearelotsofprivatekeymaterialhere
onvariouslineslikethis
wecanjustcopypasteasitappearsinthefile
andusesinglequotesaroundthewholething
-----END OPENSSH PRIVATE KEY-----'
SOME_OTHER_SECRET=1234asdf
```

Then continue with encryption using the [kms-ext](https://github.com/meltano/kms-ext) utility.

## Job or Schedule Run Notifications via Webhook

`MELTANO_CLOUD_WEBHOOK_URL` can be set to receive notifications on success or fail of a job or schedule run.

Currently only one webhook URL can be configured.
