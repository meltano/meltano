---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into BigQuery
---

# BigQuery

The `target-bigquery` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into a [BigQuery](https://cloud.google.com/bigquery) data warehouse.

To learn more about `target-bigquery`, refer to the repository at <https://github.com/adswerve/target-bigquery>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

Then, follow the steps in the ["Activate the Google BigQuery API" section of the repository's README](https://github.com/adswerve/target-bigquery#step-1-activate-the-google-bigquery-api).

### Installation and configuration

#### Using the Command Line Interface

1. Add the `target-bigquery` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-bigquery
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the "Add to project" button for "BigQuery".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`target-bigquery` requires the [configuration](/docs/configuration.html) of the following settings:

- [Project ID](#project-id)
- [Dataset ID](#dataset-id)
- [Location](#location)
- [Credentials Path](#credentials-path)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-bigquery` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-8}
plugins:
  loaders:
  - name: target-bigquery
    variant: adswerve
    config:
      project_id: my-project-id
      # dataset_id: my-dataset-id   # override if default (see below) is not appropriate
      location: EU
```

### Project ID

- Name: `project_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_PROJECT_ID`

BigQuery project

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set project_id <id>

export TARGET_BIGQUERY_PROJECT_ID=<id>
```

### Dataset ID

- Name: `dataset_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_DATASET_ID`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html).

BigQuery dataset

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set dataset_id <id>

export TARGET_BIGQUERY_DATASET_ID=<id>
```

### Location

- Name: `location`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_LOCATION`
- Default: `US`

Dataset location

See <https://cloud.google.com/bigquery/docs/locations>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set location EU

export TARGET_BIGQUERY_LOCATION=EU
```

### Credentials Path

- Name: `credentials_path`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_CREDENTIALS_PATH`, alias: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: `$MELTANO_PROJECT_ROOT/client_secrets.json`

Fully qualified path to `client_secrets.json` for your service account.

See the ["Activate the Google BigQuery API" section of the repository's README](https://github.com/adswerve/target-bigquery#step-1-activate-the-google-bigquery-api) and <https://cloud.google.com/docs/authentication/production>.

By default, this file is expected to be at the root of your project directory.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set credentials_path /home/user/Downloads/client_secrets.json

export TARGET_BIGQUERY_CREDENTIALS_PATH=/home/user/Downloads/client_secrets.json
```

### Validate Records

- Name: `validate_records`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_VALIDATE_RECORDS`
- Default: `false`

Validate records

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set validate_records true

export TARGET_BIGQUERY_VALIDATE_RECORDS=true
```

### Add Metadata Columns

- Name: `add_metadata_columns`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_ADD_METADATA_COLUMNS`
- Default: `false`

Add `_time_extracted` and `_time_loaded` metadata columns

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set add_metadata_columns true

export TARGET_BIGQUERY_ADD_METADATA_COLUMNS=true
```

### Replication Method

- Name: `replication_method`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_REPLICATION_METHOD`
- Options: `append`, `truncate`
- Default: `append`

Replication method, `append` or `truncate`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set replication_method truncate

export TARGET_BIGQUERY_REPLICATION_METHOD=truncate
```

### Table Prefix

- Name: `table_prefix`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_TABLE_PREFIX`

Add prefix to table name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set table_prefix <prefix>

export TARGET_BIGQUERY_TABLE_PREFIX=<prefix>
```

### Table Suffix

- Name: `table_suffix`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_TABLE_SUFFIX`

Add suffix to table name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set table_suffix <suffix>

export TARGET_BIGQUERY_TABLE_SUFFIX=<suffix>
```

### Max Cache

- Name: `max_cache`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_BIGQUERY_MAX_CACHE`
- Default: `50`

Maximum cache size in MB

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-bigquery set max_cache 100

export TARGET_BIGQUERY_MAX_CACHE=100
```
