---
sidebar: auto
metaTitle: Meltano Tutorial - Load data from GitLab groups and projects into Postgres
description: Learn how to use Meltano to analyze your GitLab data by automatically loading it into Postgres.
lastUpdatedSignificantly: 2020-02-13
---

# Tutorial: GitLab API + Postgres

In this tutorial we'll explain how to get the [GitLab Extractor](https://gitlab.com/meltano/tap-gitlab) integrated with your Meltano project to pull your GitLab data and load it into a Postgres analytics database.

<br />
<div class="embed-responsive embed-responsive-16by9">
  <iframe
  width="560" height="315" src="https://www.youtube.com/embed/QLETNl_9bpc" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## Prerequisites

For this tutorial, you can use a new or existing Meltano project.

If you need help getting started, we recommend reviewing the [Installation documentation](/docs/installation.html) and [Getting Started guide](/docs/getting-started.html) to set up your first project.

If this is your first time using GitLab with Meltano, you will need to enable access to GitLab's API and get your GitLab Private Token by following the instructions found in the [GitLab Extractor documentation](/plugins/extractors/gitlab.html#private-token).

## Setup the Postgres Loader

Add the Postgres loader to your Meltano project through the command line:

```
meltano add loader target-postgres
```

Then setup your Postgres database by following [this tutorial](/plugins/loaders/postgres.html).

## Setup the GitLab Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and GitLab Extractor highlighted](/images/gitlab-tutorial/01-gitlab-extractor-selection.png)

Let's install `tap-gitlab` by clicking on the `Install` button inside its card.

On the configuration modal we want to enter the Private Token that GitLab extractor will use to connect to GitLab, the Groups and Projects we are going to extract from and the Start Date we want the extracted data set to start from.

![Screenshot of GitLab Extractor Configuration](/images/gitlab-tutorial/02-gitlab-configuration.png)

For this tutorial, we will scope our data sample to only include the Meltano project to make things faster.

- Populate `Project` with the Meltano project: `meltano/meltano`
- Set the `Start Date` to the beginning of last month, for example: `01/10/2020`

Once you click Save, your pipeline will kick off! And once that is complete, you can click on the Analyze button to choose the model you want to analyze!

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data.

![Screenshot of Analyze page for GitLab Issues](/images/gitlab-tutorial/06-gitlab-issues-analyze-page.png)

Now, let's explore and analyze our GitLab Issues data by selecting the following properties in the left column:

- **Columns**
  - Created Year
  - Created Quarter
- **Aggregates**
  - Total Issues
  - Average Days to Close

![Screenshot of selected properties for GitLab Issues](/images/gitlab-tutorial/07-gitlab-issues-selected-properties.png)

And with that, the big moment is upon us, it's time to click `Run` to run our query!

![Screenshot of bar graph for GitLab Issues data](/images/gitlab-tutorial/08-gitlab-issues-bar-graph.png)

You should now see a bar chart visualization and a table below to see the data in detail!

Let's order the data by Year and Quarter ascending:

![Screenshot of data and ordering for GitLab Issues data](/images/gitlab-tutorial/09-gitlab-issues-ordering.png)

We can also filter the results to only include bugs. Select the `Filters` dropdown menu at the top of the Query pane and add a filter to only keep issues with the `bug` label:

`Labels (for filtering)` --> `Like` --> `%bug%`

We add the percentages around the `bug` cause issues may have multiple labels and the `bug` label can be anywhere in that field.

![Screenshot of data and ordering for GitLab Issues data](/images/gitlab-tutorial/10-gitlab-issues-filter.png)

And, finally, switch the graph to an area chart:

![Screenshot of area chart for GitLab Issues data](/images/gitlab-tutorial/11-gitlab-issues-area-diagram.png)

## Save a report

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/gitlab-tutorial/12-gitlab-issues-save-report-dialogue.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/gitlab-tutorial/13-gitlab-issues-saved-report.png)

And with that, our analysis has been saved!

## Add a report to a dashboard

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/gitlab-tutorial/14-gitlab-issues-add-to-dashboard-dropdown.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/gitlab-tutorial/15-gitlab-issues-new-dashboard-dialog.png)

Once we click `Create`, we can now verify that the our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu. We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard and the associated Report.

![Dashboard page with new dashboard and the associated Report](/images/gitlab-tutorial/16-gitlab-dashboard-page.png)

## Next steps

And with that, you have now setup a complete end-to-end data solution for extracting and analyzing GitLab data with Meltano! 🎉

You can now check the rest of the pre-bundled Models for Projects, Merge Requests, Users and more.

Don't forget to save the reports that you find useful and add reports to your dashboards.
