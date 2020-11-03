---
description: Use Meltano to easily load extracted data into arbitrary data destinations (databases, SaaS APIs, and file formats) using Singer targets.
---

# Destinations (Loaders)

Meltano lets you easily load [extracted](/plugins/extractors/) data into arbitrary data destinations (databases, SaaS APIs, and file formats) using [Singer targets](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [loader plugins](/docs/plugins.html#loaders).

Loaders for the following destinations are currently [discoverable](/docs/plugins.html#discoverable-plugins) and supported out of the box:

- [BigQuery](/plugins/loaders/bigquery.html)
- [Comma Separated Values (CSV)](/plugins/loaders/csv.html)
- [JSON Lines (JSONL)](/plugins/loaders/jsonl.html)
- [PostgreSQL](/plugins/loaders/postgres.html)
- [SQLite](/plugins/loaders/sqlite.html)
- [Snowflake](/plugins/loaders/snowflake.html)

To learn more about [extracting](/plugins/loaders/) and loading data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

::: tip Don't see your data destination listed here?

If a [Singer target](https://www.singer.io/#targets) for your destination already exists,
it can easily be [added to your project as a custom loader](/docs/command-line-interface.html#how-to-use-custom-plugins).
If not, you can learn how to [create your own from scratch](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

Once you've got the new loader working in your project, please consider
[contributing its definition](/docs/contributor-guide.html#discoverable-plugins)
to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
so that it can be added to this page!

:::
