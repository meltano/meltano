---
description: Use Meltano to easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using Singer taps.
---

::: warning
This page is now deprecated and will be removed in the future.

View the current documentation on the [MeltanoHub](https://hub.meltano.com/extractors/)
:::

# Sources (Extractors)

Meltano lets you easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using [Singer taps](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [extractor plugins](/docs/plugins.html#extractors).


Extractors for the following sources are currently [discoverable](/docs/plugins.html#discoverable-plugins) and supported out of the box:

- [BigQuery](https://hub.meltano.com/extractors/bigquery.html)
- [Bing Ads](https://hub.meltano.com/extractors/bing-ads.html)
- [Chargebee](https://hub.meltano.com/extractors/chargebee.html)
- [Comma Separated Values (CSV)](https://hub.meltano.com/extractors/csv.html)
- [Facebook Ads](https://hub.meltano.com/extractors/facebook.html)
- [Fastly](https://hub.meltano.com/extractors/fastly.html)
- [GitLab](https://hub.meltano.com/extractors/gitlab.html)
- [Google Ads](https://hub.meltano.com/extractors/adwords.html)
- [Google Analytics](https://hub.meltano.com/extractors/google-analytics.html)
- [Marketo](https://hub.meltano.com/extractors/marketo.html)
- [MongoDB](https://hub.meltano.com/extractors/mongodb.html)
- [MySQL / MariaDB](https://hub.meltano.com/extractors/mysql.html)
- [PostgreSQL](https://hub.meltano.com/extractors/postgres.html)
- [Quickbooks](https://hub.meltano.com/extractors/quickbooks.html)
- [ReCharge](https://hub.meltano.com/extractors/recharge.html)
- [Sage Intacct](https://hub.meltano.com/extractors/intacct.html)
- [Salesforce](https://hub.meltano.com/extractors/salesforce.html)
- [Shopify](https://hub.meltano.com/extractors/shopify.html)
- [Slack](https://hub.meltano.com/extractors/slack.html)
- [Spreadsheets Anywhere](https://hub.meltano.com/extractors/spreadsheets-anywhere.html) (CSV files and Excel spreadsheets on cloud or local storage)
- [Stripe](https://hub.meltano.com/extractors/stripe.html)
- [Zendesk](https://hub.meltano.com/extractors/zendesk.html)
- [Zoom](https://hub.meltano.com/extractors/zoom.html)

To learn more about extracting and [loading](https://hub.meltano.com/loaders/) data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

::: tip Don't see your data source listed here?

If a [Singer tap](https://www.singer.io/#taps) for your source already exists,
it can easily be [added to your project as a custom extractor](/docs/plugin-management.html#custom-plugins).
If not, you can learn how to [create your own from scratch](/tutorials/create-a-custom-extractor.html).

Once you've got the new extractor working in your project, please consider
[contributing its description](/docs/contributor-guide.html#discoverable-plugins)
to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
so that it can be added to this page!

:::
