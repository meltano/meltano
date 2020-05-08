---
sidebar: auto
metaTitle: Extract Data from Google Analytics
description: Use Meltano to extract raw data from Google Analytics and insert it into Postgres, Snowflake, and more.
lastUpdatedSignificantly: 2020-04-14
---

# Google Analytics

The Google Analytics extractor pulls raw data from the [Google Analytics Reporting API](https://developers.google.com/analytics/devguides/reporting/core/v4/).

## Google Analytics Setup

In order to access your Google Analytics data, you will need:

- View ID
- Client Secrets
- Start Date

<div class="embed-responsive embed-responsive-16by9">
  <iframe
  width="560" height="315" src="https://www.youtube.com/embed/FON9ywXOcwM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

### View ID

To get your View ID:

1. Visit Google Analytics: <https://analytics.google.com/>
2. Log in if you haven't already.
3. Open the account/property/view selector in the top left corner

![Screenshot of closed account selector](/images/tap-google-analytics/account-selector-closed.png)

3. Select the account, property, and view that you would like to connect with Meltano

![Screenshot of open account selector](/images/tap-google-analytics/account-selector-open.png)

4. You will see the View ID displayed inside the selector below the name of the view (e.g. "All Web Site Data"): 188274549

<h3 id="key-file-location">Client Secrets</h3>

:::tip Configuration Notes

- Follow the steps below if you don't already have a valid `client_secrets.json` to upload
- The process below can take over 10 minutes, but it's a one-time setup that's well worth it

:::

This extractor supports service account based authorization, where an administrator manually creates a service account with the appropriate permissions to view the account, property, and view you wish to fetch data from.

To access your Google Analytics data, the "Analytics Reporting API" and "Analytics API" both need to be enabled. These need to be enabled for a project inside the same organization as your Google Analytics account.

#### Step 1: Creating Service Account Credentials

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

Meltano will use the private key in this `client_secrets.json` file to connect with the Google Analytics API. You will upload it in the Meltano interface after completing the next two steps.

#### Step 2: Linking Credentials to Google Analytics

The newly created service account will have an email address that looks similar to:

```
service-account-name@PROJECT-ID.iam.gserviceaccount.com
```

To grant this service account access to your Google Analytics data, add the email address as a [new user](https://support.google.com/analytics/answer/1009702) to your Google Analytics account, property or view through the "Admin > User Management" page.

Only the [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495) are needed as Meltano only extracts data to generate reports.

![Screenshot of Google Analytics Add User](/images/tap-google-analytics/03-ga-add-user.png)

#### Step 3: Enabling the APIs

1. Visit the [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) dashboard and make sure that the project you used in the previous step is selected.

   Now enable the API using the button at the top, so that the button will say "Disable API" instead:

   ![Screenshot of Google Analytics Reporting API](/images/tap-google-analytics/04-ga-reporting-api.png)

2. Next, visit the [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) dashboard, make sure that the project you used in the previous step is selected, and enable this API as well.

   ![Screenshot of Google Analytics API](/images/tap-google-analytics/05-ga-api.png)

#### Next Steps

Now it's time to tell Meltano about the newly created service account so that it can use it to connect to the Google Analytics API:

1. Click the "Upload" button to the right of "Client Secret" in the Meltano interface
2. Select and upload the `client_secrets.json` file you generated and downloaded in step 1

### Start Date

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

## Meltano Setup

### Prerequisites

- [Running instance of Meltano](/docs/installation.html#local-installation)

### Configuration

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data source.

Let's install `tap-google-analytics` by clicking on the `Connect` button inside its card.

For the **Client Secrets**, you will need to upload your `client_secrets.json` using the file uploader.

For the **View ID**, enter the ID you retrieved using [Google Analytics Account Explorer](https://ga-dev-tools.appspot.com/account-explorer/)

For the **Start Date**, choose the date when you want to start extracting data for.

Click `Save` to finish configuring the extractor and progress to the next step: "Configure the Loader".

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
