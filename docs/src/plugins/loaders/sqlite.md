---
sidebar: auto
metaTitle: Load Data into a SQLite database with Meltano
description: Use Meltano to load data from numerous sources and insert it into a SQLite database for easy analysis.
---

# SQLite Database

`target-sqlite` is a loader that works with other extractors in order to move data into a SQLite database.

## Info

- **Data Warehouse**: [SQLite](https://sqlite.org/)
- **Repository**: [https://gitlab.com/meltano/target-sqlite](https://gitlab.com/meltano/target-sqlite)

## Installing from the Meltano UI

From the Meltano UI, you can [select this Loader in Step 3 of your pipeline configuration](http://localhost:5000/pipelines/loaders).

### Configuration

Once the loader has installed, a modal will appear that'll allow you to configure your SQLite database connection.

## Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```shell
meltano add loader target-sqlite
```

If you are successful, you should see `Added and installed loaders 'target-sqlite'` in your terminal.

### CLI Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```shell
export SQLITE_DATABASE=""
```
