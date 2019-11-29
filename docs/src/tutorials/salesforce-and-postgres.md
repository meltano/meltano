---
sidebar: auto
metaTitle: Meltano Tutorial - Load Salesforce data into Postgres
description: Learn how to use Meltano to analyze your Salesforce data by automatically loading it into Postgres.
---

# Tutorial: Salesforce API + Postgres

In this tutorial we'll explain how to get the [Salesforce Extractor](https://gitlab.com/meltano/tap-salesforce) integrated with your Meltano project to pull your Salesforce data and load it into a Postgres analytics database.


## Prerequisites

For this tutorial, you can use a new or existing Meltano project. 

If you need help getting started, we recommend reviewing the [Installation documentation](/docs/installation.html) and [Getting Started Guide](/docs/getting-started.html) to set up your first project. 

If this is your first time using Salesforce with Meltano, you will need to enable access to Salesforce's API and get your Salesforce Security Token by following the instructions found in the [Salesforce Extractor documentation](/plugins/extractors/salesforce.html#salesforce-setup). 

## Setup the Salesforce Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and Salesforce Extractor highlighted](/images/salesforce-tutorial/01-salesforce-extractor-selection.png)

Let's install `tap-salesforce` by clicking on the `Install` button inside its card. 

On the configuration modal enter your username and password, the Security Token Salesforce extractor will use to connect to Salesforce, and the Start Date you want the extracted data set to start from.

![Screenshot of Salesforce Extractor Configuration](/images/salesforce-tutorial/02-salesforce-configuration.png)

## Setup the Postgres Loader

Click `Save` to finish configuring the extractor and progress to the next step, the Loaders page.

Click to `Install` Postgres and set the credentials for your local Postgres.

![Screenshot of Postgres Loader Configuration](/images/meltano-ui/target-postgres-configuration.png)

Information on how to install a Postgres Database on your local machine and configure the Postgres Loader can be found on [PostgresQL Database Tutorials](/plugins/loaders/postgres.html).

## Apply transformations as desired

With our extractor and loader configured, you should now see the following page:

![Screenshot of Transform page on Meltano webapp](/images/meltano-ui/transform-run-selected.png)

This page allows you to apply transformations to your data. We want to run the default transforms that come pre-bundled with Meltano for data fetched from Salesforce, so we are going to select `Run` and then click `Save`. 

If you'd like to learn more about how transforms work in Meltano, check out our [docs on Meltano transform](/docs/architecture.html#meltano-transform).

## Create a pipeline schedule

You should now be greeted with the Schedules page with a modal to create your first pipeline!

![Create pipeline modal for Salesforce Extractor](/images/salesforce-tutorial/03-salesforce-create-new-pipeline.png)

Pipelines allow you to create scheduled tasks through Apache Airflow. For example, you may want a recurring task that updates the database at the end of every business day.

In the current form, you will see:

- A pipeline **name** which has a default name that is dynamically generated, but can be easily changed if desired
- The **extractor** the pipeline will use, which should be `tap-salesforce`
- The **loader** the pipeline will use, which should be `target-postgres`
- Whether the **transform** step should be applied, which should be `run`
- The **interval** at which the pipeline should be run, which is set by default to be `@once`

All we need to do is click `Save` to start our new pipeline! The pipeline's log opens automatically and you can check the pipeline running and what Meltano does behind the scenes to extract and load the data. 

You should see a spinning icon that indicates that the pipeline is not completed. Once it's complete, the indicator will disappear and you should be able to see the final results of the extraction:

![Screenshot of run log of a completed pipeline for Salesforce Extractor](/images/salesforce-tutorial/04-salesforce-log-of-completed-pipeline.png)

Now that you have connected to Salesforce, configured the Postgres Loader, and run a successful pipeline for the dataset, you are now ready to analyze the data!

Click the Analyze button on the bottom right of the log modal and then select the option provided for the Salesforce Model.

![Screenshot of Analyze: Model options for Salesforce](/images/salesforce-tutorial/05-salesforce-model-selection.png)

Meltano Models provide a starting point to explore and analyze data for specific use cases. They are similar to templates with only what is relevant for each use case included.

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data.

Let's explore and analyze our Salesforce Opportunities data by selecting the following attributes in the left column:

- **Columns**
  - Stage
  - Opportunity Type
  - Lead Source
- **Aggregates**
  - Total Opportunities
  - Average Probability (%)
  - Average Amount

![Screenshot of selected attributes for Salesforce Opportunities](/images/salesforce-tutorial/06-salesforce-opportunities-analyze-page-with-selected-attributes.png)

And with that, the big moment is upon us, it's time to click `Run` to run our query!

![Screenshot of bar graph for Salesforce Opportunities data](/images/salesforce-tutorial/07-salesforce-opportunities-bar-graph.png)

You should now see a bar chart visualization and a table below to see the data in detail.

Let's order the data by Average Amount descending:

![Screenshot of data and ordering for Salesforce Opportunities data](/images/salesforce-tutorial/08-salesforce-opportunities-ordering.png)

Let's say that we want to figure out which combination of Source and Opportunity Type results to the highest average amounts. We can filter the results to only include won opportunities. 

Select the `Filters` dropdown menu at the top of the Query pane and add a filter to only keep opportunities in the `Closed Won` Stage:

`Stage Name` --> `Equal to` --> `Closed Won`

![Screenshot of data and ordering for Salesforce Opportunities data](/images/salesforce-tutorial/09-salesforce-opportunities-filter.png)

Click `Add`, run the query and, finally, switch the graph to an area chart:

![Screenshot of area chart for Salesforce Opportunities data](/images/salesforce-tutorial/10-salesforce-opportunities-area-diagram.png)

In our example, we can see that the most valuable opportunities are new customers that are reffered by our partners.

## Save a report

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/salesforce-tutorial/11-salesforce-opportunities-save-report-dialogue.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/salesforce-tutorial/12-salesforce-opportunities-saved-report.png)

And with that, our analysis has been saved!

## Add a report to a dashboard

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/salesforce-tutorial/13-salesforce-opportunities-add-to-dashboard-dropdown.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/salesforce-tutorial/14-salesforce-opportunities-new-dashboard-dialog.png)

Once we click `Create`, we can now verify that the our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu. We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard and the associated Report.

![Dashboard page with new dashboard and the associated Report](/images/salesforce-tutorial/15-salesforce-dashboard-page.png)

## Next steps

And with that, you have now setup a complete end-to-end data solution for extracting and analyzing Salesforce data with Meltano! 🎉

You can now check the advanced Tutorial on how to [Create Custom Transformations and Models](/tutorials/create-custom-transforms-and-models.html) for your Salesforce data.

And don't forget to save the reports that you find useful and add reports to your dashboards. 
