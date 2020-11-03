---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into SQLite
---

# SQLite

The `target-sqlite` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into a [SQLite](https://www.sqlite.org/) database.

To learn more about `target-sqlite`, refer to the repository at <https://gitlab.com/meltano/target-sqlite>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `target-sqlite` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-sqlite
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the "Add to project" button for "SQLite".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`target-sqlite` requires the [configuration](/docs/configuration.html) of the following settings:

- [Database](#database)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-sqlite` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-7}
plugins:
  loaders:
  - name: target-sqlite
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/target-sqlite.git
    config:
      database: my_database.db
```

### Database

- Name: `database`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SQLITE_DATABASE`, alias: `SQLITE_DATABASE`
- Default: `warehouse`

Name of the SQLite database file to be used or created, relative to the project root.

The `.db` extension is optional and will be added automatically when omitted.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-sqlite set database <database>

export TARGET_SQLITE_DATABASE=<database>
```

### Batch Size

- Name: `batch_size`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SQLITE_BATCH_SIZE`
- Default: `50`

How many records are sent to SQLite at a time?

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-sqlite set batch_size 100

export TARGET_SQLITE_BATCH_SIZE=100
```

### Timestamp Column

- Name: `timestamp_column`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SQLITE_TIMESTAMP_COLUMN`
- Default: `__loaded_at`

Name of the column used for recording the timestamp when Data are loaded to SQLite.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-sqlite set timestamp_column <column>

export TARGET_SQLITE_TIMESTAMP_COLUMN=<column>
```
