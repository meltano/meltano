---
sidebar: auto
metaTitle: Meltano Tutorial - Load GitLab commit history into Postgres
description: Learn how to use Meltano to analyze your GitLab data by automatically loading it into Postgres.
---

# Tutorial: GitLab API + Postgres

For this tutorial, our goal will be to Extract data from GitLab using Meltano, Load the extracted data to a Postgres database, Transform the data and Analyze the final results.

We'll use [tap-gitlab](/plugins/extractors/gitlab.html) and demonstrate how to integrate it with your Meltano project.

## Prerequisites

- Meltano
- GitLab account
- Basic command line knowledge

## Video Walkthrough

<p></p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/AwZ5rRvqzf8" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Setup Meltano

Let's start by initializing a new project! Navigate to your desired directory and run:

```bash
# Start a new Meltano project called gitlab-tutorial
meltano init gitlab-tutorial

# Once the setup is complete, navigate into your project
cd gitlab-tutorial

# Start Meltano UI
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

## Setup the GitLab Extractor

You should see now see the Extractors page, which contains various options for connecting your data source.

![Screenshot of Meltano UI with all extractors not installed and GitLab Extractor highlighted](/images/gitlab-tutorial/01-gitlab-extractor-selection.png)

Let's install `tap-gitlab` by clicking on the `Install` button inside its card. 

On the configuration modal we want to enter the Private Token `tap-gitlab` will use to connect to GitLab, the Groups and Projects we are going to extract from and the Start Date we want the extracted data set to start from. 

![Screenshot of GitLab Extractor Configuration](/images/gitlab-tutorial/02-gitlab-configuration.png)

The following sections explain how to obtain and fill that information.

### GitLab API Token

In order to access GitLab's API to fetch data, we must get a personal access token that will authenticate you with the server. This is very simple to do:

<video controls style="max-width: 100%">
  <source src="/screenshots/personal-access-token.mov">
</video>

1. Navigate to your [profile's access tokens](https://gitlab.com/profile/personal_access_tokens).

2. Fill out the personal access token form with the following properties:

- **Name:** meltano-gitlab-tutorial
- **Expires:** _leave blank unless you have a specific reason to expire the token_
- **Scopes:**
  - api

3. Click on `Create personal access token` to submit your request.

4. You should see your token appear at the top of your screen.

5. Copy and paste the token into the `Private Token` field. It should look something like this: `I8vxHsiVAaDnAX3hA`

### Projects

This property allows you to scope the project that the service fetches, but it is completely optional. If this is left blank, the extractor will try to fetch all projects that it can grab.

If you want to configure this, the format for it is `group/project`. Here are a couple examples:

- `meltano/meltano` - The core [Meltano project](https://gitlab.com/meltano/)
- `meltano/tap-gitlab` - The project for the [GitLab Extractor](https://gitlab.com/meltano/tap-gitlab)

For this tutorial, we will scope our data sample to only include the Meltano project to make things faster. So we will now populate the `Projects` field as follows: `meltano/meltano`

### Groups

This property allows you to scope data that the extractor fetches to only the desired group(s). The group name can generally be found at the root of a repository's URL. If this is left blank, you have to at least provide a project.

For example, `https://www.gitlab.com/meltano/tap-gitlab` has a group of `Meltano`. This can be confirmed as well by visiting `https://gitlab.com/meltano` and noting the Group ID below the header.

![Group ID verification example](/screenshots/group-header-example.png)

For this tutorial, we will also scope the data to reduce the size of data being fetched. So we will configure the field `Groups` with the Meltano group: `meltano`

:::tip Configuration options for Groups and projects

- Either groups or projects need to be provided
- Filling in 'groups' but leaving 'projects' empty will sync all the projects for the provided group(s).
- Filling in 'projects' but leaving 'groups' empty will sync the specified projects.
- Filling in 'groups' and 'projects' will sync only the specified projects in those groups.

:::

### Start Date

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.

