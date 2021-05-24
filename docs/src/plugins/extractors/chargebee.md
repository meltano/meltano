---
sidebar: auto
description: Use Meltano to pull data from the Chargebee API and load it into Snowflake, PostgreSQL, and more
---

# Chargebee

The `tap-chargebee` [extractor](https://hub.meltano.com/extractors/) pulls data from the [Chargebee API](https://apidocs.chargebee.com/docs/api).

- **Repository**: <https://github.com/hotgluexyz/tap-chargebee>
- **Maintainer**: [Hotglue](https://hotglue.xyz/)
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-chargebee` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-chargebee
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Chargebee".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-chargebee` requires the [configuration](/docs/configuration.html) of the following settings:

- [API Key](#api-key)
- [Site](#site)
- [Product Catalog](#product-catalog)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-chargebee` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-chargebee
    variant: hotgluexyz
    config:
      product_catalog: '1.0'
      site: 'example.chargebee.com'
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_CHARGEBEE_API_KEY=my_client_id
```

### API Key

- Name: `api_key`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_API_KEY`

Your Chargebee API Key

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set api_key <api key>

export TAP_CHARGEBEE_API_KEY=<api key>
```

### Site

- Name: `site`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_SITE`

Your Chargebee site `{site}.chargebee.com`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set chargebee_site <site>

export TAP_CHARGEBEE_SITE=<site>
```

### Product Catalog

- Name: `product_catalog`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_PRODUCT_CATALOG`

The Chargebee product catalog you wish to use. Valid values are `1.0` or `2.0`.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set product_catalog <product catalog>

export TAP_CHARGEBEE_PRODUCT_CATALOG=<product catalog>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_CHARGEBEE_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-chargebee set start_date 2020-10-01T00:00:00Z

export TAP_CHARGEBEE_START_DATE=2020-10-01T00:00:00Z
```

### Select Fields By Default

- Name: `select_fields_by_default`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_SELECT_FIELDS_BY_DEFAULT`
- Default: `true`

Select by default any new fields discovered in Chargebee objects

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set select_fields_by_default false

export TAP_CHARGEBEE_SELECT_FIELDS_BY_DEFAULT=false
```

### State Message Threshold

- Name: `state_message_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_STATE_MESSAGE_THRESHOLD`
- Default: `1000`

Used to throttle how often STATE messages are generated when the tap is using the "REST" API.

This is a balance between not slowing down execution due to too many STATE messages produced and how many records must be fetched again if a tap fails unexpectedly. Defaults to 1000 (generate a STATE message every 1000 records).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set state_message_threshold 500

export TAP_CHARGEBEE_STATE_MESSAGE_THRESHOLD=500
```

### Max Workers

- Name: `max_workers`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_CHARGEBEE_MAX_WORKERS`
- Default: `8`

Maximum number of threads to use

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-chargebee set max_workers 16

export TAP_CHARGEBEE_MAX_WORKERS=16
```
