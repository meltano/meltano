---
sidebar: auto
description: Use Meltano to pull data from the Quickbooks Online API and load it into Snowflake, PostgreSQL, and more
---

# Quickbooks

The `tap-quickbooks` [extractor](/plugins/extractors/) pulls data from the [Quickbooks Online API](https://developer.intuit.com/app/developer/qbo/docs/develop).

To learn more about `tap-quickbooks`, refer to the repository at <https://github.com/hotgluexyz/tap-quickbooks>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-quickbooks` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-quickbooks
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Quickbooks".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-quickbooks` requires the [configuration](/docs/configuration.html) of the following settings:

- [Client ID](#client-id)
- [Client Secret](#client-secret)
- [Refresh Token](#refresh-token)
- [Realm ID](#realm-id)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-quickbooks` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-quickbooks
    variant: hotgluexyz
    config:
      start_date: '2020-10-01T00:00:00Z'
      realmId: '4000000000'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_QUICKBOOKS_CLIENT_ID=my_client_id
export TAP_QUICKBOOKS_CLIENT_SECRET=my_client_secret
export TAP_QUICKBOOKS_REFRESH_TOKEN=my_token
```

### Client ID

- Name: `client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_CLIENT_ID`

Your Quickbooks Online OAuth client ID

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set client_id <client id>

export TAP_QUICKBOOKS_CLIENT_ID=<client id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_CLIENT_SECRET`

Your Quickbooks Online OAuth client secret

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set client_secret <client secret>

export TAP_QUICKBOOKS_CLIENT_SECRET=<client secret>
```

### Refresh Token

- Name: `refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_REFRESH_TOKEN`

Access to Quickbooks's API requires a refresh token that will authenticate you with the server.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set refresh_token <token>

export TAP_QUICKBOOKS_REFRESH_TOKEN=<token>
```

### Realm ID

- Name: `realmId`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_REALMID`

Access to Quickbooks's API requires a the realm ID (company ID) you wish to connect to.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set realmId <id>

export TAP_QUICKBOOKS_REALMID=<id>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_QUICKBOOKS_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-quickbooks set start_date 2020-10-01T00:00:00Z

export TAP_QUICKBOOKS_START_DATE=2020-10-01T00:00:00Z
```

### Is Sandbox

- Name: `is_sandbox`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_IS_SANDBOX`
- Default: `false`

Use Quickbooks Sandbox

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set is_sandbox true

export TAP_QUICKBOOKS_IS_SANDBOX=true
```

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set api_type BULK

export TAP_QUICKBOOKS_API_TYPE=BULK
```

### Select Fields By Default

- Name: `select_fields_by_default`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_SELECT_FIELDS_BY_DEFAULT`
- Default: `true`

Select by default any new fields discovered in Quickbooks objects

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set select_fields_by_default false

export TAP_QUICKBOOKS_SELECT_FIELDS_BY_DEFAULT=false
```

### State Message Threshold

- Name: `state_message_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_STATE_MESSAGE_THRESHOLD`
- Default: `1000`

Used to throttle how often STATE messages are generated when the tap is using the "REST" API.

This is a balance between not slowing down execution due to too many STATE messages produced and how many records must be fetched again if a tap fails unexpectedly. Defaults to 1000 (generate a STATE message every 1000 records).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set state_message_threshold 500

export TAP_QUICKBOOKS_STATE_MESSAGE_THRESHOLD=500
```

### Max Workers

- Name: `max_workers`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_QUICKBOOKS_MAX_WORKERS`
- Default: `8`

Maximum number of threads to use

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-quickbooks set max_workers 16

export TAP_QUICKBOOKS_MAX_WORKERS=16
```
