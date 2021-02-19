---
sidebar: auto
description: Use Meltano to pull data from the Intacct API and load it into Snowflake, PostgreSQL, and more
---

# Sage Intacct

The `tap-intacct` [extractor](/plugins/extractors/) pulls data from the [Intacct API](https://developer.intacct.com/api/).

To learn more about `tap-intacct`, refer to the repository at <https://github.com/hotgluexyz/tap-intacct>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-intacct` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-intacct
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Sage Intacct".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-intacct` requires the [configuration](/docs/configuration.html) of the following settings:

- [Company Id](#company-id)
- [Sender Id](#sender-id)
- [Sender Password](#sender-password)
- [User Id](#user-id)
- [User Password](#user-password)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-intacct` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-intacct
    variant: hotgluexyz
    config:
      company_id: 'example company'
      sender_id: 'example sender'
      user_id: 'example user'
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_INTACCT_SENDER_PASSWORD=my_sender_password
```

### Company Id

- Name: `company_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_COMPANY_ID`

Your Intacct Company Id

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set company_id <company id>

export TAP_INTACCT_COMPANY_ID=<company id>
```

### Sender Id

- Name: `sender_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_SENDER_ID`

Your Intacct Sender Id

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set sender_id <sender id>

export TAP_INTACCT_SENDER_ID=<sender id>
```

### Sender Password

- Name: `sender_password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_SENDER_PASSWORD`

Your Intacct Sender Password

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set sender_password <sender password>

export TAP_INTACCT_SENDER_PASSWORD=<sender password>
```

### User Id

- Name: `user_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_USER_ID`

Your Intacct User Id

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set user_id <user id>

export TAP_INTACCT_USER_ID=<user id>
```

### User Password

- Name: `user_password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_USER_PASSWORD`

Your Intacct User Password

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set user_password <user password>

export TAP_INTACCT_USER_PASSWORD=<user password>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_INTACCT_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-intacct set start_date 2020-10-01T00:00:00Z

export TAP_INTACCT_START_DATE=2020-10-01T00:00:00Z
```

### Select Fields By Default

- Name: `select_fields_by_default`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_SELECT_FIELDS_BY_DEFAULT`
- Default: `true`

Select by default any new fields discovered in Intacct objects

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set select_fields_by_default false

export TAP_INTACCT_SELECT_FIELDS_BY_DEFAULT=false
```

### State Message Threshold

- Name: `state_message_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_STATE_MESSAGE_THRESHOLD`
- Default: `1000`

Used to throttle how often STATE messages are generated when the tap is using the "REST" API.

This is a balance between not slowing down execution due to too many STATE messages produced and how many records must be fetched again if a tap fails unexpectedly. Defaults to 1000 (generate a STATE message every 1000 records).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set state_message_threshold 500

export TAP_INTACCT_STATE_MESSAGE_THRESHOLD=500
```

### Max Workers

- Name: `max_workers`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_INTACCT_MAX_WORKERS`
- Default: `8`

Maximum number of threads to use

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-intacct set max_workers 16

export TAP_INTACCT_MAX_WORKERS=16
```
