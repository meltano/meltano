---
metaTitle: Getting Started With Data Analysis
description: Create your first data analysis project, build a pipeline, and analyze your data after installing Meltano.
---

# Getting Started

::: tip
We recommend using Meltano as hosted software (SaaS), but if you prefer to host Meltano yourself please see our [open source installation instructions](/developer-tools/self-hosted-installation.html).
:::

## Create Your Account

To create your Meltano account [fill out the signup form](https://meltano.typeform.com/to/NJPwxv) and we will email you login information.

<a href="https://meltano.typeform.com/to/NJPwxv" class="button is-purple is-filled">Get started with your free hosted Meltano dashboard</a>

## Connect Data Sources

Once you've logged into Meltano, you'll begin on the **Data** page to connect your [data sources](/plugins/).

![Meltano UI with all extractors not installed initial loading screen](/images/getting-started-guide/gsg-01.png)

Choose a data source to connect, and fill in the form with your authentication details.

![Example of Stripe docs appearing next to configuration form](/images/getting-started-guide/gsg-02.png)

Some of our popular data source connectors include:

- [Google Analytics](/plugins/extractors/google-analytics.html#google-analytics)
- [Stripe](/plugins/extractors/stripe.html#stripe)
- [Salesforce](/plugins/extractors/salesforce.html#salesforce)

See a [full list of data sources here](/plugins/).

## Choose Data Update Schedule

Now that you've connected a data source, you can select how often we want your data to update. On the right hand side of your **Data** page, choose your desired interval and then click on `Save`.

The pipeline will begin running, and Meltano will provide a modal with a live log showing you what is happening behind the scenes:

![Screenshot of run log of a completed pipeline](/images/getting-started-guide/gsg-04.png)

::: tip
You can close this modal at anytime, and the pipeline will continue to run.
:::

Once the pipeline has finished running, the indicator will disappear and you'll see the final results of the data extraction. You will also see your **Data** page update with a **Pipelines** section.

![Screenshot of Pipelines section on Data page](/images/getting-started-guide/gsg-03.png)

## Analyze Your Data

Congratulations! Now that you have connected a data source, and run a successful pipeline for the dataset, we are now ready to analyze the data!

Click `Reports` next to your newly created pipeline to visualize the data from your source.

The **Analyze** page contains an interactive user interface to allow you to dynamically build queries and visualize your data. By default, it will run a standard report.

![Screenshot of Analyze page for Carbon Region](/images/getting-started-guide/gsg-10.png)

Now, you can explore and analyze the data by clicking on different Attributes in the **Query** side menu on the left hand side. This will trigger live changes to the SQL queries which will update the chart dynamically.

While exploring the Analyze page, you can also check out:

- Filters
- Different chart types which can be found in the upper right
- Exploring table data and sorting data via column properties like ascending or descending

## Create Reports

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/getting-started-guide/gsg-11.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/getting-started-guide/gsg-12.png)

And with that, our analysis has been saved!

## Create Dashboards

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

### Next Steps

Now you have now setup a complete end-to-end data analysis solution with Meltano! 🎉

To learn about more Meltano recipes and functionality with our [tutorials](/tutorials/).
