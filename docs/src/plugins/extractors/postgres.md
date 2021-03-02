---
sidebar: auto
description: Use Meltano to pull data from a PostgreSQL database and load it into Snowflake, PostgreSQL, and more
---

# PostgreSQL

The `tap-postgres` [extractor](/plugins/extractors/) pulls data from a [PostgreSQL](https://www.postgresql.org/) database.

- **Repository**: <https://github.com/transferwise/pipelinewise-tap-postgres>
- **Documentation**: <https://transferwise.github.io/pipelinewise/connectors/taps/postgres.html>
- **Maintainer**: [TransferWise](https://transferwise.com/)
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

Then, follow the steps in the ["Setup requirements" section of the documentation](https://transferwise.github.io/pipelinewise/connectors/taps/postgres.html#postgresql-setup-requirements).

If you'd like to use [log-based incremental replication](/docs/integration.html#log-based-incremental-replication), also follow the ["Existing replication slot" step in the repository's README](https://github.com/transferwise/pipelinewise-tap-postgres#log-based-replication-requirements), since Meltano does not create a replication slot automatically.

#### Dependencies

`tap-postgres` [requires](https://www.psycopg.org/docs/install.html#runtime-requirements) the
[`libpq` library](https://www.postgresql.org/docs/current/libpq.html) to be available on your system.
If you've installed PostgreSQL, you should already have it, but you can also install it by itself using the
[`libpq-dev` package](https://pkgs.org/download/libpq-dev) on Ubuntu/Debian or the
[`libpq` Homebrew formula](https://formulae.brew.sh/formula/libpq) on macOS.

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-postgres` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-postgres
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "PostgreSQL".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Choose how to replicate each entity](/docs/getting-started.html#choose-how-to-replicate-each-entity)

    Supported [replication methods](/docs/integration.html#replication-methods):
    [`LOG_BASED`](/docs/integration.html#log-based-incremental-replication),
    [`INCREMENTAL`](/docs/integration.html#key-based-incremental-replication),
    [`FULL_TABLE`](/docs/integration.html#full-table-replication)

1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)

    Note that this extractor is incompatible with the default `datamill-co` [variants](/docs/plugins.html#variants)
    of [`target-postgres`](/plugins/loaders/postgres.html) and [`target-snowflake`](/plugins/loaders/snowflake.html),
    because they don't support stream names that include the source schema in addition to the table name: `<schema>-<table>`, e.g. `public-accounts`.

    Instead, use the `transferwise` variants that were made to be used with this extractor:
    [`target-postgres`](/plugins/loaders/postgres--transferwise.html) and [`target-snowflake`](/plugins/loaders/snowflake--transferwise.html).

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, refer to the ["Troubleshooting" section](#troubleshooting) below or [learn how to get help](/docs/getting-help.html).

## Settings

`tap-postgres` requires the [configuration](/docs/configuration.html) of the following settings:

- [Host](#host)
- [Port](#port)
- [User](#user)
- [Password](#password)
- [DBname](#dbname)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-postgres` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-9}
plugins:
  extractors:
  - name: tap-postgres
    variant: transferwise
    config:
      host: postgres.example.com
      port: 5432
      user: my_user
      dbname: my_database
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_POSTGRES_PASSWORD=my_password
```

### Host

- Name: `host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_HOST`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set host <host>

export TAP_POSTGRES_HOST=<host>
```

### Port

- Name: `port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_PORT`
- Default: `5432`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set port 5502

export TAP_POSTGRES_PORT=5502
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_USER`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set user <user>

export TAP_POSTGRES_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set password <password>

export TAP_POSTGRES_PASSWORD=<password>
```

### DBname

- Name: `dbname`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_DBNAME`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set dbname <database>

export TAP_POSTGRES_DBNAME=<database>
```

### SSL

- Name: `ssl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_SSL`
- Default: `false`

Using SSL via postgres `sslmode='require'` option.

If the server does not accept SSL connections or the client certificate is not recognized the connection will fail.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set ssl true

export TAP_POSTGRES_SSL=true
```

### Filter Schemas

- Name: `filter_schemas`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_FILTER_SCHEMAS`

Scan only the specified comma-separated schemas to improve the performance of data extraction

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set filter_schemas <schema1>,<schema2>

export TAP_POSTGRES_FILTER_SCHEMAS=<schema1>,<schema2>
```

### Default Replication Method

- Name: `default_replication_method`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_DEFAULT_REPLICATION_METHOD`
- Options: [`LOG_BASED`](/docs/integration.html#log-based-incremental-replication), [`INCREMENTAL`](/docs/integration.html#key-based-incremental-replication), [`FULL_TABLE`](/docs/integration.html#full-table-replication)

Default [replication method](/docs/integration.html#replication-methods) to use for tables that don't have `replication-method` [stream metadata](/docs/integration.html#setting-metadata) specified.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set default_replication_method <LOG_BASED|INCREMENTAL|FULL_TABLE>

export TAP_POSTGRES_DEFAULT_REPLICATION_METHOD=<LOG_BASED|INCREMENTAL|FULL_TABLE>
```

### Max Run Seconds

- Name: `max_run_seconds`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_MAX_RUN_SECONDS`
- Default: `43200`

Stop running the tap after certain number of seconds

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set max_run_seconds 100000

export TAP_POSTGRES_MAX_RUN_SECONDS=100000
```

### Logical Poll Total Seconds

- Name: `logical_poll_total_seconds`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_LOGICAL_POLL_TOTAL_SECONDS`
- Default: `10800`

Stop running the tap when no data received from wal after certain number of seconds

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set logical_poll_total_seconds 100000

export TAP_POSTGRES_LOGICAL_POLL_TOTAL_SECONDS=100000
```

### Break At End LSN

- Name: `break_at_end_lsn`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_POSTGRES_BREAK_AT_END_LSN`
- Default: `true`

Stop running the tap if the newly received lsn is after the max lsn that was detected when the tap started

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-postgres set break_at_end_lsn false

export TAP_POSTGRES_BREAK_AT_END_LSN=false
```

## Troubleshooting

### Error: `pg_config executable not found` or `libpq-fe.h: No such file or directory`

This error message indicates that the [`libpq`](https://www.postgresql.org/docs/current/libpq.html) dependency is missing.

To resolve this, refer to the ["Dependencies" section](#dependencies) above.
