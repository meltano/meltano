---
sidebar: auto
description: Use Meltano to pull data from a BigQuery data warehouse and load it into Snowflake, PostgreSQL, and more
---

# BigQuery

The `tap-bigquery` [extractor](/plugins/extractors/) pulls data from a [BigQuery](https://cloud.google.com/bigquery) data warehouse.

- **Repository**: <https://github.com/anelendata/tap-bigquery>
- **Maintainer**: [Anelen](https://anelen.co/)
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

Then, follow the steps in the ["Activate the Google BigQuery API" section of the repository's README](https://github.com/anelendata/tap-bigquery#step-1-activate-the-google-bigquery-api).

### Installation and configuration

1. Add the `tap-bigquery` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-bigquery
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-bigquery` requires the [configuration](/docs/configuration.html) of the following settings:

- [Streams](#streams)
- [Credentials Path](#credentials-path)
- [Start Datetime](#start-datetime)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-bigquery` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-15}
plugins:
  extractors:
  - name: tap-bigquery
    variant: anelendata
    config:
      streams:
        - name: users
          table: "`my_project.my_dataset.users`"
          columns: [id, first_name, last_name, updated_at]
          datetime_key: updated_at
        - name: widgets
          table: "`my_project.my_dataset.widgets`"
          columns: [id, name, created_at]
          datetime_key: created_at
      start_datetime: '2020-10-01T00:00:00Z'
```

### Streams

- Name: `streams`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_STREAMS`

Array of objects with `name`, `table`, `columns`, `datetime_key`, and `filters` keys:

- `name`: The entity name, used by most loaders as the name of the table to be created.
- `table`: Fully qualified table name in BigQuery, with format `` `<project>.<dataset>.<table>` ``. Since backticks have special meaning in YAML, values in `meltano.yml` should be wrapped in double quotes.
- `columns`: Array of column names to select. Using `["*"]` is not recommended as it can become very expensive for a table with a large number of columns.
- `datetime_key`: Name of datetime column to use as [replication key](/docs/integration.html#replication-key).
- `filters`: Optional array of `WHERE` clauses to filter extracted data, e.g. `"column='value'"`.

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{5-14}
plugins:
  extractors:
  - name: tap-bigquery
    variant: anelendata
    config:
      streams:
        - name: <stream_name>
          table: "`<project>.<dataset>.<table>`"
          columns: [<column>, <column2>]
          datetime_key: <datetime_column>
          filters:
            - "<column>=<value>"
            # ...
        # ...
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set streams '[{"name": "<stream_name>", "table": "`<project>.<dataset>.<table>`", "columns": ["<column>", ...], "date_time_key": "<datetime_column>", "filters": [...]}, ...]'

export TAP_BIGQUERY_STREAMS='[{"name": "<stream_name>", "table": "`<project>.<dataset>.<table>`", "columns": ["<column>", ...], "date_time_key": "<datetime_column>", "filters": [...]}, ...]'
```

### Credentials Path

- Name: `credentials_path`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_CREDENTIALS_PATH`, alias: `GOOGLE_APPLICATION_CREDENTIALS`
- Default: `$MELTANO_PROJECT_ROOT/client_secrets.json`

Fully qualified path to `client_secrets.json` for your service account.

See the ["Activate the Google BigQuery API" section of the repository's README](https://github.com/anelendata/tap-bigquery#step-1-activate-the-google-bigquery-api) and <https://cloud.google.com/docs/authentication/production>.

By default, this file is expected to be at the root of your project directory.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set credentials_path /home/user/Downloads/client_secrets.json

export TAP_BIGQUERY_CREDENTIALS_PATH=/home/user/Downloads/client_secrets.json
```

### Start Datetime

- Name: `start_datetime`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_START_DATETIME`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set start_datetime YYYY-MM-DDTHH:MM:SSZ

export TAP_BIGQUERY_START_DATETIME=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-bigquery set start_datetime 2020-10-01T00:00:00Z

export TAP_BIGQUERY_START_DATETIME=2020-10-01T00:00:00Z
```

### End Datetime

- Name: `end_datetime`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_END_DATETIME`

Date up to when historical data will be extracted.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set end_datetime YYYY-MM-DDTHH:MM:SSZ

export TAP_BIGQUERY_END_DATETIME=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-bigquery set end_datetime 2020-10-01T00:00:00Z

export TAP_BIGQUERY_END_DATETIME=2020-10-01T00:00:00Z
```

### Limit

- Name: `limit`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_LIMIT`

Limits the number of records returned in each stream, applied as a limit in the query.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set limit 100

export TAP_BIGQUERY_LIMIT=100
```

### Start Always Inclusive

- Name: `start_always_inclusive`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_BIGQUERY_START_ALWAYS_INCLUSIVE`
- Default: `true`

When replicating incrementally, disable to only select records whose `datetime_key` is greater than the maximum value replicated in the last run, by excluding records whose timestamps match exactly.

This could cause records to be missed that were created after the last run finished, but during the same second and with the same timestamp.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-bigquery set start_always_inclusive false

export TAP_BIGQUERY_START_ALWAYS_INCLUSIVE=false
```
