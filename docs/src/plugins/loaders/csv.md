---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into Comma Separated Values (CSV) files
---

::: warning
This page is now deprecated and will be removed in the future.

View the current documentation on the [MeltanoHub](https://hub.meltano.com/loaders/csv)
:::

# Comma Separated Values (CSV)

The `target-csv` [loader](https://hub.meltano.com/loaders/) loads [extracted](https://hub.meltano.com/extractors/) data into [Comma Separated Values (CSV)](https://en.wikipedia.org/wiki/Comma-separated_values) files.

- **Repository**: <https://github.com/singer-io/target-csv>
- **Maintainer**: [Stitch](https://www.stitchdata.com/)
- **Maintenance status**: Unresponsive to community issues and contributions
  - A [more active fork](https://github.com/singer-io/target-csv/network) may be available that you can [use instead](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin).
  - This plugin is [up for adoption](/docs/contributor-guide.html#adopting-a-plugin)!

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `target-csv` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-csv
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the "Add to project" button for "Comma Separated Values (CSV)".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`target-csv` requires the [configuration](/docs/configuration.html) of the following settings:

- [Destination Path](#destination-path)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-csv` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-6}
plugins:
  loaders:
  - name: target-csv
    variant: singer-io
    config:
      destination_path: my_csv_files
```

### Destination Path

- Name: `destination_path`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_CSV_DESTINATION_PATH`
- Default: `output`

Sets the destination path the CSV files are written to, relative to the project root.

The directory needs to exist already, it will not be created automatically.

To write CSV files to the project root, set an empty string (`""`).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-csv set destination_path <path>

export TARGET_CSV_DESTINATION_PATH=<path>
```

### Delimiter

- Name: `delimiter`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_CSV_DELIMITER`
- Options: Comma (`,`), Tab (`\t`), Semi-colon (`;`), Pipe (`|`)
- Default: `,`

A one-character string used to separate fields.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-csv set delimiter ";"

export TARGET_CSV_DELIMITER=";"
```

### QuoteChar

- Name: `quotechar`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_CSV_QUOTECHAR`
- Options: Single Quote (`'`), Double Quote (`"`)
- Default: `'`

A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-csv set quotechar '"'

export TARGET_CSV_QUOTECHAR='"'
```
