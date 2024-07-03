---
title: "Usage"
layout: doc
hidden: false
sidebar_position: 4
sidebar_class_name: hidden
---

:::info

<p><strong>Meltano Cloud has been shut down in favor of Arch.</strong></p>
<p>Read the announcement on <a href="https://meltano.com/blog/were-bringing-powerful-data-engineering-capabilities-to-software-teams-with-arch/">our blog</a>.</p>

:::

## Cloud Web Dashboard

Meltano Cloud is meant to be primarily used via the CLI, although there are some features that are also available in the web interface [https://app.meltano.cloud/](https://app.meltano.cloud/):

- Run history and status
- Logs
- Billing

## Managing Credits

Currently during Beta users need to talk to sales in order to purchase credits or view current usage.
Please contact Sales [https://meltano.com/talk-to-sales](https://meltano.com/talk-to-sales) or reach out in Slack.

For more details on credits and pricing see the [Pricing FAQ](https://meltano.com/pricing/).

## Backfills and State

Meltano Cloud will support state management operations similar to the Meltano Core [state](/reference/command-line-interface#state) command in GA.
While in Beta users have a few options for migrating existing state:

1. Let a full refresh run in Meltano Cloud.
   This is the easiest method but if the source has a high volume of data it could be slow and/or expensive.
   Once the job completes Meltano Cloud will maintain incremental bookmarks moving forward.
2. Configure a start date, if supported by the extractor, in your meltano.yml directly or in your Meltano Cloud environment variables by using the [`meltano-cloud` config](/cloud/cloud-cli#config) command with `<PLUGIN_NAME>_START_DATE=""`.
   See [the docs](/guide/configuration#configuring-settings) for more details on overriding settings using environment variables.
   Once the job completes you can remove the start date and allow the bookmarks to manage incremental syncs.
3. Contact the Meltano team to get your existing state migrated to Meltano Cloud.
