---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into PostgreSQL
---

# PostgreSQL (`meltano` variant)

The `target-postgres` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into a [PostgreSQL](https://www.postgresql.org/) database.

To learn more about `target-postgres`, refer to the repository at <https://github.com/meltano/target-postgres>.

#### Alternative variants

Multiple [variants](/docs/plugins.html#variants) of `target-postgres` are available.
This document describes the `meltano` variant.

Alternative options are [`datamill-co`](./postgres.html) (default) and [`transferwise`](./postgres--transferwise.html).

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `meltano` variant of the `target-postgres` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-postgres --variant meltano
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the arrow next to the "Add to project" button for "PostgreSQL".
1. Choose "Add variant 'meltano'".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`target-postgres` requires the [configuration](/docs/configuration.html) of the following settings:

- [User](#user)
- [Password](#password)
- [Host](#host)
- [Port](#port)
- [DBname](#dbname)
- [Schema](#schema)

A [URL](#url) setting is also available that can be used as an alternative to setting User, Password, Host, Port, and DBname separately.

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-postgres` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-10}
plugins:
  loaders:
  - name: target-postgres
    variant: meltano
    config:
      user: my_user
      host: postgres.example.com
      port: 5432
      dbname: my_database
      # schema: my_schema   # override if default (see below) is not appropriate
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_POSTGRES_PASSWORD=my_password
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_USER`, alias: `PG_USERNAME`, `POSTGRES_USER`
- Default: `warehouse`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set user <user>

export TARGET_POSTGRES_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PASSWORD`, alias: `PG_PASSWORD`, `POSTGRES_PASSWORD`
- Default: `warehouse`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set password <password>

export TARGET_POSTGRES_PASSWORD=<password>
```

### Host

- Name: `host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_HOST`, alias: `PG_ADDRESS`, `POSTGRES_HOST`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set host <host>

export TARGET_POSTGRES_HOST=<host>
```

### Port

- Name: `port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_PORT`, alias: `PG_PORT`, `POSTGRES_PORT`
- Default: `5502`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set port 5432

export TARGET_POSTGRES_PORT=5432
```

### DBname

- Name: `dbname`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_DBNAME`, alias: `PG_DATABASE`, `POSTGRES_DBNAME`
- Default: `warehouse`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set dbname <database>

export TARGET_POSTGRES_DBNAME=<database>
```

### URL

- Name: `url`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_URL`, alias: `PG_URL`, `POSTGRES_URL`

Lets you set [User](#user), [Password](#password), [Host](#host), [Port](#port), and [DBname](#dbname) in one go using a [`postgresql://` URI](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql).

Takes precedence over the other settings when set.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set url postgresql://<username>:<password>@<host>:<port>/<database>

export TARGET_POSTGRES_URL=postgresql://<username>:<password>@<host>:<port>/<database>
```

### Schema

- Name: `schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_POSTGRES_SCHEMA`, alias: `PG_SCHEMA`, `POSTGRES_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-postgres set schema <schema>

export TARGET_POSTGRES_SCHEMA=<schema>
```
