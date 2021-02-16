---
sidebar: auto
description: Use Meltano to pull data from the Salesforce API and load it into Snowflake, PostgreSQL, and more
---

# Salesforce

The `tap-salesforce` [extractor](/plugins/extractors/) pulls data from the [Salesforce API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm).

To learn more about `tap-salesforce`, refer to the repository at <https://gitlab.com/meltano/tap-salesforce>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-salesforce` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-salesforce
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Salesforce".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-salesforce` requires the [configuration](/docs/configuration.html) of the following settings:

In case of username/password authentication:

- [Username](#username)
- [Password](#password)
- [Security Token](#security-token)

In case of OAuth authentication:

- [Client ID](#client-id)
- [Client Secret](#client-secret)
- [Refresh Token](#refresh-token)

Always:

- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-salesforce` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-salesforce
    variant: meltano
    config:
      username: user@example.com
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_SALESFORCE_PASSWORD=my_password
export TAP_SALESFORCE_SECURITY_TOKEN=my_token
```

### Username

- Name: `username`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_USERNAME`

The username (or email address) used to sign in to your Salesforce account

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set username <username>

export TAP_SALESFORCE_USERNAME=<username>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_PASSWORD`

The password used to sign in to your Salesforce account

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set password <password>

export TAP_SALESFORCE_PASSWORD=<password>
```

### Security Token

- Name: `security_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_SECURITY_TOKEN`

Access to Salesforce's API requires a security token that will authenticate you with the server.

#### How to get

If you don't already have a Salesforce Security Token for your account, you can generate one through the following steps:

1. Sign in to your [Salesforce Account](https://login.salesforce.com/).

1. Go to your Account Settings (top right on the header bar)

1. Click `Reset My Security Token` (Under the `My Personal Information` section)

1. Click `Reset Security Token`

An email with the Security Token will be sent to your email.

![Screenshot of Salesforce Security Token Reset](/images/salesforce/01-salesforce-reset-security-token.png)

::: tip

**Why is my "Reset Security Token" option missing?**

If a user’s profile is configured such that there is a restriction on the IP ranges that can access Salesforce, then that user will not have the ability to access/reset their security token.

In order to give access to the security token, either remove the user from the profile that contains the IP range restriction, or update the user’s profile by removing the IP range restriction.

In rare cases where the user’s profile doesn’t contain IP range restriction and they still can’t access the security token reset option, edit the user’s profile and save (without making any actual changes to the profile).

:::

::: tip

When you reset your Salesforce password, your security token resets as well. If that security token is used to integrate Meltano with Salesforce, that integration will break as well. Each time you reset an account password used to connect Meltano or other applications to Salesforce, you will need to re-enter your new security token into that application.

:::

::: warning

If you have other third-party applications integrated with Salesforce and you reset your security token, that integration will break. Try to use your existing Security Token instead of resetting your existing one. Otherwise, you will need to re-enter your new security token into all the connected applications.

:::

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesfroce set security_token <token>

export TAP_SALESFORCE_SECURITY_TOKEN=<token>
```

### Client ID

- Name: `client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_CLIENT_ID`

See <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_understanding_web_server_oauth_flow.htm>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set client_id <client_id>

export TAP_SALESFORCE_CLIENT_ID=<client_id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_CLIENT_SECRET`

See <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_understanding_web_server_oauth_flow.htm>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set client_secret <client_secret>

export TAP_SALESFORCE_CLIENT_SECRET=<client_secret>
```

### Refresh Token

- Name: `refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_REFRESH_TOKEN`

See <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_understanding_web_server_oauth_flow.htm>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set refresh_token <token>

export TAP_SALESFORCE_REFRESH_TOKEN=<token>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_SALESFORCE_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-salesforce set start_date 2020-10-01T00:00:00Z

export TAP_SALESFORCE_START_DATE=2020-10-01T00:00:00Z
```

### Is Sandbox

- Name: `is_sandbox`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_IS_SANDBOX`
- Default: `false`

Use Salesforce Sandbox

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set is_sandbox true

export TAP_SALESFORCE_IS_SANDBOX=true
```

### API Type

- Name: `api_type`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_API_TYPE`
- Options: `REST`, `BULK`
- Default: `REST`

Used to switch the behavior of the tap between using Salesforce's "REST" and "BULK" APIs.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set api_type BULK

export TAP_SALESFORCE_API_TYPE=BULK
```

### Select Fields By Default

- Name: `select_fields_by_default`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_SELECT_FIELDS_BY_DEFAULT`
- Default: `true`

Select by default any new fields discovered in Salesforce objects

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set select_fields_by_default false

export TAP_SALESFORCE_SELECT_FIELDS_BY_DEFAULT=false
```

### State Message Threshold

- Name: `state_message_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_STATE_MESSAGE_THRESHOLD`
- Default: `1000`

Used to throttle how often STATE messages are generated when the tap is using the "REST" API.

This is a balance between not slowing down execution due to too many STATE messages produced and how many records must be fetched again if a tap fails unexpectedly. Defaults to 1000 (generate a STATE message every 1000 records).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set state_message_threshold 500

export TAP_SALESFORCE_STATE_MESSAGE_THRESHOLD=500
```

### Max Workers

- Name: `max_workers`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_SALESFORCE_MAX_WORKERS`
- Default: `8`

Maximum number of threads to use

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-salesforce set max_workers 16

export TAP_SALESFORCE_MAX_WORKERS=16
```
