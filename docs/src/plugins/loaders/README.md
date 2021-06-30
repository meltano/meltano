---
description: Use Meltano to easily load extracted data into arbitrary data destinations (databases, SaaS APIs, and file formats) using Singer targets.
---

::: warning
This page is now deprecated and will be removed in the future.

View the current documentation on the [MeltanoHub](https://hub.meltano.com/loaders/)
:::

# Destinations (Loaders)

Meltano lets you easily load [extracted](https://hub.meltano.com/extractors/) data into arbitrary data destinations (databases, SaaS APIs, and file formats) using [Singer targets](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [loader plugins](/docs/plugins.html#loaders).

Loaders for the following destinations are currently [discoverable](/docs/plugins.html#discoverable-plugins) and supported out of the box:

- [BigQuery](https://hub.meltano.com/loaders/bigquery.html)
- [Comma Separated Values (CSV)](https://hub.meltano.com/loaders/csv.html)
- [JSON Lines (JSONL)](https://hub.meltano.com/loaders/jsonl.html)
- [PostgreSQL](https://hub.meltano.com/loaders/postgres.html)
- [Redshift](https://hub.meltano.com/loaders/redshift.html)
- [Snowflake](https://hub.meltano.com/loaders/snowflake.html)
- [SQLite](https://hub.meltano.com/loaders/sqlite.html)

To learn more about [extracting](https://hub.meltano.com/loaders/) and loading data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

::: tip Don't see your data destination listed here?

If a [Singer target](https://www.singer.io/#targets) for your destination already exists,
it can easily be [added to your project as a custom loader](/docs/plugin-management.html#custom-plugins).
If not, you can learn how to [create your own from scratch](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

Once you've got the new loader working in your project, please consider
[contributing its description](/docs/contributor-guide.html#discoverable-plugins)
to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
so that it can be added to this page!

:::
