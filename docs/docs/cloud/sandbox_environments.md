---
title: "Sandbox"
layout: doc
sidebar_class_name: hidden
---

:::info

<p><strong>Meltano Cloud is currently in Beta.</strong></p>
<p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>

:::

## Creating a Sandbox Environment for Meltano Cloud

We recommend creating a new Meltano environment named `sandbox`. You can create a new environment definition using the following CLI command:

```console
meltano environment add sandbox
```

If your data pipelines write data to a data warehouse or other production resource, the `sandbox` environment should be configured to not conflict with or overlap with any of your production data targets.

For example, if your production data pipelines output data to `RAW_DB`, you may want to create a new database called `STAGING_RAW_DB` or `RAW_DB_STAGING` which can be the target for the Meltano Cloud workloads during testing.

Note:

- In the Beta phase, branch and environment names will be fully configurable without contacting Meltano Support.
