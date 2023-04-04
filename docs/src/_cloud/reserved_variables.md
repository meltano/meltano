---
title: "Reserved Variables"
description: Reserved variables for use in Meltano Cloud
layout: doc
weight: 4
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

# Reserved Variables

There are specific environment variables that are reserved for certain use-cases.

## SSH Private Keys for Private Git Repository Package Access

`GIT_SSH_PRIVATE_KEY` is a reserved variable that should be set if you have private repository packages.

> The following instruction and example is secrets encryption for Alpha which will be deprecated in Beta.
> Current encryption instructions can be found in our [Encrypting Secrets guide](https://github.com/meltano/cloud-docs/blob/main/docs/encrypting_secrets.md#components-for-encryption).

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
