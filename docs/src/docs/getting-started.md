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

Choose a data source to connect, fill in the form with your authentication details, and then save.

![Example of GitLab docs appearing next to configuration form](/images/getting-started-guide/gsg-02.png)

Once saved, we automatically start data extraction for you. The extraction time varies based on the data source and Start Date setting that you previously selected. Once complete you can click one of the related data model buttons from which to build reports.

![Example of GitLab extraction log and data model buttons](/images/getting-started-guide/gsg-03.png)

These buttons are also available via the **Reports** main navigation dropdown or via the **Data** page which now shows the corresponding data pipeline that was automatically created when you saved your connection.

![Example of GitLab data model buttons on data page](/images/getting-started-guide/gsg-03b.png)

Some of our popular data source connectors include:

- [Facebook Ads](/plugins/extractors/facebook.html)
- [Google Analytics](/plugins/extractors/google-analytics.html#google-analytics)
- [Stripe](/plugins/extractors/stripe.html#stripe)
- [Salesforce](/plugins/extractors/salesforce.html#salesforce)

See a [full list of data sources here](/plugins/).

## Analyze Your Data

Congratulations! Now that you have connected a data source, and run a successful pipeline for the dataset, we are now ready to analyze the data!

After clicking one of the aforementioned data model buttons, you will be on the **Analyze** page which contains an interactive user interface to allow you to dynamically build queries and visualize your data. By default, it will run a standard report.

You can explore and analyze the data by clicking on different Attributes in the **Query** side menu on the left hand side. Autorun is enabled by default to trigger live changes to the SQL queries which will update the chart dynamically.

![Screenshot of Analyze page for GitLab](/images/getting-started-guide/gsg-04.png)

While exploring the Analyze page, you can also modify:

- Date Ranges (upper right)
- Filters (upper left of Query panel)
- Different chart (upper right of Results panel)
- Exploring table data and sorting data via column properties like ascending or descending (bottom right)

## Create Reports

When we find an analysis that we want to reference in the future, we can easily do this by creating a report. This can be accomplished by clicking on the `Save Report` dropdown in the Analyze toolbar. This will open a dropdown with a default report name that is dynamically populated, but can be easily changed.

![Save Report dialogue for naming the report you want to save](/images/getting-started-guide/gsg-05.png)

Once we click `Save`, we should see the upper left "Untitled Report" change to our new report name.

![Saved report with a designated report name](/images/getting-started-guide/gsg-06.png)

And with that, our analysis has been saved!

## Create Dashboards

As you acquire more reports, you will probably want to organize them via dashboards. This can be done by clicking on the new `Add to Dashboard` dropdown in the toolbar.

![Dropdown menu for adding report to dashboard](/images/getting-started-guide/gsg-07.png)

Since we have never created a dashboard, click on `New Dashboard`, which will trigger a modal that contains a dynamically generated dashboard name that can be customized as desired.

![New dashboard dialog for configuring the dashboard](/images/getting-started-guide/gsg-08.png)

Once we click `Create`, we can now verify that our report has been added to the Dashboard by clicking on the `Add to Dashboard` menu.

![Confirmation that our report is added to the dashboard](/images/getting-started-guide/gsg-09.png)

We can also visit the Dashboard directly by clicking on the `Dashboard` navigation item in the header, which shows our newly created Dashboard.

![Dashboard page with newly created dashboard](/images/getting-started-guide/gsg-10.png)

Once we select it, you will see the dashboard you created. You can repeat the above process to add more reports to the same and/or different dashboards.

![Dashboard with the saved Report](/images/getting-started-guide/gsg-11.png)

## Share Reports and Dashboards

Once you've created reports and dashboards, you can share them publicly. Click the share dropdown at either the dashboard or report level. The share options for each are:

- Link (dedicated landing page)
- Embed (code snippet to embed in a website)

![Sharing reports and dashboards](/images/getting-started-guide/gsg-12.png)

## Choose Data Update Schedule

To keep your data updated, you can change the update interval of a particular data pipeline on the **Data** page. This is how you automate data collection. Additionally, your reports and the dashboards that contain them will be dynamically updated based off this fresh data.

![Changing update schedule](/images/getting-started-guide/gsg-13.png)

### Next Steps

Now you have now setup a complete end-to-end data analysis solution with Meltano! 🎉

To learn about more Meltano recipes and functionality with our [tutorials](/tutorials/).
