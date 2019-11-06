---
prev: /plugins/
metaTitle: Loading Data with Meltano
description: Use Meltano to load raw data from numerous sources into Postgres, Snowflake, and more. 
---

# Loaders

**L**oading data is the **L** in the term **ELT**. In this section, we provide a detailed overview of how Meltano takes the data that was pulled from your sources during **E**xtract step, and puts it into a reporting database (Load) for further manipulation and analysis.

Meltano Loaders _load data in bulk_ after it has been imported from source(s) using Extractors. Meltano currently supports loading data in the follow formats:

- [Comma Separated Values (CSV)](/plugins/loaders/csv.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgresQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)
