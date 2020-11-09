---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into PostgreSQL
---

# PostgreSQL (`transferwise` variant)

The `target-postgres` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into a [PostgreSQL](https://www.postgresql.org/) database.

To learn more about `target-postgres`, refer to the repository at <https://github.com/transferwise/pipelinewise-target-postgres>.

#### Alternative variants

Multiple [variants](/docs/plugins.html#variants) of `target-postgres` are available.
This document describes the `transferwise` variant, which was originally built to be used with [PipelineWise](https://transferwise.github.io/pipelinewise/).

Alternative options are [`datamill-co`](./postgres.html) (default) and [`meltano`](./postgres--meltano.html).

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `transferwise` variant of the `target-postgres` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-postgres --variant transferwise
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the arrow next to the "Add to project" button for "PostgreSQL".
1. Choose "Add variant 'transferwise'".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`target-postgres` requires the [configuration](/docs/configuration.html) of the following settings:

- [Host](#host)
- [Port](#port)
- [User](#user)
- [Password](#password)
- [DBname](#dbname)
- [Default Target Schema](#default-target-schema)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-postgres` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-14}
plugins:
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
    config:
      host: postgres.example.com
      port: 5432
      user: my_user
      dbname: my_database
      # default_target_schema: my_schema   # override if default (see below) is not appropriate
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_POSTGRES_PASSWORD=my_password
```

### Host

- Name: `host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_HOST`, alias: `PG_ADDRESS`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set host <host>

export TARGET_POSTGRES_HOST=<host>
```

### Port

- Name: `port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PORT`, alias: `PG_PORT`
- Default: `5432`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set port 5502

export TARGET_POSTGRES_PORT=5502
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_USER`, alias: `PG_USERNAME`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set user <user>

export TARGET_POSTGRES_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PASSWORD`, alias: `PG_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set password <password>

export TARGET_POSTGRES_PASSWORD=<password>
```

### DBname

- Name: `dbname`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DBNAME`, alias: `PG_DATABASE`

PostgreSQL database name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set dbname <dbname>

export TARGET_POSTGRES_DBNAME=<dbname>
```

### SSL

- Name: `ssl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSL`
- Default: `false`

Using SSL via postgres `sslmode='require'` option.

If the server does not accept SSL connections or the client certificate is not recognized the connection will fail.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set ssl true

export TARGET_POSTGRES_SSL=true
```

### Default Target Schema

- Name: `default_target_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DEFAULT_TARGET_SCHEMA`, alias: `TARGET_POSTGRES_SCHEMA`, `PG_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html).

Name of the schema where the tables will be created. If `schema_mapping` is not defined then every stream sent by the tap is loaded into this schema.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set default_target_schema <schema>

export TARGET_POSTGRES_DEFAULT_TARGET_SCHEMA=<schema>
```

### Batch Size Rows

- Name: `batch_size_rows`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_BATCH_SIZE_ROWS`
- Default: `100000`

Maximum number of rows in each batch. At the end of each batch, the rows in the batch are loaded into Postgres.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set batch_size_rows 1000

export TARGET_POSTGRES_BATCH_SIZE_ROWS=1000
```

### Flush All Streams

- Name: `flush_all_streams`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_FLUSH_ALL_STREAMS`
- Default: `false`

Flush and load every stream into Postgres when one batch is full. Warning: This may trigger the COPY command to use files with low number of records.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set flush_all_streams true

export TARGET_POSTGRES_FLUSH_ALL_STREAMS=true
```

### Parallelism

- Name: `parallelism`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PARALLELISM`
- Default: `0`

The number of threads used to flush tables. 0 will create a thread for each stream, up to parallelism_max. -1 will create a thread for each CPU core. Any other positive number will create that number of threads, up to parallelism_max.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set parallelism -1

export TARGET_POSTGRES_PARALLELISM=-1
```

### Parallelism Max

- Name: `parallelism_max`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PARALLELISM_MAX`
- Default: `16`

Max number of parallel threads to use when flushing tables.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set parallelism_max 8

export TARGET_POSTGRES_PARALLELISM_MAX=8
```

### Schema Mapping

- Name: `schema_mapping`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SCHEMA_MAPPING`

Useful if you want to load multiple streams from one tap to multiple Postgres schemas.

If the tap sends the `stream_id` in `<schema_name>-<table_name>` format then this option overwrites the `default_target_schema` value.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set schema_mapping <mapping>

export TARGET_POSTGRES_SCHEMA_MAPPING=<mapping>
```

### Add Metadata Columns

- Name: `add_metadata_columns`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_ADD_METADATA_COLUMNS`
- Default: `false`

Metadata columns add extra row level information about data ingestions, (i.e. when was the row read in source, when was inserted or deleted in postgres etc.) Metadata columns are creating automatically by adding extra columns to the tables with a column prefix `_SDC_`. The column names are following the stitch naming conventions documented at <https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns>. Enabling metadata columns will flag the deleted rows by setting the `_SDC_DELETED_AT` metadata column. Without the `add_metadata_columns` option the deleted rows from singer taps will not be recongisable in Postgres.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set add_metadata_columns true

export TARGET_POSTGRES_ADD_METADATA_COLUMNS=true
```

### Hard Delete

- Name: `hard_delete`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_HARD_DELETE`
- Default: `false`

When `hard_delete` option is true then DELETE SQL commands will be performed in Postgres to delete rows in tables. It's achieved by continuously checking the `_SDC_DELETED_AT` metadata column sent by the singer tap. Due to deleting rows requires metadata columns, `hard_delete` option automatically enables the `add_metadata_columns` option as well.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set hard_delete true

export TARGET_POSTGRES_HARD_DELETE=true
```

### Data Flattening Max Level

- Name: `data_flattening_max_level`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DATA_FLATTENING_MAX_LEVEL`
- Default: `0`

Object type RECORD items from taps can be transformed to flattened columns by creating columns automatically. When value is 0 (default) then flattening functionality is turned off.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set data_flattening_max_level 2

export TARGET_POSTGRES_DATA_FLATTENING_MAX_LEVEL=2
```

### Primary Key Required

- Name: `primary_key_required`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PRIMARY_KEY_REQUIRED`
- Default: `true`

Log based and Incremental replications on tables with no Primary Key cause duplicates when merging UPDATE events. When set to true, stop loading data if no Primary Key is defined.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set primary_key_required false

export TARGET_POSTGRES_PRIMARY_KEY_REQUIRED=false
```

### Validate Records

- Name: `validate_records`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_VALIDATE_RECORDS`
- Default: `false`

Validate every single record message to the corresponding JSON schema. This option is disabled by default and invalid RECORD messages will fail only at load time by Postgres. Enabling this option will detect invalid records earlier but could cause performance degradation.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set validate_records true

export TARGET_POSTGRES_VALIDATE_RECORDS=true
```

### Temp Dir

- Name: `temp_dir`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_TEMP_DIR`
- Default: platform-dependent

Directory of temporary CSV files with RECORD messages.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set temp_dir /tmp/dir

export TARGET_POSTGRES_TEMP_DIR=/tmp/dir
```
