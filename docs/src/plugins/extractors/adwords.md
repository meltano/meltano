---
sidebar: auto
metaTitle: Extract Google Ads Data
description: Use Meltano to extract Google Ads data from the AdWords API and insert it into Postgres, Snowflake, and more.
---

# Google Ads

The Google Ads extractor pulls raw data from Google's [AdWords API](https://developers.google.com/adwords/api/docs/guides/start) and extracts the following resources from a Google Ads account:

- [Accounts / Managed Customer](https://developers.google.com/adwords/api/docs/reference/v201705/ManagedCustomerService.ManagedCustomer)
- [Campaigns](https://developers.google.com/adwords/api/docs/reference/v201705/CampaignService.Campaign)
- [Ad Groups](https://developers.google.com/adwords/api/docs/reference/v201705/AdGroupService.AdGroup)
- [Ads](https://developers.google.com/adwords/api/docs/reference/v201705/AdGroupAdService.AdGroupAd)
- [Ad Performance Report](https://developers.google.com/adwords/api/docs/appendix/reports/ad-performance-report)
- [Keywords Performance Report](https://developers.google.com/adwords/api/docs/appendix/reports/keywords-performance-report)

For more information you can check [the documentation for tap-adwords](https://gitlab.com/meltano/tap-adwords).

## Google Ads Setup

In order to access your Google Ads data, you will need the following:

- The Account IDs to replicate data from
- Your Developer Token for Google AdWords
- The Client ID and Secret for a valid Google OAuth Client
- A Refresh Token generated through the OAuth flow by using your OAuth Client and your Developer Token.

<h3 id="customer-ids">Account IDs</h3>

A comma-separated list of AdWords account IDs to replicate data from.

For example: `1234567890, 1234567891, 1234567892`

<h3 id="start-date">Start Date</h3>

This property allows you to configure where you want your extracted data set to start from.

:::tip Configuration Notes

- Determines how much historical data will be extracted.
- Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

<h3 id="end-date">End Date</h3>

This property allows you to configure where you want your extracted data set to end. Otherwise, if left blank, it will try to fetch all the Ads data from the Start Date until the date you run the Extractor.

<h3 id="refresh-token">OAuth Refresh Token</h3>

::: tip Get it now!
You can also use the <OAuthServiceLink provider="google-adwords">Meltano OAuth Service</OAuthServiceLink> to acquire this token.
:::

The Refresh Token generated through the OAuth flow run using your OAuth Client and your Developer Token.

You have to give access to your Ads Account (your google Account that manages your Google Ads).

You can check [Google's documentation on how to generate a Refresh Token](https://developers.google.com/adwords/api/docs/guides/first-api-call#get_an_oauth2_refresh_token_and_configure_your_client)

<h3 id="user-agent">User Agent for your OAuth Client</h3>

The User Agent for your OAuth Client (used in requests made to the AdWords API).

For example: `Meltano`

## Meltano Setup

::: warning Self-Hosted
Please note that this extractor requires advanced configuration for self-hosted Meltano instances.

If you do not have (1) a developer token for your Google Ads Account and (2) an approved Google OAuth Client, the process that you have to go through to generate those may take between one and four weeks.
:::

### Prerequisites

- [Running instance of Meltano](/docs/getting-started.html)
- A valid [Google OAuth 2.0 Client](https://console.cloud.google.com/apis/credentials), including:
  - [Your Developer Token for Google AdWords](https://developers.google.com/adwords/api/docs/guides/first-api-call#request_a_developer_token)
  - [Your Google OAuth Client ID](https://developers.google.com/adwords/api/docs/guides/first-api-call#set_up_oauth2_authentication)
  - [Your Google OAuth Client Secret](https://developers.google.com/adwords/api/docs/guides/first-api-call#set_up_oauth2_authentication)

### Configure the OAuth Client

In order for the extractor to properly authenticate on Google APIs, it requires to be able to acquire new access tokens.
The following variables are required for the authentication flow:

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN=<developer_token>
export OAUTH_GOOGLE_ADWORDS_CLIENT_ID=<client_id>
export OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET=<client_secret>
```

### Configuration with the Meltano UI

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and Google Ads Extractor highlighted](/images/adwords-tutorial/01-adwords-extractor-selection.png)

Let's install the Google Ads Extractor by clicking on the `Install` button inside its card.

On the configuration modal we want to enter all the fields descibed in the [Google Ads Setup](/plugins/extractors/adwords.html#google-ads-setup) section.

![Screenshot of the Google Ads Extractor Configuration](/images/adwords-tutorial/02-adwords-configuration.png)

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
1. Run the following command:

```bash
meltano add extractor tap-adwords
```

If you are successful, you should see `Added and installed extractors 'tap-adwords'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

Required:

```bash
export TAP_ADWORDS_REFRESH_TOKEN=""
export TAP_ADWORDS_USER_AGENT=""
export TAP_ADWORDS_CUSTOMER_IDS=""
export TAP_ADWORDS_START_DATE="2020-01-01T00:00:00Z"
```

Optional:

```bash
export TAP_ADWORDS_END_DATE="2020-02-17T00:00:00Z"
export TAP_ADWORDS_CONVERSION_WINDOW_DAYS=""
```

`TAP_ADWORDS_CONVERSION_WINDOW_DAYS` sets how many days before the **start_date** to fetch data for Performance Reports (default: 0)

Check the [README](https://gitlab.com/meltano/tap-adwords) for more details.
