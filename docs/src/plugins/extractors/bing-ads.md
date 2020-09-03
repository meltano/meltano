---
sidebar: auto
metaTitle: Extract Bing Ads Data
description: Use Meltano to extract Bing Ads data from the AdWords API and insert it into Postgres, Snowflake, and more.
lastUpdatedSignificantly: 2020-04-30
---

# Bing Ads

The `tap-bing-ads` extractor pulls raw data from the [Bing Ads API](https://docs.microsoft.com/en-us/advertising/guides/).

For more details, refer to the repository at <https://github.com/singer-io/tap-bing-ads>.

## Installation

### Using the Command Line Interface

1. Add the `tap-bing-ads` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-bing-ads
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

### Using Meltano UI

1. Start Meltano UI using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Bing Ads".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

## Settings

`tap-bing-ads` requires the [configuration](/docs/configuration.html) of the following settings:

- [Developer Token](#developer-token)
- [OAuth Client ID](#oauth-client-id)
- [OAuth Client Secret](#oauth-client-secret)
- [Customer ID](#customer-id)
- [Account IDs](#account-ids)
- [Refresh Token](#refresh-token)
- [Start Date](#start-date)

### Developer Token

- Name: `developer_token`
- Environment variable: `OAUTH_BING_ADS_DEVELOPER_TOKEN`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#get-developer-token>.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an environment variable:

```bash
meltano config tap-bing-ads set developer_token <token>

export OAUTH_BING_ADS_DEVELOPER_TOKEN=<token>
```

### OAuth Client ID

- Name: `oauth_client_id`
- Environment variable: `OAUTH_BING_ADS_CLIENT_ID`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#quick-start-production>.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an environment variable:

```bash
meltano config tap-bing-ads set oauth_client_id <id>

export OAUTH_BING_ADS_CLIENT_ID=<id>
```

### OAuth Client Secret

- Name: `oauth_client_secret`
- Environment variable: `OAUTH_BING_ADS_CLIENT_SECRET`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#quick-start-production>.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an environment variable:

```bash
meltano config tap-bing-ads set oauth_client_secret <secret>

export OAUTH_BING_ADS_CLIENT_SECRET=<secret>
```

### Customer ID

- Name: `customer_id`
- Environment variable: `TAP_BING_ADS_CUSTOMER_ID`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#get-ids>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an environment variable:

```bash
meltano config tap-bing-ads set customer_id <id>

export TAP_BING_ADS_CUSTOMER_ID=<id>
```

### Account IDs

- Name: `account_ids`
- Environment variable: `TAP_BING_ADS_ACCOUNT_IDS`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#get-ids>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an environment variable:

```bash
meltano config tap-bing-ads set account_ids <id>

export TAP_BING_ADS_ACCOUNT_IDS=<id>
```

### Refresh Token

- Name: `refresh_token`
- Environment variable: `TAP_BING_ADS_REFRESH_TOKEN`

See <https://docs.microsoft.com/en-us/advertising/guides/get-started#quick-start-production>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an environment variable:

```bash
meltano config tap-bing-ads set refresh_token <token>

export TAP_BING_ADS_REFRESH_TOKEN=<token>
```

### Start Date

- Name: `start_date`
- Environment variable: `TAP_BING_ADS_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an environment variable:

```bash
meltano config tap-bing-ads set start_date <date>

export TAP_BING_ADS_START_DATE=<date>
```
