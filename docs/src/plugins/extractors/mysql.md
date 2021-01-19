---
sidebar: auto
description: Use Meltano to pull data from a MySQL or MariaDB database and load it into Snowflake, PostgreSQL, and more
---

# MySQL / MariaDB

The `tap-mysql` [extractor](/plugins/extractors/) pulls data from a [MySQL](https://www.mysql.com/) or [MariaDB](https://mariadb.org/) database.

To learn more about `tap-mysql`, refer to the repository at <https://github.com/transferwise/pipelinewise-tap-mysql> and documentation at <https://transferwise.github.io/pipelinewise/connectors/taps/mysql.html>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

Then, follow the steps in the ["Setup requirements" section of the documentation](https://transferwise.github.io/pipelinewise/connectors/taps/mysql.html#mysql-setup-requirements).

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-mysql` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-mysql
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "MySQL".
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

## Settings

`tap-mysql` requires the [configuration](/docs/configuration.html) of the following settings:

- [Host](#host)
- [Port](#port)
- [User](#user)
- [Password](#password)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-mysql` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-8}
plugins:
  extractors:
  - name: tap-mysql
    variant: transferwise
    config:
      host: mysql.example.com
      port: 3306
      user: my_user
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_MYSQL_PASSWORD=my_password
```

### Host

- Name: `host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_HOST`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set host <host>

export TAP_MYSQL_HOST=<host>
```

### Port

- Name: `port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_PORT`
- Default: `3306`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set port 3307

export TAP_MYSQL_PORT=3307
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_USER`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set user <user>

export TAP_MYSQL_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set password <password>

export TAP_MYSQL_PASSWORD=<password>
```

### Database

- Name: `database`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_DATABASE`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set database <database>

export TAP_MYSQL_DATABASE=<database>
```

### SSL

- Name: `ssl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_SSL`
- Default: `false`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set ssl true

export TAP_MYSQL_SSL=true
```

### Filter DBs

- Name: `filter_dbs`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_FILTER_DBS`

Comma separated list of schemas to extract tables only from particular schemas and to improve data extraction performance

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set filter_dbs <schema1>,<schema2>

export TAP_MYSQL_FILTER_DBS=<schema1>,<schema2>
```

### Export Batch Rows

- Name: `export_batch_rows`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_EXPORT_BATCH_ROWS`
- Default: `50000`

Number of rows to export from MySQL in one batch.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set export_batch_rows 100000

export TAP_MYSQL_EXPORT_BATCH_ROWS=100000
```

### Session SQLs

- Name: `session_sqls`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MYSQL_SESSION_SQLS`
- Default:

  ```json
  [
    "SET @@session.time_zone='+0:00'",
    "SET @@session.wait_timeout=28800",
    "SET @@session.net_read_timeout=3600",
    "SET @@session.innodb_lock_wait_timeout=3600"
  ]
  ```

List of SQL commands to run when a connection made. This allows to set session variables dynamically, like timeouts.

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{5-8}
plugins:
  extractors:
  - name: tap-mysql
    variant: transferwise
    config:
      session_sqls:
        - SET @@session.<variable>=<value>
        # ...
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-mysql set session_sqls '["SET @@session.<variable>=<value>", ...]'

export TAP_MYSQL_SESSION_SQLS='["SET @@session.<variable>=<value>", ...]'
```
