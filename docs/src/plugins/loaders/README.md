---
metaTitle: Loading Data with Meltano
description: Use Meltano to load raw data from numerous sources into Postgres, Snowflake, and more.
---

# Loaders: Data Destinations

**L**oading data is the **L** in the term **ELT**. After Meltano pulls data from your sources during the **E**xtract step, it uses Loader plugins (that are also known as [targets](/docs/architecture.html#targets)) to load the data into a reporting database for further manipulation and analysis.

Meltano currently supports the following loader destinations:

The following loaders are currently [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box on the [CLI](/docs/command-line-interface.html#add) and [UI](/docs/analysis.html#set-up-meltano):

- [Comma Separated Values (CSV) file](/plugins/loaders/csv.html)
- [JSON Lines (JSON) file](/plugins/loaders/jsonl.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgreSQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)

Note that Meltano dashboards and reports are only supported when PostgreSQL is used.

::: tip Don't see your reporting database here?
You can easily add [any existing Singer target](https://www.singer.io/#targets) as a [custom loader](/docs/command-line-interface.html#how-to-use-custom-plugins) or [create your own from scratch](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

Don't forget to make your new plugin [known to Meltano](/docs/contributor-guide.html#known-plugins) if you'd like to make it available to other people!
:::
