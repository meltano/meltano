---
sidebar: auto
description: Use Meltano to pull data from the Marketo API and load it into Snowflake, PostgreSQL, and more
---

# Marketo

The `tap-marketo` [extractor](/plugins/extractors/) pulls data from the [Marketo API](https://developers.marketo.com/rest-api/).

To learn more about `tap-marketo`, refer to the repository at <https://gitlab.com/meltano/tap-marketo>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-marketo` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-marketo
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Marketo".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select streams and properties to extract](/docs/getting-started.html#select-streams-and-properties-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`tap-marketo` requires the [configuration](/docs/configuration.html) of the following settings:

- [Endpoint](#endpoint)
- [Identity](#identity)
- [Client ID](#client-id)
- [Client Secret](#client-secret)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-marketo` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-10}
plugins:
  extractors:
  - name: tap-marketo
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-marketo.git
    config:
      endpoint: https://284-RPR-133.mktorest.com/rest
      identity: https://284-RPR-133.mktorest.com/identity
      client_id: 70ee92a1-603f-44a8-97a3-e0e55d758d1b
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_MARKETO_CLIENT_SECRET=my_secret
```

### Endpoint

- Name: `endpoint`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MARKETO_ENDPOINT`

Endpoint URL

See <https://developers.marketo.com/rest-api/base-url/>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-marketo set endpoint <endpoint_url>

export TAP_MARKETO_ENDPOINT=<endpoint_url>
```

### Identity

- Name: `identity`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MARKETO_IDENTITY`

Identity URL

See <https://developers.marketo.com/rest-api/base-url/>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-marketo set identity <identity_url>

export TAP_MARKETO_IDENTITY=<identity_url>
```

### Client ID

- Name: `client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MARKETO_CLIENT_ID`

See <https://developers.marketo.com/rest-api/authentication/>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-marketo set client_id <client_id>

export TAP_MARKETO_CLIENT_ID=<client_id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MARKETO_CLIENT_SECRET`

See <https://developers.marketo.com/rest-api/authentication/>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-marketo set client_secret <client_secret>

export TAP_MARKETO_CLIENT_SECRET=<client_secret>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_MARKETO_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-marketo set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_MARKETO_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-marketo set start_date 2020-10-01T00:00:00Z

export TAP_MARKETO_START_DATE=2020-10-01T00:00:00Z
```