Similar to the previous examples, we will limit the scope of data being fetched in order to shorten the download time, so let's configure the start date to the beginning of last month, for example: `01/10/2019`


## Setup the Postgres Loader

Click `Save` to finish configuring the extractor and progress to the next step, the Loaders page.

Click to `Install` Postgres and set the credentials for your local Postgres.

![Screenshot of Postgres Loader Configuration](/images/meltano-ui/target-postgres-configuration.png)

Information on how to install a Postgres Database on your local machine and configure the Postgres Loader can be found on [PostgresQL Database Tutorials](/plugins/loaders/postgres.html).

## Apply transformations as desired

With our extractor and loader configured, you should now see the following page:

![Screenshot of Transform page on Meltano webapp](/images/meltano-ui/transform-run-selected.png)

This page allows you to apply transformations to your data. We want to run the default transforms that come pre-bundled with Meltano for data fetched from GitLab, so we are going to select `Run` and then click `Save`. 

If you'd like to learn more about how transforms work in Meltano, check out our [docs on Meltano transform](/docs/architecture.html#meltano-transform).

## Create a pipeline schedule

You should now be greeted with the Schedules page with a modal to create your first pipeline!

![Create pipeline modal for GitLab Extractor](/images/gitlab-tutorial/03-gitlab-create-new-pipeline.png)

Pipelines allow you to create scheduled tasks through Apache Airflow. For example, you may want a recurring task that updates the database at the end of every business day.

In the current form, you will see:

- A pipeline **name** which has a default name that is dynamically generated, but can be easily changed if desired
- The **extractor** the pipeline will use, which should be `tap-gitlab`
- The **loader** the pipeline will use, which should be `target-postgres`
- Whether the **transform** step should be applied, which should be `run`
- The **interval** at which the pipeline should be run, which is set by default to be `@once`

All we need to do is click `Save` to start our new pipeline! The pipeline's log opens automatically and you can check the pipeline running and what Meltano does behind the scenes to extract and load the data. 

You should see a spinning icon that indicates that the pipeline is not completed. Once it's complete, the indicator will disappear and you should be able to see the final results of the extraction:

![Screenshot of run log of a completed pipeline for GitLab Extractor](/images/gitlab-tutorial/04-gitlab-log-of-completed-pipeline.png)

Congratulations! Now that you have connected to GitLab, configured the Postgres Loader, and run a successful pipeline for the dataset, we are now ready to analyze the data!

## Select a data model

Let's start by closing the Run Log for the pipeline and click on the `Model` option on the header of the page. This should bring us to the "Analyze: Models" page:

![Screenshot of Analyze: Model page for GitLab](/images/gitlab-tutorial/05-gitlab-model-page.png)

Meltano Models provide a starting point to explore and analyze data for specific use cases. They are similar to templates with only what is relevant for each use case included. As you can see in the right column, `Gitlab` already has the required models installed.

Let's move on to the next step by clicking `Analyze` in the `Gitlab Issues` card to move on to the next step.

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data.

![Screenshot of Analyze page for GitLab](/images/gitlab-tutorial/06-gitlab-issues-analyze-page.png)

Now, let's explore and analyze our GitLab Issues data by selecting the following attributes in the left column:

- **Columns**
  - Created Year
  - Created Month
- **Aggregates**
  - Total Issues
  - Average Days to Close

![Screenshot of selected attributes for GitLab](/images/gitlab-tutorial/07-gitlab-issues-selected-attributes.png)

And with that, the big moment is upon us, it's time to click `Run` to run our query!

![Screenshot of bar graph for GitLab Issues data](/images/gitlab-tutorial/08-gitlab-issues-bar-graph.png)

You should now see a beautiful data visualization and a table below to see the data in detail!

Let's order the data by Year and Month ascending:

![Screenshot of data and ordering for GitLab Issues data](/images/gitlab-tutorial/09-gitlab-issues-ordering.png)

And filter the results to only include bugs:

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
