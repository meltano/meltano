# Architecture

## Concepts

Below are common terms used within the Meltano ecosystem arranged alphabetically.

### Aggregate

An `Aggregate` relates to a calculable column, via `count`, `sum` or other (i.e., aggregate definitions). These are limited to predefined methods with no custom SQL as well since custom SQL will be handled through transforms with dbt.

### Collection

A `Collection` is a group of one or many `Designs` that determines how they will be mapped together.

A `Collection` can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

### Column

A `Column` relates directly to a column in a table of a database. Some limitations of this are that it will be limited to column only and no custom SQL.

### Dashboard

A `Dashboard` is a group of many `Reports`.

A `Dashboard` is identified by the file naming schema: `set-name.dashboard.m5o` and should be stored in the `/dashboards` directory.

### Design

A `Design` maps multiple tables together via joins. It points to many tables by names and can also add filters. At a high level, it does the following:

1. Takes selected columns to generate SQL from the `.m5oc` file
1. Runs the SQL query
1. Outputs the desired graph

In addition, a `Design` is the file that you would use to do the actual analysis because it defines the relationship between the tables.

A `Design` can be identified by the file naming schema: `design-name.design.m5o` and should be stored in the `/collections` directory.

### M5O Files

There are two types of `.m5o` files:

1. `.m5o` are user defined files that model the data in your database
2. `.m5oc` are compiled files generated from multiple `m5o` files

The `.m5o` files are based on the JSON-like HOCON syntax and serve as input for the compiled `.m5oc` files that Meltano UI then leverages.

### Report

A `Report` is a saved state of selecting and analyzing a `Design`. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

A `Report` can be identified by the file naming schema: `report-name.report.m5o` and should be stored in the `/reports` directory.

### Table

A `Table` relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains `columns` and `aggregates` so you can select which you want to show.

A `Table` can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

### Taps

A `Tap` is an application that pulls data out of a data source by using the best integration for extracting bulk data.

For example, it takes data from sources like databases or web service APIs and converts them in a format that can be used for data integration or an ETL (Extract Transform Load) pipeline. 

Meltano's `taps` is part of the Extractor portion of the data workflow and are based on the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

### Targets

A `Target` is an application that has the responsibility of consuming data from `taps` and perform a task with it. Examples include loading it into a file (i.e., CSV), API, or database. 

Meltano `targets` is part of the Loader portion of the data workflow.

## Meltano Schema

Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

### Create Schema and Roles

Create and grant usage for a database schema.

## Meltano Model

Meltano Models allow you to define your data model and interactively generate SQL so that you can easily analyze and visualize it in Meltano UI.

### Discover Available Models

To see what models are currently available in the Meltano ecosystem, run the following command:

```
meltano discover models
```

### Add a Model

To add an existing model to your Meltano project, run the following command:

```
meltano add model [name_of_model]
```

### Create a New Model

#### Model Setup
There are two foundational steps required for Meltano to extract, load, and transform your data for analysis in Meltano UI:
1. Author `my-database-setup.model.m5o` file(s)
    - Define a database, connection settings, and the table relationships (further defined in each `my-table.table.m5o` file) to inform Meltano how to connect for ELT, orchestration, and interactive SQL generation using the Meltano UI
1. Author `my-table.table.m5o` file(s)
    - Define a database table for connecting to using Meltano's CLI and/or UI

