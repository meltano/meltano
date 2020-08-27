---
metaTitle: Loading Data with Meltano
description: Use Meltano to easily load extracted data into arbitrary data destinations (databases, SaaS APIs, and file formats) using Singer targets.
---

# Loaders: Data Destinations

Meltano lets you easily load [extracted](/plugins/extractors/) data into arbitrary data destinations (databases, SaaS APIs, and file formats) using [Singer targets](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [loader plugins](/docs/plugins.html#loaders).

To learn more about [extracting](/plugins/loaders/) and loading data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

Loaders for the following destinations are currently [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box:

- [Comma Separated Values (CSV) file](/plugins/loaders/csv.html)
- [JSON Lines (JSON) file](/plugins/loaders/jsonl.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgreSQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)

::: tip Don't see your data destination listed here?

If a [Singer target](https://www.singer.io/#targets) for your destination already exists,
it can easily be [added to your project as a custom loader](/docs/command-line-interface.html#how-to-use-custom-plugins).
If not, you can learn how to [create your own from scratch](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

Once you've successfully added a previously unknown loader to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!

:::
