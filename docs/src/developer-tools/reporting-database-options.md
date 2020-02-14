---
sidebarDepth: 2
---

# Reporting Database Options

Users who chose to self-host Meltano need to create, configure and connect a **Loader** database to Meltano. Meltano Loaders _load data in bulk_ after it has been imported from source(s) using Extractors. Meltano currently supports loading data in the follow formats:

- [Comma Separated Values (CSV)](/plugins/loaders/csv.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgresQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)

::: tip
Hosted instances of Meltano come with a pre-configured PostgresQL database where Meltano loads extracted data so that it can be analyzed. If you are not sure how to set up your Loader, you can [sign up for a free hosted instance](https://meltano.typeform.com/to/NJPwxv) and we'll take care of that for you.
:::