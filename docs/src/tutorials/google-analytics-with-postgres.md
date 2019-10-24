---
sidebar: auto
---

# Tutorial: Google Analytics API + Postgres

For this tutorial, our goal will be to get [https://gitlab.com/meltano/tap-google-analytics](https://gitlab.com/meltano/tap-google-analytics) integrated with your Meltano project.

## Prerequisites

- Meltano
- GitLab account
- Basic command line knowledge

## Video Walkthrough

<p></p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/AwZ5rRvqzf8" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Meltano Setup

Let's start by initializing a new project! Navigate to your desired directory and run:

```bash
# Start a new Meltano project called google-analytics-tutorial
meltano init google-analytics-tutorial

# Once the setup is complete, navigate into your project
cd google-analytics-tutorial
```

## Google Analytics Setup

In order to access your Google Analytics data, `tap-google-analytics` needs:

1. The ID for the Google Analytics View you want to fetch data from.

   You can easily find it by using [Google Analytics Account Explorer](https://ga-dev-tools.appspot.com/account-explorer/).

   ![Screenshot of Google Analytics Account Explorer](/images/tap-google-analytics/01-ga-account-explorer.png)

2. Authorization to access your Google Analytics account.

   At the moment, `tap-google-analytics` supports service account based authorization, where an administrator manually creates a service account with the appropriate permissions to view the account, property, and view you wish to fetch data from.

   In order for `tap-google-analytics` to access your Google Analytics Account, it needs the Analytics Reporting API *and* the Analytics API enabled. These need to be enabled for a project inside the same organization as your Google Analytics account (check the next section for more details).

3. A way to authenticate when accessing the Analytics APIs

   When you create a service account Google gives you a json file with that service account's credentials called the `client_secrets.json`, and that's all you need to pass to this tap.

#### Creating service account credentials

If you already have a valid `client_secrets.json` for a service account, you can skip the rest of this section.

As a first step, you need to create or use an existing project in the Google Developers Console:

1. Sign in to the Google Account you are using for managing Google Analytics (you must have Manage Users permission at the account, property, or view level).

2. Open the [Service accounts page](https://console.developers.google.com/iam-admin/serviceaccounts). If prompted, select a project or create a new one to use for accessing Google Analytics.

3. Click Create service account.

   In the Create service account window, type a name for the service account, and select Furnish a new private key. Then click Save and store it locally in your `google-analytics-tutorial` directory as `client_secrets.json`.

   If you already have a service account, you can generate a key by selecting 'Edit' for the account and then selecting the option to generate a key.

![Screenshot of Google Service Account Configuration](/images/tap-google-analytics/02-ga-service-account-configuration.png)

Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. You are responsible for storing it securely.

#### Add service account to the Google Analytics account

The newly created service account will have an email address that looks similar to:

```
quickstart@PROJECT-ID.iam.gserviceaccount.com
```

Use this email address to [add a user](https://support.google.com/analytics/answer/1009702) to the Google analytics view you want to access via the API. For using `tap-google-analytics` only [Read & Analyze permissions](https://support.google.com/analytics/answer/2884495) are needed.

![Screenshot of Google Analytics Add User](/images/tap-google-analytics/03-ga-add-user.png)


#### Enable the APIs

1. Visit the [Google Analytics Reporting API](https://console.developers.google.com/apis/api/analyticsreporting.googleapis.com/overview) dashboard and make sure that the project you used in the `Create credentials` step is selected.

   From this dashboard, you can enable/disable the API for your account, set Quotas and check usage stats for the service account you are using with `tap-google-analytics`.

   ![Screenshot of Google Analytics Reporting API](/images/tap-google-analytics/04-ga-reporting-api.png)

2. Visit the [Google Analytics API](https://console.developers.google.com/apis/api/analytics.googleapis.com/overview) dashboard, make sure that the project you used in the `Create credentials` step is selected and enable the API for your account.

   ![Screenshot of Google Analytics API](/images/tap-google-analytics/05-ga-api.png)


## Setup the Google Analytics Extractor

With `client_secrets.json` downloaded, you are now set to run Meltano UI and start extracting data from your Google Analytics Account.

```bash
# Start Meltano UI
meltano ui
```

You should see now see the Extractors page, which contains various options for connecting your data source.

![Screenshot of Meltano UI with all extractors not installed and Google Analytics highlighted](/images/google-analytics-tutorial/01-ga-extractor-selection.png)

Let's install `tap-google-analytics` by clicking on the `Install` button inside its card. 

On the configuration modal enter the View ID you retrieved using [Google Analytics Account Explorer](https://ga-dev-tools.appspot.com/account-explorer/) and the start date you want to extract data for. If you leave the end date empty, `tap-google-analytics` sets it to yesterday. 

![Screenshot of Google Analytics Extractor Configuration](/images/google-analytics-tutorial/02-ga-configuration.png)

Click `Save` to finish configuring the extractor and progress to the next step: "Entity Selection".

## Select entities

Data sources can contain a lot of different entities. As a result, you might not want Meltano to pull every data source into your dashboard. As you can see on your screen, all of the entities are currently selected by default for `tap-google-analytics`.

![Screenshot of Google Analytics Extractor Entity Selection](/images/google-analytics-tutorial/03-ga-entity-selection.png)

We want to select all the default Entities (reports in the case of Google Analytics) that Meltano extracts, so click `Save` to finish configuring our extractor.

## Setup the Postgres Loader

Once you save your entities, you should be greeted with the Loaders page. Click to `Install` Postgres and set the credentials for your local Postgres.

![Screenshot of Postgres Loader Configuration](/images/meltano-ui/target-postgres-configuration.png)

Information on how to install a Postgres Database on your local machine and configure the Postgres Loader can be found on [PostgresQL Database Tutorials](/plugins/loaders/postgres.html).

## Apply transformations as desired

With our extractor and loader configured, you should now see the following page:

![Screenshot of Transform page on Meltano webapp](/images/meltano-ui/transform-run-selected.png)

This page allows you to apply transformations to your data. We want to run the default transforms that come pre-bundled with Meltano for data fetched from Google Analytics, so we are going to select `Run` and then click `Save`. 

If you'd like to learn more about how transforms work in Meltano, check out our [docs on Meltano transform](/docs/architecture.html#meltano-transform).

## Create a pipeline schedule

You should now be greeted with the Schedules page with a modal to create your first pipeline!

![Create pipeline modal for Google Analytics](/images/google-analytics-tutorial/04-ga-create-new-pipeline.png)

Pipelines allow you to create scheduled tasks through Apache Airflow. For example, you may want a recurring task that updates the database at the end of every business day.

In the current form, you will see:

- A pipeline **name** which has a default name that is dynamically generated, but can be easily changed if desired
- The **extractor** the pipeline will use, which should be `tap-google-analytics`
- The **loader** the pipeline will use, which should be `target-postgres`
- Whether the **transform** step should be applied, which should be `run`
- The **interval** at which the pipeline should be run, which is set by default to be `@once`

All we need to do is click `Save` to start our new pipeline! The pipeline's log opens automatically and you can check the pipeline running and what Meltano does behind the scenes to extract and load the data. 

You should see a spinning icon that indicates that the pipeline is not completed. Once it's complete, the indicator will disappear and you should be able to see the final results of the extraction:

![Screenshot of run log of a completed pipeline for Google Analytics](/images/google-analytics-tutorial/05-ga-log-of-completed-pipeline.png)

Congratulations! Now that you have connected to Google Analytics, configured the Postgres Loader, and run a successful pipeline for the dataset, we are now ready to analyze the data!

## Select a data model

Let's start by closing the Run Log for the pipeline and click on the `Model` option on the header of the page. This should bring us to the "Analyze: Models" page:

![Screenshot of Analyze: Model page for Google Analytics](/images/google-analytics-tutorial/06-ga-model-page.png)

Meltano Models provide a starting point to explore and analyze data for specific use cases. They are similar to templates with only what is relevant for each use case included. As you can see in the right column, `tap-google-analytics` already has the required models installed.

Let's move on to the next step by clicking `Analyze` in the `Google analytics website overview` card to move on to the next step.

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data.

![Screenshot of Analyze page for Google Analytics](/images/google-analytics-tutorial/07-ga-website-overview-analyze-page.png)

Now, let's explore and analyze our `tap-google-analytics` data by selecting the following attributes in the left column:

- **Columns**
  - Year
  - Month
  - Day
- **Aggregates**
  - Total Users
  - Total Sessions

![Screenshot of selected attributes for Google Analytics](/images/google-analytics-tutorial/08-ga-website-overview-selected-attributes.png)

And with that, the big moment is upon us, it's time to click `Run` to run our query!

![Screenshot of bar graph for Google Analytics Website data](/images/google-analytics-tutorial/09-ga-website-overview-bar-graph.png)

You should now see a beautiful data visualization and a table below to see the data in detail!

Let's remove the Day so that we can see aggregate stats per month and order the data by Year and Month ascending:

![Screenshot of data and ordering for Google Analytics Website data](/images/google-analytics-tutorial/10-ga-website-overview-ordering.png)

And, finally, switch the graph to an area chart:

![Screenshot of area chart for Google Analytics Website data](/images/google-analytics-tutorial/11-ga-website-overview-area-diagram.png)


## Save a report

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/google-analytics-tutorial/12-ga-website-overview-save-report-dialogue.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/google-analytics-tutorial/13-ga-website-overview-saved-report.png)

And with that, our analysis has been saved!

## Add a report to a dashboard

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/google-analytics-tutorial/14-ga-website-overview-add-to-dashboard-dropdown.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/google-analytics-tutorial/15-ga-website-overview-new-dashboard-dialog.png)

Once we click `Create`, we can now verify that the our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu. We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard and the associated Report.

![Dashboard page with new dashboard and the associated Report](/images/google-analytics-tutorial/16-ga-dashboard-page.png)


## Next steps

And with that, you have now setup a complete end-to-end data solution for Google Analytics with Meltano! 🎉

You can now check the rest of the pre-bundled Models for Device, Location, Traffic Source Stats and more.

Don't forget to save the reports that you find useful and add reports to your dashboards. 

This is only a starting point: Google Analytics' API provides access to [hundreds of dimensions and metrics](https://ga-dev-tools.appspot.com/dimensions-metrics-explorer/). We are going to add an Advanced Tutorial soon with how to setup the Google Analytics Extractor to generate any report you may want, add custom Transforms for the extracted data and Custom Models to analyze the end results.
