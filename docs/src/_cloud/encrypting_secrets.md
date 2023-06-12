---
title: "Encrypting Secrets"
description: Details the process for encrypting Meltano Cloud secrets
layout: doc
weight: 8
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

This document covers information on encrypting secrets in your Meltano `secrets.yml` file.

## Components for Encryption

### Encryption Method

Use the `meltano-cloud config env set --key <SECRET_NAME> --value <SECRET_VALUE>` CLI command to set configuration secrets.

Note: The value can be passed in directly or via an environment variable.
If you have an environment variable set locally called `TEST_SECRET`, the example to set it would be `meltano-cloud config env set --key TEST_SECRET --value $TEST_SECRET`.

This will set secrets via the `.env` file at runtime for a job or schedule.

You can list and delete secrets configured as well.

```
meltano-cloud config env list
meltano-cloud config env delete <SECRET_NAME>
```

Secrets cannot be decrypted after they are set. If you need to change a secret, you can set the secret again.

### Reserved Variables

See the [reserved variables](/platform/#reserved-variables) docs for more details on variables that are reserved for use by Meltano Cloud.
