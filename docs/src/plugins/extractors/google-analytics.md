---
sidebar: auto
description: Use Meltano to pull data from the Google Analytics API and load it into Snowflake, PostgreSQL, and more
---

# Google Analytics

The `tap-google-analytics` [extractor](/plugins/extractors/) pulls data from the [Google Analytics Reporting API](https://developers.google.com/analytics/devguides/reporting/core/v4/).

- **Repository**: <https://gitlab.com/meltano/tap-google-analytics>
- **Maintainer**: Meltano community
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-google-analytics` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-google-analytics
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

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-google-analytics` requires the [configuration](/docs/configuration.html) of the following settings:

In case of service account authentication:

- [Key File Location](#key-file-location)

In case of OAuth authentication:

- [OAuth Credentials: Client ID](#oauth-credentials-client-id)
- [OAuth Credentials: Client Secret](#oauth-credentials-client-secret)
- [OAuth Credentials: Access Token](#oauth-credentials-access-token)
- [OAuth Credentials: Refresh Token](#oauth-credentials-refresh-token)

Always:

- [View ID](#view-id)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-google-analytics` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      view_id: 188274549
      start_date: '2020-10-01T00:00:00Z'
```

### Key File Location

- Name: `key_file_location`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_KEY_FILE_LOCATION`, alias: `GOOGLE_ANALYTICS_API_CLIENT_SECRETS`
- Default: `$MELTANO_PROJECT_ROOT/client_secrets.json`

Fully qualified path to `client_secrets.json` for your service account.

See <https://developers.google.com/analytics/devguides/reporting/core/v4/authorization#service_accounts>.

By default, this file is expected to be at the root of your project directory.

#### How to get

Follow the steps below if you don't already have a valid `client_secrets.json` to upload. The process below can take over 10 minutes, but it's a one-time setup that's well worth it.

This extractor supports service account based authorization, where an administrator manually creates a service account with the appropriate permissions to view the account, property, and view you wish to fetch data from.

To access your Google Analytics data, the "Analytics Reporting API" and "Analytics API" both need to be enabled. These need to be enabled for a project inside the same organization as your Google Analytics account.

##### Step 1: Creating Service Account Credentials

As a first step, you need to create a new project in Google Cloud Platform or use an existing one:

1. Sign in to the Google Account you are using for managing Google Analytics (you must have Manage Users permission at the account, property, or view level).

2. Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts). If prompted, select a project or create a new one to use for accessing Google Analytics.

   ![Screenshot of Google Service Accounts page](/images/tap-google-analytics/02-ga-service-account-configuration-create-new-account.png)

3. Click "Create service account"

   In the Create service account window, type a name for the service account, and click `Create`.

   We do not need to provide any additional permissions for this account, so click `Continue` in the `Service account permissions` configuration page.

   We also do not need to grant access to any users for this service account, as we only need the key.

   ![Screenshot of Google Service Account Configuration for new Account](/images/tap-google-analytics/02-ga-service-account-configuration-new-account.png)

   Click `Create Key`, select `JSON` as the key type and create a new private key. Then click `Save` and store it locally as `client_secrets.json`.

Meltano will use the private key in this `client_secrets.json` file to connect with the Google Analytics API.

##### Step 2: Linking Credentials to Google Analytics

The newly created service account will have an email address that looks similar to:

```
service-account-name@PROJECT-ID.iam.gserviceaccount.com
```

To grant this service account access to your Google Analytics data, add the email address as a [new user](https://support.google.com/analytics/answer/1009702) to your Google Analytics account, property or view through the "Admin > User Management" page.

Only the [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495) are needed as Meltano only extracts data to generate reports.

![Screenshot of Google Analytics Add User](/images/tap-google-analytics/03-ga-add-user.png)

##### Step 3: Enabling the APIs

1. Visit the [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) dashboard and make sure that the project you used in the previous step is selected.

   Now enable the API using the button at the top, so that the button will say "Disable API" instead:

   ![Screenshot of Google Analytics Reporting API](/images/tap-google-analytics/04-ga-reporting-api.png)

2. Next, visit the [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) dashboard, make sure that the project you used in the previous step is selected, and enable this API as well.

   ![Screenshot of Google Analytics API](/images/tap-google-analytics/05-ga-api.png)

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set key_file_location /home/user/Downloads/client_secrets.json

export TAP_GOOGLE_ANALYTICS_KEY_FILE_LOCATION=/home/user/Downloads/client_secrets.json
```

### OAuth Credentials: Client ID

- Name: `oauth_credentials.client_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_ID`, alias: `GOOGLE_ANALYTICS_API_OAUTH_CLIENT_ID`

See <https://developers.google.com/analytics/devguides/reporting/core/v4/authorization#OAuth2Authorizing>.

Takes precedence over [Key File Location](#key-file-location) if both are specified.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set oauth_credentials client_id <client_id>

export TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_ID=<client_id>
```

### OAuth Credentials: Client Secret

- Name: `oauth_credentials.client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_SECRET`, alias: `GOOGLE_ANALYTICS_API_OAUTH_CLIENT_SECRET`

See <https://developers.google.com/analytics/devguides/reporting/core/v4/authorization#OAuth2Authorizing>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set oauth_credentials client_secret <client_secret>

export TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_SECRET=<client_secret>
```

### OAuth Credentials: Access Token

- Name: `oauth_credentials.access_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_ACCESS_TOKEN`, alias: `GOOGLE_ANALYTICS_API_OAUTH_ACCESS_TOKEN`

See <https://developers.google.com/analytics/devguides/reporting/core/v4/authorization#OAuth2Authorizing>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set oauth_credentials access_token <token>

export TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_ACCESS_TOKEN=<token>
```

### OAuth Credentials: Refresh Token

- Name: `oauth_credentials.refresh_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_REFRESH_TOKEN`, alias: `GOOGLE_ANALYTICS_API_OAUTH_REFRESH_TOKEN`

See <https://developers.google.com/analytics/devguides/reporting/core/v4/authorization#OAuth2Authorizing>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set oauth_credentials refresh_token <token>

export TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_REFRESH_TOKEN=<token>
```

### View ID

- Name: `view_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_VIEW_ID`, alias: `GOOGLE_ANALYTICS_API_VIEW_ID`

Google Analytics View ID

#### How to get

To get your View ID:

1. Visit Google Analytics: <https://analytics.google.com/>
2. Log in if you haven't already.
3. Open the account/property/view selector in the top left corner

![Screenshot of closed account selector](/images/tap-google-analytics/account-selector-closed.png)

3. Select the account, property, and view that you would like to connect with Meltano

![Screenshot of open account selector](/images/tap-google-analytics/account-selector-open.png)

4. You will see the View ID displayed inside the selector below the name of the view (e.g. "All Web Site Data"): `188274549`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set view_id <id>

export TAP_GOOGLE_ANALYTICS_VIEW_ID=<ids>
```

### Reports

- Name: `reports`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_REPORTS`, alias: `GOOGLE_ANALYTICS_API_REPORTS`
- Default: Bundled [`defaults/default_report_definition.json`](https://gitlab.com/meltano/tap-google-analytics/blob/master/tap_google_analytics/defaults/default_report_definition.json)

Project-relative path to JSON file with the definition of the reports to be generated.

See <https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/> for valid dimensions and metrics.

The JSON structure expected is as follows:

```json
[
  { "name" : "name of stream to be used",
    "dimensions" :
    [
      "Google Analytics Dimension",
      "Another Google Analytics Dimension",
      // ... up to 7 dimensions per stream ...
    ],
    "metrics" :
    [
      "Google Analytics Metric",
      "Another Google Analytics Metric",
      // ... up to 10 metrics per stream ...
    ]
  },
  // ... as many streams / reports as the user wants ...
]
```

For example, if you want to extract user stats per day in a `users_per_day` stream and session stats per day and country in a `sessions_per_country_day` stream:

```json
[
  { "name" : "users_per_day",
    "dimensions" :
    [
      "ga:date"
    ],
    "metrics" :
    [
      "ga:users",
      "ga:newUsers"
    ]
  },
  { "name" : "sessions_per_country_day",
    "dimensions" :
    [
      "ga:date",
      "ga:country"
    ],
    "metrics" :
    [
      "ga:sessions",
      "ga:sessionsPerUser",
      "ga:avgSessionDuration"
    ]
  }
]
```

### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set reports <path>

export TAP_GOOGLE_ANALYTICS_REPORTS=<path>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_GOOGLE_ANALYTICS_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-google-analytics set start_date 2020-10-01T00:00:00Z

export TAP_GOOGLE_ANALYTICS_START_DATE=2020-10-01T00:00:00Z
```

### End Date

- Name: `end_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GOOGLE_ANALYTICS_END_DATE`

Date up to when historical data will be extracted.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-google-analytics set end_date YYYY-MM-DDTHH:MM:SSZ

export TAP_GOOGLE_ANALYTICS_END_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-google-analytics set end_date 2020-10-01T00:00:00Z

export TAP_GOOGLE_ANALYTICS_END_DATE=2020-10-01T00:00:00Z
```
