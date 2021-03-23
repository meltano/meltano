---
sidebar: auto
description: Use Meltano to pull data from the Slack API and load it into Snowflake, PostgreSQL, and more
---

# Slack

The `tap-slack` [extractor](/plugins/extractors/) pulls data from the [Slack API](https://api.slack.com/).

- **Repository**: <https://github.com/Mashey/tap-slack>
- **Maintainer**: [Mashey](https://www.mashey.com/)
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-slack` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-slack
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Slack".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-slack` requires the [configuration](/docs/configuration.html) of the following settings:

For API Authentication:

- [JSON Web Token](#json-web-token)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

To obtain a token for a single workspace you will need to create a [Slack App](https://api.slack.com/apps?new_app=1) in your workspace and assigning it the relevant scopes. The minimum required scopes for the tap are:

    channels:history
    channels:join
    channels:read
    files:read
    groups:read
    links:read
    reactions:read
    remote_files:read
    remote_files:write
    team:read
    usergroups:read
    users.profile:read
    users:read

#### Minimal configuration

A minimal configuration of `tap-slack` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml
plugins:
  extractors:
  - name: tap-slack
    variant: mashey
    config:
        start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_ZOOM_JWT=my_jwt
```

### JSON Web Token

- Name: `jwt`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_JWT`

Your Slack JSON Web Token. The JWT is likely the easiest option for tap users. Configure the JWT with a very long expiry so it does not expire.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set jwt <jwt>

export TAP_ZOOM_JWT=<jwt>
```

### Client ID

- Name: `client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_CLIENT_ID`

Your Slack Client ID - example from docs: `7lstjK9NTyett_oeXtFiEQ`. See the [Slack OAuth App Credentials documentation](https://marketplace.slack.us/docs/guides/build/oauth-app#app-credentials) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set slack_client_id <client_id>

export TAP_ZOOM_CLIENT_ID=<client_id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_CLIENT_SECRET`

The Slack Client Secret that is generated when app credentials are created. See the [Slack OAuth App Credentials documentation](https://marketplace.slack.us/docs/guides/build/oauth-app#app-credentials) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set client_secret <client secret>

export TAP_ZOOM_CLIENT_SECRET=<client secret>
```

### Refresh Token

- Name: `refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ZOOM_REFRESH_TOKEN`

The Slack Refresh Token that is provided after successfully authenticating with Slack. See the [Slack OAuth Access Token Request documentation](https://marketplace.slack.us/docs/guides/auth/oauth#step-2-request-access-token) for more information.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set refresh_token <refresh token>

export TAP_ZOOM_REFRESH_TOKEN=<refresh token>
