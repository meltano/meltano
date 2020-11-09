---
sidebar: auto
description: Use Meltano to pull data from CSV files and Excel spreadsheets on cloud or local storage and load it into Snowflake, PostgreSQL, and more
---

# Spreadsheets Anywhere

The `tap-spreadsheets-anywhere` [extractor](/plugins/extractors/) pulls data from [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) files and Excel spreadsheets on cloud or local storage.

To learn more about `tap-spreadsheets-anywhere`, refer to the repository at <https://github.com/ets/tap-spreadsheets-anywhere>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

1. Add the `tap-spreadsheets-anywhere` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-spreadsheets-anywhere
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`tap-spreadsheets-anywhere` requires the [configuration](/docs/configuration.html) of the following settings:

- [Tables](#tables)

#### Minimal configuration

A minimal configuration of `tap-spreadsheets-anywhere` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-20}
plugins:
  extractors:
  - name: tap-spreadsheets-anywhere
    variant: etc
    pip_url: git+https://github.com/ets/tap-spreadsheets-anywhere.git
    config:
      tables:
        - path: s3://my-s3-bucket
          name: target_table_name
          pattern: "subfolder/common_prefix.*"
          start_date: "2017-05-01T00:00:00Z"
          key_properties: []
          format: csv
        - path: file:///home/user/Downloads/xls_files
          name: another_table_name
          pattern: "subdir/.*User.*"
          start_date: "2017-05-01T00:00:00Z"
          key_properties: [id]
          format: excel
          worksheet_name: Names
```

### Tables

- Name: `tables`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SPREADSHEETS_ANYWHERE_TABLES`

Array holding objects that each describe a set of targeted source files.

See <https://github.com/ets/tap-spreadsheets-anywhere#configuration>.

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{6-14}
plugins:
  extractors:
  - name: tap-spreadsheets-anywhere
    variant: etc
    pip_url: git+https://github.com/ets/tap-spreadsheets-anywhere.git
    config:
      tables:
        - path: <path>
          name: <table_name>
          pattern: "<pattern>"
          start_date: "YYYY-MM-DDTHH:MM:SSZ"
          key_properties: [<key>]
          format: <csv|excel>
        # ...
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-spreadsheets-anywhere set tables '[{"path": "<path>", ...}, ...]'

export TAP_SPREADSHEETS_ANYWHERE_TABLES='[{"path": "<path>", ...}, ...]'
```
