---
sidebar: auto
description: Use Meltano to pull data from the ReCharge API and load it into Snowflake, Postgres, and more
---

# ReCharge

The `tap-recharge` [extractor](/plugins/extractors/) pulls raw data from the [ReCharge API](https://rechargepayments.com/developers/).

To learn more about `tap-recharge`, refer to the repository at <https://github.com/singer-io/tap-recharge>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-recharge` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-recharge
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "ReCharge".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`tap-recharge` requires the [configuration](/docs/configuration.html) of the following settings:

- [Access Token](#access-token)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-recharge` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-7}
plugins:
  extractors:
  - name: tap-recharge
    variant: singer-io
    pip_url: tap-recharge==1.0.3
    config:
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_RECHARGE_ACCESS_TOKEN=my_access_token
```

### Access Token

- Name: `access_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_RECHARGE_ACCESS_TOKEN`

Private API token

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-recharge set access_token <token>

export TAP_RECHARGE_ACCESS_TOKEN=<token>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_RECHARGE_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-recharge set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_RECHARGE_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-recharge set start_date 2020-10-01T00:00:00Z

export TAP_RECHARGE_START_DATE=2020-10-01T00:00:00Z
```

### User Agent

- Name: `user_agent`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_RECHARGE_USER_AGENT`
- Default: `tap-recharge via Meltano`

User agent to send to ReCharge along with API requests. Typically includes name of integration and an email address you can be reached at, e.g. `tap-recharge via Meltano <user@example.com>`.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-recharge set user_agent <user_agent>

export TAP_RECHARGE_USER_AGENT=<user_agent>
```
