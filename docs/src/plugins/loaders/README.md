---
metaTitle: Loading Data with Meltano
description: Use Meltano to load raw data from numerous sources into Postgres, Snowflake, and more. 
---

# Reporting Databases (Loaders)

**L**oading data is the **L** in the term **ELT**. After Meltano pulls data from your sources during the **E**xtract step, it uses Loader plugins (that are also known as [targets](/developer-tools/architecture.html#taps)) to load the data into a reporting database for further manipulation and analysis.

Meltano currently supports the following loader destinations:

- [Comma Separated Values (CSV)](/plugins/loaders/csv.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgreSQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)

Note that Meltano dashboards and reports are only supported when PostgreSQL is used.

::: tip
Hosted instances of Meltano come with a pre-configured PostgreSQL database where Meltano loads extracted data so that it can be analyzed. If you are not sure how to set up your Loader, you can [sign up for a free hosted instance](https://meltano.typeform.com/to/NJPwxv) and we'll take care of that for you.
:::
