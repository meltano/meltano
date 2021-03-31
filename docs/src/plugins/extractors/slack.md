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

`tap-slack` requires the [configuration](/docs/configuration.html) of the following setting:

- [API Token](#api-token)

This and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-slack` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml
plugins:
  extractors:
  - name: tap-slack
    variant: mashey
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_SLACK_API_TOKEN=my_api_token
```

### API Token

- Name: `api_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_API_TOKEN`

Your Slack API Token. To obtain a token for a single workspace you will need to create a [Slack App](https://api.slack.com/apps?new_app=1) in your workspace and assigning it the relevant scopes. The minimum required scopes for the tap are:

* `channels:history`
* `channels:join`
* `channels:read`
* `files:read`
* `groups:read`
* `links:read`
* `reactions:read`
* `remote_files:read`
* `remote_files:write`
* `team:read`
* `usergroups:read`
* `users.profile:read`
* `users:read`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set api_token <api_token>

export TAP_SLACK_API_TOKEN=<api_token>
```

### Channels

- Name: `channels`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_CHANNELS`

Optionally specify specific channels to sync. By default the tap will sync all channels it has been invited to, but this can be overriden using this configuration. Note that the values need to be channel ID, not the name, as [recommended by the Slack API](https://api.slack.com/types/conversation#other_attributes). To get the ID for a channel, either use the Slack API or find it in the [URL](https://www.wikihow.com/Find-a-Channel-ID-on-Slack-on-PC-or-Mac).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set channels '["<channelid>", ...]'

export TAP_SLACK_CHANNELS='["<channelid>", ...]'
```

### Private Channels

- Name: `private_channels`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_PRIVATE_CHANNELS`
- Default: `true`

Specifies whether to sync private channels or not. Default is true.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set private_channels false

export TAP_SLACK_PRIVATE_CHANNELS=false
```

### Public Channels

- Name: `join_public_channels`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_JOIN_PUBLIC_CHANNELS`
- Default: `false`

Specifies whether to have the tap auto-join all public channels in your ogranziation. Default is false.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set join_public_channels true

export TAP_SLACK_JOIN_PUBLIC_CHANNELS=true
```

### Archived Channels

- Name: `archived_channels`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_ARCHIVED_CHANNELS`
- Default: `false`

Specifies whether the tap will sync archived channels or not. Note that a bot cannot join an archived channel, so unless the bot was added to the channel prior to it being archived it will not be able to sync the data from that channel. Default is false.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set archived_channels true

export TAP_SLACK_ARCHIVED_CHANNELS=true
```

### Date Window Size

- Name: `date_window_size`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SLACK_DATE_WINDOW_SIZE`
- Default: `7`

Specifies the window size for syncing certain streams (messages, files, threads). The default is 7 days.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-slack set date_window_size <integer>

export TAP_SLACK_DATE_WINDOW_SIZE=<integer>
```
