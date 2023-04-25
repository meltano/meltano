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

## Job or Schedule Run Notifications via Webhook

`MELTANO_CLOUD_WEBHOOK_URL` can be set to receive notifications on success or fail of a job or schedule run.

Currently only one webhook URL can be configured.
