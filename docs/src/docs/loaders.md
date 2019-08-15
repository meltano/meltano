---
sidebarDepth: 1
---


# Loaders

**L**oading data is the **L** in the term **ELT**. In this section, we provide a detailed overview of how Meltano takes the data that was pulled from your sources during **E**xtract step, and puts it into a reporting database (Load) for further manipulation and analysis.

Meltano Loaders *load data in bulk* after it has been imported from source(s) using Extractors. Meltano currently supports loading data in the follow formats:
- [Comma Separated Values (CSV)](#csv)
- [PostgresQL Database](#postgres)
- [Snowflake Data Warehouse](#snowflake)
- [SQLite](#sqlite)

## Comma Separated Values (CSV)

Comma Separated Values, better known as spreadsheets, are the swiss army knife of data analysis. Loading data into this format will create .CSV files that can be used with many other tools that are able to import/export this file type.

### Info

- **Data Warehouse**: CSV Files
- **Repository**: [https://gitlab.com/meltano/target-csv](https://gitlab.com/meltano/target-csv)

### Installing from the Meltano UI

From the Meltano UI, you can (select this Loader in Step 3 of your pipeline configuration)[http://localhost:5000/pipelines/loaders].

#### Configuration

Once the loader has installed, a modal will appear with options for selecting the Delimiter and Quotechar you would like Meltano to use when loads your data into CSV format. The most commonly used options are selected by default.

### Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add loader target-csv
```

If you are successful, you should see `Added and installed loaders 'target-csv'` in your terminal.

#### CLI Configuration

If you want to customize your delimited or quote character, open `meltano.yml` for your desired project and update the configuration there.

```yaml{1-3}
  - config:
      delimiter": "\t"
      quotechar": ''''
    name: target-csv
    pip_url: git+https://gitlab.com/meltano/target-csv.git
```

## Snowflake Data Warehouse

`target-snowflake` is a loader that works with other extractors in order to move data into a Snowflake database.

::: warning
Please note that querying in the Meltano UI is not supported, yet.
You can follow the progress on this feature in this issue: [meltano/meltano#428](https://gitlab.com/meltano/meltano/issues/428)
:::

### Info

- **Data Warehouse**: [Snowflake](https://www.snowflake.com/)
- **Repository**: [https://gitlab.com/meltano/target-snowflake](https://gitlab.com/meltano/target-snowflake)

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export SF_ACCOUNT=""
export SF_USER=""
export SF_PASSWORD=""
export SF_ROLE=""       # in UPPERCASE
export SF_DATABASE=""   # in UPPERCASE
export SF_WAREHOUSE=""  # in UPPERCASE
```

- **SF_ACCOUNT** - This is the account name which is derived from the URL. More info can be found on the [Snowflake docs](https://docs.snowflake.net/manuals/user-guide/connecting.html#your-snowflake-account-name-and-url)
- **SF_USER** - This is the username for the user that will be used for loading data
- **SF_PASSWORD** - This is the password for the user that will be used for loading data
- **SF_ROLE** - This is the role you want to use for your account for loading the data
- **SF_DATABASE** - The name of the Snowflake database you want to use
- **SF_WAREHOUSE** - The name of the Snowflake warehouse you want to use

## PostgreSQL Database

`target-postgres` is a loader that moves data into a PostgreSQL (same as Postgres) database. In order to use this target, you will need a Postgres database where Meltano can load data.

### Tutorials

#### Beginner: Using a PostgreSQL Database for the First Time

In this section, we provide a tutorial for installing Postgres and setting up a new Postgres database.

##### Install PostgreSQL locally
1. Launch your terminal
1. Follow the [installation instructions from PostgreSQL.org](https://www.postgresql.org/download/macosx/)

##### Create Your Database
1. [Start your PostgreSQL server](https://tableplus.io/blog/2018/10/how-to-start-stop-restart-postgresql-server.html)
1. Create your first database by running `createdb <DATABASE_NAME>`
1. Connect to your postgres with the command: `psql <DATABASE_NAME>`

##### Create Your User
1. Run `createuser -s postgres` - this fixes the error: role "postgres" does not exist
1. Run `ALTER USER postgres WITH PASSWORD 'password';` with the new password of your choice
1. Run `\du` to get a list of users (from within psql)

##### Install pgAdmin
1. Go to the pgAdmin website and download the GUI https://www.pgadmin.org/
1. Install the .dmg packge that is appropriate for your operating system
1. Run the pgAdmin application and follow the prompt to create a master password
1. Back on the command line, log into your postgres user with `psql -U postgres` (by default, Postgres will log you into your username account on your machine so you will need to switch to the new user we created in the steps above)
1. Navigate to pgAdmin in your browser (it will launch a new tab when the server starts at a URL similar to http://127.0.0.1:52991/browser/#


#### Intermediate: Connecting Meltano to an Existing PostgreSQL Database

Once you have identified a PostgreSQL database where Meltano should load the data it extracts from your source(s), go to Meltano UI and complete Step 3 of the pipeline creation process. 

![Meltano UI pipeline select PostgreSQL loader](/screenshots/meltano-ui-load-postgres.png)


#### Advanced: Command Line (CLI) Configuration

In this section we provide additional information for configuring Meltano to connect with your PostgreSQL databae from the Meltano command line interface (CLI).

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export PG_ADDRESS=""
export PG_USERNAME=""
export PG_PORT=""
export PG_PASSWORD=""
export PG_DATABASE=""
export PG_SCHEMA=""
```

### Contributor Info

- **Data Warehouse**: [Postgres](https://www.postgresql.org/)
- **Repository**: [https://github.com/meltano/target-postgres](https://github.com/meltano/target-postgres)

## SQLite Database

`target-sqlite` is a loader that works with other extractors in order to move data into a SQLite database.

### Info

- **Data Warehouse**: [SQLite](https://sqlite.org/)
- **Repository**: [https://gitlab.com/meltano/target-sqlite](https://gitlab.com/meltano/target-sqlite)

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export SQLITE_DATABASE=""
```