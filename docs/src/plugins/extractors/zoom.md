---
sidebar: auto
description: Use Meltano to pull data from the Zoom API and load it into Snowflake, PostgreSQL, and more
---

# Zoom

The `tap-zoom` [extractor](/plugins/extractors/) pulls data from the [Zoom API](https://marketplace.zoom.us/docs/api-reference/introduction).

To learn more about `tap-zoom`, refer to the repository at <https://github.com/Mashey/tap-zoom>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-zoom` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-zoom
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Zoom".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-zoom` requires the [configuration](/docs/configuration.html) of the following settings:

In case of JSON Web Token authentication:

- [JSON Web Token](#json-web-token)

In case of OAuth authentication:

- [Client ID](#client-id)
- [Client Secret](#client-secret)
- [Refresh Token](#refresh-token)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.
Note that the Start Date is not available as the API does not support incremental replication.
Zoom also appears to "expire" meetings and webinars over time, making them unavailable to the API. Make sure your data lands in a trusted destination, as it may be the only place it eventually becomes available.

#### Minimal configuration

A minimal configuration of `tap-zoom` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-zoom
    variant: mashey
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_ZOOM_JWT=my_jwt
```

### JSON Web Token

- Name: `jwt`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_JWT`

Your Zoom JSON Web Token. The JWT is likely the easiest option for tap users. Configure the JWT with a very long expiry so it does not expire.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-zoom set jwt <jwt>

export TAP_ZOOM_JWT=<jwt>
```

### Client ID

- Name: `client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_CLIENT_ID`

Your Zoom Client ID - example from docs: `7lstjK9NTyett_oeXtFiEQ`. See the [Zoom OAuth App Credentials documentation](https://marketplace.zoom.us/docs/guides/build/oauth-app#app-credentials) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-zoom set zoom_client_id <client_id>

export TAP_ZOOM_CLIENT_ID=<client_id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_CLIENT_SECRET`

The Zoom Client Secret that is generated when app credentials are created. See the [Zoom OAuth App Credentials documentation](https://marketplace.zoom.us/docs/guides/build/oauth-app#app-credentials) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-zoom set client_secret <client secret>

export TAP_ZOOM_CLIENT_SECRET=<client secret>
```

### Refresh Token

- Name: `refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_REFRESH_TOKEN`

The Zoom Refresh Token that is provided after successfully authenticating with Zoom. See the [Zoom OAuth Access Token Request documentation](https://marketplace.zoom.us/docs/guides/auth/oauth#step-2-request-access-token) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-zoom set refresh_token <refresh token>

export TAP_ZOOM_REFRESH_TOKEN=<refresh token>
