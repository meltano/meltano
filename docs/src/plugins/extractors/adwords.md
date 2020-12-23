---
sidebar: auto
description: Use Meltano to pull data from the Google Ads (AdWords) API and load it into Snowflake, PostgreSQL, and more
---

# Google Ads (AdWords)

The `tap-adwords` [extractor](/plugins/extractors/) pulls data from the [Google AdWords API](https://developers.google.com/adwords/api/).

To learn more about `tap-adwords`, refer to the repository at <https://gitlab.com/meltano/tap-adwords>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-adwords` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-adwords
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Google Ads".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`tap-adwords` requires the [configuration](/docs/configuration.html) of the following settings:

- [Developer Token](#developer-token)
- [OAuth Client ID](#oauth-client-id)
- [OAuth Client Secret](#oauth-client-secret)
- [Refresh Token](#refresh-token)
- [Customer ID(s)](#customer-ids)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-adwords` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-adwords
    variant: meltano
    config:
      customer_ids: 1234567890,1234567891
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN=my_access_developer_token
export OAUTH_GOOGLE_ADWORDS_CLIENT_ID=my_oauth_client_id
export OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET=my_oauth_client_secret
export TAP_ADWORDS_REFRESH_TOKEN=my_refresh_token
```

### Developer Token

- Name: `developer_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN`, alias: `TAP_ADWORDS_DEVELOPER_TOKEN`

See <https://developers.google.com/adwords/api/docs/guides/first-api-call#request_a_developer_token>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set developer_token <token>

export OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN=<token>
```

### OAuth Client ID

- Name: `oauth_client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `OAUTH_GOOGLE_ADWORDS_OAUTH_CLIENT_ID`, alias: `TAP_ADWORDS_OAUTH_CLIENT_ID`

See <https://developers.google.com/adwords/api/docs/guides/first-api-call#set_up_oauth2_authentication>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set oauth_client_id <client_id>

export OAUTH_GOOGLE_ADWORDS_OAUTH_CLIENT_ID=<client_id>
```

### OAuth Client Secret

- Name: `oauth_client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `OAUTH_GOOGLE_ADWORDS_OAUTH_CLIENT_SECRET`, alias: `TAP_ADWORDS_OAUTH_CLIENT_SECRET`

See <https://developers.google.com/adwords/api/docs/guides/first-api-call#set_up_oauth2_authentication>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set oauth_client_secret <client_secret>

export OAUTH_GOOGLE_ADWORDS_OAUTH_CLIENT_SECRET=<client_secret>
```

### Refresh Token

- Name: `refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_REFRESH_TOKEN`

See <https://developers.google.com/adwords/api/docs/guides/first-api-call#get_an_oauth2_refresh_token_and_configure_your_client>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set refresh_token <token>

export TAP_ADWORDS_REFRESH_TOKEN=<token>
```

### Customer ID(s)

- Name: `customer_ids`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_CUSTOMER_IDS`

One or more comma-separated Google Ads Account IDs to extract data from.

#### How to get

To get your Account ID(s):

1. Visit the Google Ads management interface: <https://ads.google.com/>
2. Log in if you haven't already.
3. Make sure the correct account is selected in the top left corner.

![Screenshot of account selector](/images/tap-adwords/account-selector.png)

4. You will see the Account ID displayed inside the selector to the right of the account name, with added dashes for readability.

Remove the dashes before you enter the ID in Meltano: `205-667-8813` becomes `2056678813`.

If you want to extract data from multiple Ad Accounts, repeat the steps above to find the IDs (without dashes), and enter them in Meltano separated by commas (`,`).

For example:
- One Account ID: `1234567890`
- Multiple Account IDs: `1234567890,1234567891,1234567892`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set customer_ids <ids>

export TAP_ADWORDS_CUSTOMER_IDS=<ids>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_ADWORDS_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-adwords set start_date 2020-10-01T00:00:00Z

export TAP_ADWORDS_START_DATE=2020-10-01T00:00:00Z
```

### End Date

- Name: `end_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_END_DATE`

Date up to when historical data will be extracted.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set end_date YYYY-MM-DDTHH:MM:SSZ

export TAP_ADWORDS_END_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-adwords set end_date 2020-10-01T00:00:00Z

export TAP_ADWORDS_END_DATE=2020-10-01T00:00:00Z
```

### User Agent

- Name: `user_agent`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_USER_AGENT`
- Default: `tap-adwords via Meltano`

User agent to send to Google along with API requests. Typically includes name of integration and an email address you can be reached at, e.g. `tap-adwords via Meltano <user@example.com>`.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set user_agent <user_agent>

export TAP_ADWORDS_USER_AGENT=<user_agent>
```

### Conversion Window Days

- Name: `conversion_window_days`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_CONVERSION_WINDOW_DAYS`
- Default: `0`

How many Days before the Start Date to fetch data for Performance Reports

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set conversion_window_days 7

export TAP_ADWORDS_CONVERSION_WINDOW_DAYS=7
```

### Primary Keys

- Name: `primary_keys`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_ADWORDS_PRIMARY_KEYS`
- Default:

  ```json
  {
    "KEYWORDS_PERFORMANCE_REPORT": ["customerID", "campaignID", "adGroupID", "keywordID", "day", "network", "device"],
    "AD_PERFORMANCE_REPORT": ["customerID", "campaignID", "adGroupID", "adID", "day", "network", "device"]
  }
  ```

Primary Keys for the selected Entities (Streams)

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{5-8}
plugins:
  extractors:
  - name: tap-adwords
    variant: meltano
    config:
      primary_keys:
        <REPORT_NAME>: [<key1>, <key2>]
        # ...
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-adwords set primary_keys '{"<REPORT_NAME>": ["<key>", ...], ...}'

export TAP_ADWORDS_PRIMARY_KEYS='{"<REPORT_NAME>": ["<key>", ...], ...}'
```
