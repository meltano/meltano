---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into PostgreSQL
---

::: warning
This page is now deprecated and will be removed in the future.

View the current documentation on the [MeltanoHub](https://hub.meltano.com/loaders/postgres)
:::

# PostgreSQL

The `target-postgres` [loader](https://hub.meltano.com/loaders/) loads [extracted](https://hub.meltano.com/extractors/) data into a [PostgreSQL](https://www.postgresql.org/) database.

- **Repository**: <https://github.com/datamill-co/target-postgres>
- **Maintainer**: [Data Mill](https://datamill.co/)
- **Maintenance status**: Active

#### Alternative variants

Multiple [variants](/docs/plugins.html#variants) of `target-postgres` are available.
This document describes the default `datamill-co` variant, which is recommended for new users.

Alternative options are [`transferwise`](./postgres--transferwise.html) and [`meltano`](./postgres--meltano.html).

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

#### Dependencies

`target-postgres` [requires](https://www.psycopg.org/docs/install.html#runtime-requirements) the
[`libpq` library](https://www.postgresql.org/docs/current/libpq.html) to be available on your system.
If you've installed PostgreSQL, you should already have it, but you can also install it by itself using the
[`libpq-dev` package](https://pkgs.org/download/libpq-dev) on Ubuntu/Debian or the
[`libpq` Homebrew formula](https://formulae.brew.sh/formula/libpq) on macOS.

### Installation and configuration

#### Using the Command Line Interface

1. Add the `target-postgres` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-postgres
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the "Add to project" button for "PostgreSQL".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, refer to the ["Troubleshooting" section](#troubleshooting) below or [learn how to get help](/docs/getting-help.html).

## Settings

`target-postgres` requires the [configuration](/docs/configuration.html) of the following settings:

- [Postgres Host](#postgres-host)
- [Postgres Port](#postgres-port)
- [Postgres Database](#postgres-database)
- [Postgres Username](#postgres-username)
- [Postgres Password](#postgres-password)
- [Postgres Schema](#postgres-schema)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-postgres` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-10}
plugins:
  loaders:
  - name: target-postgres
    variant: datamill-co
    config:
      postgres_host: postgres.example.com
      postgres_port: 5432
      postgres_username: my_user
      postgres_database: my_database
      # postgres_schema: my_schema   # override if default (see below) is not appropriate
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_POSTGRES_PASSWORD=my_password
```

### Postgres Host

- Name: `postgres_host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_HOST`, alias: `TARGET_POSTGRES_POSTGRES_HOST`, `PG_ADDRESS`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_host <host>

export TARGET_POSTGRES_HOST=<host>
```

### Postgres Port

- Name: `postgres_port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PORT`, alias: `TARGET_POSTGRES_POSTGRES_PORT`, `PG_PORT`
- Default: `5432`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_port 5502

export TARGET_POSTGRES_PORT=5502
```

### Postgres Database

- Name: `postgres_database`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DATABASE`, alias: `TARGET_POSTGRES_POSTGRES_DATABASE`, `PG_DATABASE`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_database <database>

export TARGET_POSTGRES_DATABASE=<database>
```

### Postgres Username

- Name: `postgres_username`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_USERNAME`, alias: `TARGET_POSTGRES_POSTGRES_USERNAME`, `PG_USERNAME`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_username <username>

export TARGET_POSTGRES_USERNAME=<username>
```

### Postgres Password

- Name: `postgres_password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PASSWORD`, alias: `TARGET_POSTGRES_POSTGRES_PASSWORD`, `PG_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_password <password>

export TARGET_POSTGRES_PASSWORD=<password>
```

### Postgres Schema

- Name: `postgres_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SCHEMA`, alias: `TARGET_POSTGRES_POSTGRES_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](https://hub.meltano.com/extractors/gitlab.html).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_schema <schema>

export TARGET_POSTGRES_POSTGRES_SCHEMA=<schema>
```

### Postgres SSLmode

- Name: `postgres_sslmode`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSLMODE`, alias: `TARGET_POSTGRES_POSTGRES_SSLMODE`
- Default: `prefer`

Refer to the [libpq docs](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS) for more information about SSL.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_sslmode <mode>

export TARGET_POSTGRES_SSLMODE=<mode>
```

### Postgres SSLcert

- Name: `postgres_sslcert`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSLCERT`, alias: `TARGET_POSTGRES_POSTGRES_SSLCERT`
- Default: `~/.postgresql/postgresql.crt`

Only used if a SSL request w/ a client certificate is being made

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_sslcert <path>

export TARGET_POSTGRES_SSLCERT=<path>
```

### Postgres SSLkey

- Name: `postgres_sslkey`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSLKEY`, alias: `TARGET_POSTGRES_POSTGRES_SSLKEY`
- Default: `~/.postgresql/postgresql.key`

Only used if a SSL request w/ a client certificate is being made

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_sslkey <path>

export TARGET_POSTGRES_SSLKEY=<path>
```

### Postgres SSLrootcert

- Name: `postgres_sslrootcert`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSLROOTCERT`, alias: `TARGET_POSTGRES_POSTGRES_SSLROOTCERT`
- Default: `~/.postgresql/root.crt`

Used for authentication of a server SSL certificate

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_sslrootcert <path>

export TARGET_POSTGRES_SSLROOTCERT=<path>
```

### Postgres SSLcrl

- Name: `postgres_sslcrl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SSLCRL`, alias: `TARGET_POSTGRES_POSTGRES_SSLCRL`
- Default: `~/.postgresql/root.crl`

Used for authentication of a server SSL certificate

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set postgres_sslcrl <path>

export TARGET_POSTGRES_SSLCRL=<path>
```

### Invalid Records Detect

- Name: `invalid_records_detect`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_INVALID_RECORDS_DETECT`
- Default: `true`

Include `false` in your config to disable `target-postgres` from crashing on invalid records

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set invalid_records_detect false

export TARGET_POSTGRES_INVALID_RECORDS_DETECT=false
```

### Invalid Records Threshold

- Name: `invalid_records_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_INVALID_RECORDS_THRESHOLD`
- Default: `0`

Include a positive value `n` in your config to allow for `target-postgres` to encounter at most `n` invalid records per stream before giving up.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set invalid_records_threshold 5

export TARGET_POSTGRES_INVALID_RECORDS_THRESHOLD=5
```

### Disable Collection

- Name: `disable_collection`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DISABLE_COLLECTION`
- Default: `false`

Include `true` in your config to disable [Singer Usage Logging](https://github.com/datamill-co/target-postgres#usage-logging).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set disable_collection true

export TARGET_POSTGRES_DISABLE_COLLECTION=true
```

### Logging Level

- Name: `logging_level`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_LOGGING_LEVEL`
- Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Default: `INFO`

The level for logging. Set to `DEBUG` to get things like queries executed, timing of those queries, etc. See [Python's Logger Levels](https://docs.python.org/3/library/logging.html#levels) for information about valid values.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set logging_level DEBUG

export TARGET_POSTGRES_LOGGING_LEVEL=DEBUG
```

### Persist Empty Tables

- Name: `persist_empty_tables`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PERSIST_EMPTY_TABLES`
- Default: `false`

Whether the Target should create tables which have no records present in Remote.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set persist_empty_tables true

export TARGET_POSTGRES_PERSIST_EMPTY_TABLES=true
```

### Max Batch Rows

- Name: `max_batch_rows`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_MAX_BATCH_ROWS`
- Default: `200000`

The maximum number of rows to buffer in memory before writing to the destination table in Postgres

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set max_batch_rows 100000

export TARGET_POSTGRES_MAX_BATCH_ROWS=100000
```

### Max Buffer Size

- Name: `max_buffer_size`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_MAX_BUFFER_SIZE`
- Default: `104857600` (100MB in bytes)

The maximum number of bytes to buffer in memory before writing to the destination table in Postgres.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set max_buffer_size 52428800 # 50MB in bytes

export TARGET_POSTGRES_MAX_BUFFER_SIZE=52428800
```

### Batch Detection Threshold

- Name: `batch_detection_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_BATCH_DETECTION_THRESHOLD`
- Default: 1/40th of [Max Batch Rows](#max-batch-rows), usually `5000`

How often, in rows received, to count the buffered rows and bytes to check if a flush is necessary.

There's a slight performance penalty to checking the buffered records count or bytesize, so this controls how often this is polled in order to mitigate the penalty. This value is usually not necessary to set as the default is dynamically adjusted to check reasonably often.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set batch_detection_threshold 1000

export TARGET_POSTGRES_BATCH_DETECTION_THRESHOLD=100
```

### State Support

- Name: `state_support`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_STATE_SUPPORT`
- Default: `true`

Whether the Target should emit `STATE` messages to stdout for further consumption.

In this mode, which is on by default, STATE messages are buffered in memory until all the records that occurred before them are flushed according to the batch flushing schedule the target is configured with.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set state_support false

export TARGET_POSTGRES_STATE_SUPPORT=false
```

### Add Upsert Indexes

- Name: `add_upsert_indexes`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_ADD_UPSERT_INDEXES`
- Default: `true`

Whether the Target should create column indexes on the important columns used during data loading.

These indexes will make data loading slightly slower but the deduplication phase much faster. Defaults to on for better baseline performance.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set add_upsert_indexes false

export TARGET_POSTGRES_ADD_UPSERT_INDEXES=false
```

### Before Run SQL

- Name: `before_run_sql`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_BEFORE_RUN_SQL`

Raw SQL statement(s) to execute as soon as the connection to Postgres is opened by the target. Useful for setup like `SET ROLE` or other connection state that is important.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set before_run_sql <sql>

export TARGET_POSTGRES_BEFORE_RUN_SQL=<sql>
```

### After Run SQL

- Name: `after_run_sql`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_AFTER_RUN_SQL`

Raw SQL statement(s) to execute as soon as the connection to Postgres is opened by the target. Useful for setup like `SET ROLE` or other connection state that is important.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set after_run_sql <sql>

export TARGET_POSTGRES_AFTER_RUN_SQL=<sql>
```

## Troubleshooting

### Error: `psycopg2.ProgrammingError: syntax error at or near "-"`

This error message indicates that the extractor you are using this loader with generates
stream names that include the source database schema in addition to the table name: `<schema>-<table>`, e.g. `public-accounts`.
This is not supported by [this variant](#alternative-variants) of `target-postgres`.

Instead, use the [`transferwise` variant](https://hub.meltano.com/loaders/postgres--transferwise.html) which was made to be used with extractors that behave this way.

### Error: `pg_config executable not found` or `libpq-fe.h: No such file or directory`

This error message indicates that the [`libpq`](https://www.postgresql.org/docs/current/libpq.html) dependency is missing.

To resolve this, refer to the ["Dependencies" section](#dependencies) above.

### Error: `ld: library not found for -lssl` or `clang: error: linker command failed with exit code 1` or `error: command 'clang' failed with exit status 1`

This error message indicates that there is a problem installing OpenSSL. This 
[Stack Overflow answer](https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl) 
has specific recommendations on setting the `LDFLAGS` and/or `CPPFLAGS` environment variables. 
Set those prior to running `meltano add loader target-postgres`.
