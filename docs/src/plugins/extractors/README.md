---
description: Use Meltano to easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using Singer taps.
---

# Sources (Extractors)

Meltano lets you easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using [Singer taps](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [extractor plugins](/docs/plugins.html#extractors).


Extractors for the following sources are currently [discoverable](/docs/plugins.html#discoverable-plugins) and supported out of the box:

- [BigQuery](/plugins/extractors/bigquery.html)
- [Bing Ads](/plugins/extractors/bing-ads.html)
- [Chargebee](/plugins/extractors/chargebee.html)
- [Comma Separated Values (CSV)](/plugins/extractors/csv.html)
- [Facebook Ads](/plugins/extractors/facebook.html)
- [Fastly](/plugins/extractors/fastly.html)
- [GitLab](/plugins/extractors/gitlab.html)
- [Google Ads](/plugins/extractors/adwords.html)
- [Google Analytics](/plugins/extractors/google-analytics.html)
- [Marketo](/plugins/extractors/marketo.html)
- [MongoDB](/plugins/extractors/mongodb.html)
- [MySQL / MariaDB](/plugins/extractors/mysql.html)
- [Quickbooks](/plugins/extractors/quickbooks.html)
- [PostgreSQL](/plugins/extractors/postgres.html)
- [ReCharge](/plugins/extractors/recharge.html)
- [Sage Intacct](/plugins/extractors/intacct.html)
- [Salesforce](/plugins/extractors/salesforce.html)
- [Shopify](/plugins/extractors/shopify.html)
- [Slack](/plugins/extractors/slack.html)
- [Spreadsheets Anywhere](/plugins/extractors/spreadsheets-anywhere.html) (CSV files and Excel spreadsheets on cloud or local storage)
- [Stripe](/plugins/extractors/stripe.html)
- [Zendesk](/plugins/extractors/zendesk.html)
- [Zoom](/plugins/extractors/zoom.html)

To learn more about extracting and [loading](/plugins/loaders/) data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

::: tip Don't see your data source listed here?

If a [Singer tap](https://www.singer.io/#taps) for your source already exists,
it can easily be [added to your project as a custom extractor](/docs/plugin-management.html#custom-plugins).
If not, you can learn how to [create your own from scratch](/tutorials/create-a-custom-extractor.html).

Once you've got the new extractor working in your project, please consider
[contributing its description](/docs/contributor-guide.html#discoverable-plugins)
to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
so that it can be added to this page!

:::