#### Model Authoring (`.m5o` files)
The `.m5o` file extension is unique to Meltano but adheres to the [HOCON (Human-Optimized Config Object Notation) format](https://github.com/lightbend/config/blob/master/HOCON.md#hocon-human-optimized-config-object-notation). Below are examples with comments to aid the authoring of your `...model.m5o` and `...table.m5o` files mentioned above.

##### Example `carbon.model.m5o` file

```
# Define a database, connection settings, and the table relationships (further defined in each `my-table.table.m5o` file) to inform Meltano how to connect for ELT, orchestration, and interactive SQL generation using the Meltano UI
{
  # Define version metadata
  version = 1
  # Define the name of the database used to denote automatically generated .m5oc for use by Meltano
  name = carbon
  # Define the database connection
  connection = runners_db
  # Define GUI label
  label = carbon intensity
  # Define base tables and their respective join relationships
  designs {
    # Define the base table(s) of interest (further defined in each my-table.table.m5o file) that will be GUI joinable and subsequently used for generating SQL queries
    region {
      # Define GUI label
      label = Region
      # Define from table name
      from = region
      # Define GUI description
      description = Region Carbon Intensity Data
      # Define joinable table(s) of this base table
      joins {
        # Define name of join table
        entry {
          # Define GUI label
          label = Entry
          # Define table columns of interest that will be GUI selectable and subsequently used for generating SQL queries
          fields = [entry.from, entry.to]
          # Define the SQL join condition
          sql_on = "{{ region.id }} = {{ entry.region_id }}"
          # Define join relationship
          relationship = one_to_one
        }
      }
    }
  }
}
```

##### Example `entry.table.m5o` file

```
# Define a database table for connecting to using Meltano's CLI and/or UI
{
  # Define the schema.table-name pattern used for connecting to a specific table in a database
  sql_table_name = gitlab.entry
  # Define the table name
  name = entry
  # Define the column(s) of interest that will be GUI selectable and subsequently used for generating SQL queries
  columns {
    # Define column name
    id {
      # Define GUI label
      label = ID
      # Define the primary key (only one per colums definition)
      primary_key = yes
      # Define GUI visibility
      hidden = yes
      # Define data type so ELT process properly updates the data warehouse
      type = string
      # Define the SQL that selects this column
      sql = "{{table}}.id"
    }
  }
  # Define time-based column(s) of interest that will be GUI selectable and subsequently used for generating SQL queries
  column_groups {
    from {
      label = From
      description = Selected from range in carbon data
      type = time
      timeframes = [{ label = Date }, { label = Week }, { label = Month }, { label = Year }]
      convert_tz = no
      sql = "{{TABLE}}.from"
    }
    to {
      label = To
      description = Selected to range in carbon data
      type = time
      timeframes = [{ label = Date }, { label = Week }, { label = Month }, { label = Year }]
      convert_tz = no
      sql = "{{TABLE}}.to"
    }
  }
}
```

With these files the Meltano CLI (or in conjunction with the Meltano UI) can properly extract, load, and transform your data for analysis using Meltano UI.

## Meltano UI

Meltano UI is a dashboard that allows you to interactively generate and run SQL queries to produce data visualizations, charts, and graphs based on your data.

## Meltano ELT

Meltano uses Singer Taps and Targets to Extract the data from various data sources and load them in raw format, i.e. as close as possible to their original format, to the Data Warehouse. Subsequently, the raw data is transformed to generate the dataset used for analysis and dashboard generation.

Meltano can be used in any ELT architecture by using the right taps and targets for the job. The strategies supported can range from dumping the source data in a data lake to keeping all historical versions for each record to storing well formatted, clean data in the target data store.

When considering which taps and targets Meltano will maintain, some assumptions are followed concerning how source data is stored in the target data store:
*  All extracted data is stored in the same Target Database, e.g., we use a Database named `RAW` for storing all extracted data to Snowflake.

*  For each tap's data source, a schema is created for storing all the data that is extracted through a tap. E.g., The `RAW.SALESFORCE` schema is used for data extracted from Salesforce, and the `RAW.ZENDESK` schema is used for data extracted from Zendesk.

*  Every stream generated from a tap will result in a table with the same name. That table will be created in the schema from that tap based on the information sent in the `SCHEMA` message.

*  Meltano supports schema updates for when a schema of an entity changes during an extraction. This is enacted when Meltano receives more than one `SCHEMA` message for a specific stream in the same extract load run.

    When a SCHEMA message for a stream is received, our Targets check whether there is already a table for the entity defined by the stream.
    * If the schema for the tap does not exist, it is created.
    * If the table for the stream does not exist, it is created.
    * If a table does exist, our Targets create a diff to check if new attributes must be added to the table or already defined attributes should have their data type updated. Based on that diff, the Targets make the appropriate schema changes.

    Rules followed:
    1. Only support type upgrades (e.g., STRING -> VARCHAR) for existing columns.
    2. If an unsupported type update is requested (e.g., float --> int), then an exception is raised.
    3. Columns are never dropped. Only UPDATE existing columns or ADD new columns.

*  Data is upserted when an entity has at least one primary key (key_properties not empty). If there is already a row with the same composite key (combination of key_properties) then the new record updates the existing one.

    No key_properties must be defined for a target to work on append-only mode. In that case, the target tables will store historical information with entries for the same key differentiated by their `__loaded_at` timestamp.

*  If a timestamp_column attribute is not defined in the SCHEMA sent to the target for a specific stream, it is added explicitly. Each RECORD has the timestamp of when the target receives it as a value. As an example, `target-snowflake` sets the name of that attribute to `__loaded_at` when an explicit name is not provided in the target's configuration file.

    When a target is set to work on append-only mode (i.e. no primary keys defined for the streams), the timestamp_column's value can be used to get the most recent information for each record.

*  For targets loading data to Relational Data Stores (e.g., Postgres, Snowflake, etc.), we unnest nested JSON data structures and follow a `[object_name]__[property_name]` approach similar to [what Stitch platform also does](https://www.stitchdata.com/docs/data-structure/nested-data-structures-row-count-impact).

*  At the moment we do not deconstruct nested arrays. Arrays are stored as JSON or STRING data types (depending on the support provided by the target Data Store) with the relevant JSON representation stored as is. e.g. "['banana','apple']". It can then be extracted and used in the Transform Step.

### Concurrency

The Singer spec doesn't define how to handle concurrency at the ELT level.

Making the streams concurrent themselves is pretty straightforward, but making sure the state handles concurrent updates is the real challenge, and also source specific.
Some sources supports pagination endpoints or a cursor-like API, but not all APIs are made equal.

Also depending on the data source, you might have some limit on how concurrent you can be, for example Salesforce limits to 25 concurrent request, but Netsuite allows only one query at a time per account.

For now, Meltano will try to implement concurrent taps when possible.

### Job logging

Every time `meltano elt ...` runs, Meltano will keep track of the job and its success state in a log.

This log is stored the Meltano system database.

> Note: Out of the box, Meltano uses a SQLite database named `meltano.db` as its system database.
> However this is customizable using the `MELTANO_BACKEND=sqlite|postgresql` environment variable, or
> using the (-B|--backend) switch at invocation.


## Meltano Transform

### dbt

Meltano uses [dbt](https://docs.getdbt.com/) to transform the source data into the `analytics` schema, ready to be consumed by models.

[Fishtown wrote a good article about what to model dynamically and what to do in dbt transformations](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304).

#### Python scripts

In certain circumstances transformations cannot be done in dbt (like API calls), so we use python scripts for these cases.

### Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.

#### Loading a CSV:

> Notes:
>
> - The naming format for the `FILES` must be `<schema>.<table>.csv`. This pattern is required and will be used to create/update the table in the DW.
> - Multiple `FILES` can be used, use spaces to separate.

- Start the cloud sql proxy
- Run the command:

```
python3 elt/util/spreadsheet_loader.py csv FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Loading a Google Sheet:

> Notes:
>
> - Each `FILES` will be located and loaded based on its name. The names of the sheets shared with the runner must be unique and in the `<schema>.<table>` format
> - Multiple `FILES` can be used, use spaces to separate.

- Share the sheet with the required service account (if being used in automated CI, use the runner service account)
- Run the command:

```
python3 elt/util/spreadsheet_loader.py sheet FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Further Usage Help:

- Run the following command(s) for additional usage info `python3 elt/util/spreadsheet_loader.py <csv|sheet> -- --help`

### Access Control

Meltano manages authorization using a role based access control scheme.

  * Users have multiple roles;
  * Roles have multiple permissions;

A Permission has a context for with it is valid: anything that matches the context is permitted.

## Meltano UI in Production

Meltano UI consist of a Flask API and a Vue.js front-end application, which are both included in the `meltano` package. In other words, the Flask API is not exposed at a project level and any customizations needed must be done at the package level.

To run Meltano in production, we recommend using [gunicorn](http://docs.gunicorn.org/en/stable/install.html) for setting up your HTTP Server.

First, install gunicorn:

```bash
$ pip install gunicorn
```

You can then start Meltano UI:

::: warning Note
This is an example invocation of gunicorn, please refer to
the [gunicorn documentation](http://docs.gunicorn.org/en/stable/settings.html) for more details.
:::

```bash
# ALWAYS run Meltano UI in production mode when it is accessible externally
$ export FLASK_ENV=production
$ export MELTANO_AUTHENTICATION=true

# Start gunicorn with 4 workers, alternatively you can use `$(nproc)`
$ gunicorn -c python:meltano.api.wsgi.config -w 4 meltano.api.wsgi:app
```

