---
sidebar: auto
metaTitle: Extract Data from Google Analytics
description: Use Meltano to extract raw data from Google Analytics and insert it into Postgres, Snowflake, and more.
---

# Google Analytics

The Google Analytics extractor pulls raw data from the [Google Analytics Reporting API](https://developers.google.com/analytics/devguides/reporting/core/v4/).

## Google Analytics Setup

In order to access your Google Analytics data, you will need:

1. The ID for the Google Analytics View you want to fetch data from.

   You can easily find it by using [Google Analytics Account Explorer](https://ga-dev-tools.appspot.com/account-explorer/).

   ![Screenshot of Google Analytics Account Explorer](/images/tap-google-analytics/01-ga-account-explorer.png)

2. Authorization to access your Google Analytics account.

   This extractor supports service account based authorization, where an administrator manually creates a service account with the appropriate permissions to view the account, property, and view you wish to fetch data from.

   To access your Google Analytics Account, it needs the Analytics Reporting API _and_ the Analytics API enabled. These need to be enabled for a project inside the same organization as your Google Analytics account (check the next section for more details).

3. A way to authenticate when accessing the Analytics APIs

   When you create a service account Google gives you a json file with that service account's credentials called the `client_secrets.json`, and that's all you need to pass to this tap.

### Creating Service Account Credentials

::: tip
If you have a valid `client_secrets.json` for a service account, you can skip this section.
:::

As a first step, you need to create or use an existing project in the Google Developers Console:

1. Sign in to the Google Account you are using for managing Google Analytics (you must have Manage Users permission at the account, property, or view level).

2. Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts). If prompted, select a project or create a new one to use for accessing Google Analytics.

3. Click "Create service account"

   In the Create service account window, type a name for the service account, and select Furnish a new private key. Then click Save and store it locally in your Meltano project directory as `client_secrets.json`.

   If you already have a service account, you can generate a key by selecting 'Edit' for the account and then selecting the option to generate a key.

![Screenshot of Google Service Account Configuration](/images/tap-google-analytics/02-ga-service-account-configuration.png)

Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. You are responsible for storing it securely.

### Linking Credentials to Google Analytics

The newly created service account will have an email address that looks similar to:

```
quickstart@PROJECT-ID.iam.gserviceaccount.com
```

Use this email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. Only [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495) are needed.

![Screenshot of Google Analytics Add User](/images/tap-google-analytics/03-ga-add-user.png)

### Enabling the APIs

1. Visit the [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) dashboard and make sure that the project you used in the previous step is selected.

   From this dashboard, you can enable/disable the API for your account, set Quotas and check usage stats for the service account you are using with the Google Analytics extractor.

   ![Screenshot of Google Analytics Reporting API](/images/tap-google-analytics/04-ga-reporting-api.png)

2. Visit the [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) dashboard, make sure that the project you used in the previous step is selected, and enable the API for your account.

   ![Screenshot of Google Analytics API](/images/tap-google-analytics/05-ga-api.png)

## Meltano Setup

### Prerequisites

- [Running instance of Meltano](/docs/getting-started.html)

### Configure the Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data source.

![Screenshot of Meltano UI with all extractors not installed and Google Analytics highlighted](/images/google-analytics-tutorial/01-ga-extractor-selection.png)

Let's install `tap-google-analytics` by clicking on the `Install` button inside its card. When it's finished loading, you should see a configuration modal appear.

For the **Key File Location**, you will need to upload your `client_secrets.json` into the `extract` folder of your Meltano project. This can be done via FTP or logging in through your terminal.

For the **View ID**, enter the ID you retrieved using [Google Analytics Account Explorer](https://ga-dev-tools.appspot.com/account-explorer/)

For the **Start Date**, choose the date when you want to start extracting data for.

For the **End Date**, it is set to yesterday by default if you do not configure a date. However, you can choose to set a specific end date for your data set if you want.

![Screenshot of Google Analytics Extractor Configuration](/images/google-analytics-tutorial/02-ga-configuration.png)

Click `Save` to finish configuring the extractor and progress to the next step: "Configure the Loader".

::: tip

**Ready to do more with data from Google Analytics?**

Check out our [Google Analytics API + Postgres tutorial](/tutorials/google-analytics-with-postgres.html#select-a-data-model) to learn how you can create an analytics database from within Meltano, and start analyzing your Google Analytics data.

:::

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-google-analytics
```

If you are successful, you should see `Added and installed extractors 'tap-google-analytics'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

Required:

```bash
export GOOGLE_ANALYTICS_API_CLIENT_SECRETS="client_secrets.json"
export GOOGLE_ANALYTICS_API_VIEW_ID="YOUR VIEW ID"
export GOOGLE_ANALYTICS_API_START_DATE="2019-02-01T00:00:00Z"
```

Optional:

```bash
export GOOGLE_ANALYTICS_API_REPORTS="cli_reports.json"
export GOOGLE_ANALYTICS_API_END_DATE="2019-06-01T00:00:00Z"
```

Check the [README](https://gitlab.com/meltano/tap-google-analytics#tap-google-analytics) for details.
