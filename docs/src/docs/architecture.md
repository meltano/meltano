# Architecture

## Meltano Schema

Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

### Create Schema and Roles

Create and grant usage for a database schema.

## Meltano Model

Meltano Models allow you to define your data model and interactively generate SQL so that you can easily analyze and visualize it in Meltano Analyze.

### Model Setup
There are two foundational steps required for Meltano to extract, load, and transform your data for analysis in Meltano Analyze:
1. Author `my-database-setup.model.m5o` file(s)
    - Define a database, connection settings, and the table relationships (further defined in each `my-table.table.m5o` file) to inform Meltano how to connect for ELT, orchestration, and interactive SQL generation using the Meltano Analyze GUI
1. Author `my-table.table.m5o` file(s)
    - Define a database table for connecting to using Meltano's CLI and/or Analyze GUI

### Model Authoring (`.m5o` files)
The `.m5o` file extension is unique to Meltano but adheres to the [HOCON (Human-Optimized Config Object Notation) format](https://github.com/lightbend/config/blob/master/HOCON.md#hocon-human-optimized-config-object-notation). Below are examples with comments to aid the authoring of your `...model.m5o` and `...table.m5o` files mentioned above.

#### Example `carbon.model.m5o` file

```
# Define a database, connection settings, and the table relationships (further defined in each `my-table.table.m5o` file) to inform Meltano how to connect for ELT, orchestration, and interactive SQL generation using the Meltano Analyze GUI
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

#### Example `entry.table.m5o` file

```
# Define a database table for connecting to using Meltano's CLI and/or Analyze GUI
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

With these files the Meltano CLI (or in conjunction with the Meltano Analyze GUI) can properly extract, load, and transform your data for analysis using Meltano Analyze.

## Meltano Analyze

Meltano Analyze is a dashboard that allows you to interactively generate and run SQL queries to produce data visualizations, charts, and graphs based on your data.

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

### Docker images

Meltano provides the following docker images:

> Notes: All images are available in the GitLab's registry: `registry.gitlab.com`

- `meltano/meltano`: Contains the API, CLI, and Meltano Analyze. This image should be deployed as Meltano Analyze.
- `meltano/meltano/runner`: Contains the CLI and extra runner specific binaries. This image should be used on the CI runner.
- `meltano/meltano/singer_runner`: **DEPRECATED: Use `meltano/meltano/runner` instead** Contains the CLI, and all curated taps/targets pre-installed.

> Notes: These images are base images used as the basis of other images.

- `meltano/meltano/cli`: Contains the meltano cli
- `meltano/meltano/base`: Contains the requirements for `meltano/meltano`
