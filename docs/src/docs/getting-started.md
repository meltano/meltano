# Getting Started

Now that you have successfully [installed Meltano](/docs/installation.html) and its requirements, you can create your first project.

## Create your first project

To initialize a new project, navigate to the directory that you'd like to contain your Meltano projects, and run this command, replacing `PROJECT_NAME` with whatever you would like your new project to be called:

```bash
meltano init PROJECT_NAME
```

This will create a new directory named `PROJECT_NAME` and initialize Meltano's basic directory structure inside it.

## Start the application

Now that you've created your first Meltano project, change to the new directory and start the Meltano UI:

```bash
cd PROJECT_NAME
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

You are now ready to add data sources, configure reporting databases, schedule updates and build dashboards!

## Connect a data source

You should see now see the Extractors page, which contains various options for connecting your data source.

![Meltano UI with all extractors not installed initial loading screen](/images/getting-started-guide/getting-started-01.png)

For this guide, we will be following the "Fast Path" to get you up and running as quickly as possible. So let's install `tap-carbon-intensity` by clicking on the `Install` button inside its card. Once it is complete, you should be greeted with the following modal:

![Modal confirmation that tap-carbon-intensity is installed, doesn't require configuration and allow you to progress to the next step](/images/getting-started-guide/getting-started-02.png)

Click `Next` to move on to the next step: "Entity Selection."

## Select entities

Data sources can contain a lot of different entities. As a result, you might not want Meltano to pull every data source into your dashboard. Currently, as you can see on your screen:

![Entity Selection Modal for tap-carbon-intensity](/images/getting-started-guide/getting-started-03.png)

All of the entities are currently selected by default for "tap-carbon-intensity." Since there are only a few available entities, let's leave it as is and click `Save` to finish configuring our extractor.

## Determine where the data will live

Once you save your entities, you should be greeted with the Loaders page:

![Loader page for Meltano project](/images/getting-started-guide/getting-started-04.png)

Now that Meltano is pulling data in from your data source(s), you need to choose where and in what format you would like that data stored.

Let's use `target-sqlite` for this project by clicking `Install` in its card.

Once it is finished installing, you will see that the following modal:

![Modal dialogue for successful SQLite installation](/images/getting-started-guide/getting-started-05.png)

By default, `target-sqlite` is configured with a database named `meltano` that can be customized if desired. For this guide however, let's just use the default name and click `Save`.

## Apply transformations as desired

With our extractor and loader configured, you should now see the following page:

![Screenshot of Transform page on Meltano webapp](/images/getting-started-guide/getting-started-06.png)

This page allows you to apply transformations to your data. This is not necessary for our current setup, but if you'd like to learn more about how transforms work in Meltano, check out our [docs on Meltano transform](/docs/architecture.html#meltano-transform).

By default, the Transform step is set to `Skip`, so all we need to is click `Save`.

## Create a pipeline schedule

You should now be greeted with the Schedules page with a modal to create your first pipeline!

![Create pipeline modal](/images/getting-started-guide/getting-started-07.png)

Pipelines allow you to create scheduled tasks through Apache Airflow. For example, you may want a recurring task that updates the database at the end of every business day.

In the current form, you will see:

- A pipeline **name** which has a default name that is dynamically generated, but can be easily changed if desired
- The **extractor** the pipeline will use, which should be `tap-carbon-intensity`
- The **loader** the pipeline will use, which should be `target-sqlite`
- Whether the **transform** step should be applied, which should be `skip`
- The **interval** at which the pipeline should be run, which is set by default to be `@once`
- Finally, there is a **catch-up date** to determine how far back to extract data, which should be `None` by default

All we need to do is click `Save` to start our new pipeline! You should see a spinning icon as well as a badge next to the "Pipeline" navigation element in the header.

![Screenshot of pipeline being run](/images/getting-started-guide/getting-started-08.png)

Once it's complete, these indicators will disappear and you should see:

![Screenshot of complete pipeline run](/images/getting-started-guide/getting-started-09.png)

Congratulations! Now that you have connected a data source, configured a target database, and run a successful pipeline for the dataset, we are now ready to analyze the data!

## Select a data model

Let's start by clicking on the `Analyze` button in our pipeline. This should bring us to the "Analyze: Models" page:

![Screenshot of Analyze: Model page](/images/getting-started-guide/getting-started-10.png)

Meltano Models determine how the data is defined and assists us with interactively generating SQL so that you can easily analyze and visualize your data. As you can see in the right column, `tap-carbon-intensity` already has the required models installed.

Let's move on to the next step by clicking `Analyze` in the `model-carbon-intensity-sqlite` card to move on to the next step.

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data.

![Screenshot of Analyze page for Carbon Region](/images/getting-started-guide/getting-started-11.png)

::: warning
Before we can analyze our data, let's confirm that the database being used is correct via the dropdown in the upper right. If it says `postgresql`, switch it to `sqlite`. This will eventually be detected automatically, but a necessity at the moment.
:::

Now, let's explore and analyze our `tap-carbon-intensity` data by selecting the following attributes in the left column:

- **Geographical Region**
  - Columns: Name
  - Aggregates: Count
- **Electricity Generation Sources**
  - Columns: ID
  - Aggregates: Average Percent (%)

![Screenshot of selected attributes for tap-carbon-intensity](/images/getting-started-guide/getting-started-12.png)

And with that, the big moment is upon us, it's time to click `Run` to run our query!

![Our query visualized as a bar graph!](/images/getting-started-guide/getting-started-13.png)

You should now see a beautiful data visualization and a table below to see the data in detail!

## Save a report

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/getting-started-guide/getting-started-14.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/getting-started-guide/getting-started-15.png)

And with that, our analysis has been saved!

## Add a report to a dashboard

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/getting-started-guide/getting-started-16.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/getting-started-guide/getting-started-17.png)

Once we click `Create`, we can now verify that the our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu.

![Confirmation that our report is added to the dashboard](/images/getting-started-guide/getting-started-18.png)

We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard and the associated Report.

![Dashboard page with new dashboard and the associated Report](/images/getting-started-guide/getting-started-19.png)

## Next steps

And with that, you have now setup a complete end-to-end data solution with Meltano! 🎉

To learn about more Meltano recipes and functionality with [Advanced Tutorials](/docs/tutorial.html).
