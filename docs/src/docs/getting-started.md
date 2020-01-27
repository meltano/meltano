---
metaTitle: Getting Started With Data Analysis
description: Create your first data analysis project, build a pipeline, and analyze your data after installing Meltano.
---

# Getting Started

Now that you have successfully installed Meltano [locally](/docs/installation.html) or [in the cloud](/docs/deployment.html), you're ready to start create your first project, connect data sources, build pipelines, perform analysis and create dashboards.

::: tip
The following instructions assume you are able to access Meltano's user interface locally from `http://localhost:5000` or at `http://YOUR_CLOUD_IP_ADDRESS:5000`.
:::

## Create your first project

To initialize a new project, open your terminal and navigate to the directory that you'd like to store your Meltano projects in.

Next, to create your project, you will use the `meltano init` command which takes a `PROJECT_NAME` that is of your own choosing. For this guide, let's create a project called "carbon."

::: info
Meltano shares anonymous usage data with the team through Google Analytics. This is used to help us learn about how Meltano is being used to ensure that we are making Meltano even more useful to our users.

If you would prefer to use Meltano without sending the team this data, learn how to configure this through our [environment variables docs](/docs/environment-variables.html#anonymous-usage-data).
:::

```bash
meltano init my-meltano-project
```

This will create a new directory named `my-meltano-project` in the current directory and initialize Meltano's basic directory structure inside it.

Inside the Meltano project directory, all plugin configuration (which may include tokens and passwords) is stored inside the `.meltano` directory,
which is automatically added to the project's `.gitignore` file to prevent this potentially sensitive information from accidentally being pushed up to a hosted Git repository.

## Start the application

Now that you've created your first Meltano project, let's change directory to our new project and start Meltano UI:

```bash
cd my-meltano-project
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

## Connect a data source

You should see now see the Extractors page, which contains various options for connecting your data source.

![Meltano UI with all extractors not installed initial loading screen](/images/getting-started-guide/gsg-01.png)

Go ahead and select the data source you're interested in connecting to Meltano. If you need assistance configuring your data source, you should see documentation to help you with this.

![Example of Stripe docs appearing next to configuration form](/images/getting-started-guide/gsg-02.png)

Some of our popular taps include:

- [Google Analytics](/plugins/extractors/google-analytics.html#google-analytics)
- [Stripe](/plugins/extractors/stripe.html#stripe)
- [Salesforce](/plugins/extractors/salesforce.html#salesforce)

## Choose how often your data is updated

By default, Meltano assumes you will be using a PostgreSQL instance that is already configured for you on your DigitalOcean instance. 

::: info 
If you are working with your own Meltano instance, You can follow [these instructions](https://www.meltano.com/plugins/loaders/postgres.html#postgresql-database) to make sure your PostgreSQL instance is setup correctly.
:::

As a result, all we need to do now it select how often we want our data to update. On the right hand side of your Data page, choose your desired interval and then click on `Save`.

::: info 
Meltano provides [Orchestration](/docs/orchestration.html) using Apache Airflow, which allows you to create scheduled tasks to run pipelines automatically.
For example, you may want a recurring task that updates the database at the end of every business day.
:::

Once your pipeline is setup, you will see your Data page update with a Pipelines section.

![Screenshot of Pipelines section on Data page](/images/getting-started-guide/gsg-03.png)

Once it's complete, the indicator will disappear and you should be able to see the final results of the extraction:

![Screenshot of run log of a completed pipeline](/images/getting-started-guide/gsg-04.png)

You can click the `Analyze` button to [select a model to analyze](#analyze-the-data). The same `Analyze` button is available inline within your pipeline. If you close the log and go back to the Pipelines page you can check the log of any past pipeline by clicking the `Log` button next to it:

Congratulations! Now that you have connected a data source, and run a successful pipeline for the dataset, we are now ready to analyze the data!

## Analyze the data

The Analyze page contains an interactive user interface to allow you to dynamically build queries and visualize your data. By default, it will run a standard report.

![Screenshot of Analyze page for Carbon Region](/images/getting-started-guide/gsg-10.png)

Now, you can explore and analyze the data by clicking on different Attributes in the **Query** side menu on the left hand side. This will trigger live changes to the SQL queries which will update the chart dynamically.

While exploring the Analyze page, you can also check out:

- Filters
- Different chart types which can be found in the upper right
- Exploring table data and sorting data via column properties like ascending or descending

## Save a report

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/getting-started-guide/gsg-11.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/getting-started-guide/gsg-12.png)

And with that, our analysis has been saved!

## Add a report to a dashboard

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/getting-started-guide/gsg-13.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/getting-started-guide/gsg-14.png)

Once we click `Create`, we can now verify that our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu.

![Confirmation that our report is added to the dashboard](/images/getting-started-guide/gsg-15.png)

We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard.

![Dashboard page with newly created dashboard](/images/getting-started-guide/gsg-16.png)

Once we select it, you should see a similar page to below:

![Dashboard with the saved Report](/images/getting-started-guide/gsg-17.png)

## Next steps

And with that, you have now setup a complete end-to-end data solution with Meltano! 🎉

To learn about more Meltano recipes and functionality with our [tutorials](/tutorials/).
