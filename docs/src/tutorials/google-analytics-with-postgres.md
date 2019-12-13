---
sidebar: auto
metaTitle: Meltano Tutorial - Load Google Analytics data into Postgres
description: Learn how to use Meltano to load Google Analytics data into a Postgres database.
---

# Tutorial: Google Analytics API + Postgres

In this tutorial we'll explain how to get the [Google Analytics Extractor](https://gitlab.com/meltano/tap-google-analytics) integrated with your Meltano project to pull your Google Analytics data and load it into a Postgres analytics database.

<br />
<div class="embed-responsive embed-responsive-16by9">
  <iframe
  width="560" height="315" src="https://www.youtube.com/embed/AwZ5rRvqzf8" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## Prerequisites

For this tutorial, you can use a new or existing Meltano project.

If you need help getting started, we recommend reviewing the [Installation documentation](/docs/installation.html) and [Getting Started Guide](/docs/getting-started.html) to set up your first project.

If this is your first time using Google Analytics with Meltano, you will also need to:

1. Enable Google API access by following the instructions found in the [Google Analytics Extractor documentation](/plugins/extractors/google-analytics.html#google-analytics-setup).
2. [Install the Google Analytics extractor](/plugins/extractors/google-analytics.html#configuration)

## Setup the Postgres Loader

Once you save your Google Analytics extractor configuration settings, you should be greeted with the Loaders page. Click to `Install` Postgres and set the credentials for your local Postgres.

![Screenshot of Postgres Loader Configuration](/images/meltano-ui/target-postgres-configuration.png)

Information on how to install a Postgres Database on your local machine and configure the Postgres Loader can be found on [PostgresQL Database Tutorials](/plugins/loaders/postgres.html).

## Apply transformations as desired

With our extractor and loader configured, you should now see the following page:

![Screenshot of Transform page on Meltano webapp](/images/meltano-ui/transform-run-selected.png)

This page allows you to apply transformations to your data. We want to run the default transformations that come pre-bundled with Meltano for data fetched from Google Analytics, so we are going to select `Run` and then click `Save`.

If you'd like to learn more about how transformations work in Meltano, check out our documentation on [Meltano Transformations](/docs/architecture.html#meltano-transformations).

## Create a pipeline schedule

You should now be greeted with the Schedules page with a modal to create your first pipeline!

![Create pipeline modal for Google Analytics](/images/google-analytics-tutorial/04-ga-create-new-pipeline.png)

Meltano provides [Orchestration](/docs/orchestration.html) using Apache Airflow, which allows you to create scheduled tasks to run pipelines automatically.
For example, you may want a recurring task that updates the database at the end of every business day.

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
