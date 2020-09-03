---
description: Use Meltano to easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using Singer taps.
---

# Extractors: Data Sources

Meltano lets you easily extract data out of arbitrary data sources (databases, SaaS APIs, and file formats) using [Singer taps](https://www.singer.io/), which take the role of [your project](/docs/project.html)'s [extractor plugins](/docs/plugins.html#extractors).

To learn more about extracting and [loading](/plugins/loaders/) data using Meltano, refer to the [Data Integration (EL) guide](/docs/integration.html).

Extractors for the following sources are currently [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box:

- [Bing Ads](/plugins/extractors/bing-ads.html)
- [Comma Separated Values (CSV)](/plugins/extractors/csv.html)
- [Facebook Ads](/plugins/extractors/facebook.html)
- [Fastly](/plugins/extractors/fastly.html)
- [GitLab](/plugins/extractors/gitlab.html)
- [Google Ads](/plugins/extractors/adwords.html)
- [Google Analytics](/plugins/extractors/google-analytics.html)
- [Marketo](/plugins/extractors/marketo.html)
- [MongoDB](/plugins/extractors/mongodb.html)
- [Salesforce](/plugins/extractors/salesforce.html)
- [Shopify](/plugins/extractors/shopify.html)
- [Spreadsheets Anywhere](/plugins/extractors/spreadsheets-anywhere.html) (Excel or CSVs on localhost or Cloud storage)
- [Stripe](/plugins/extractors/stripe.html)
- [Zendesk](/plugins/extractors/zendesk.html)

::: tip Don't see your data source listed here?

If a [Singer tap](https://www.singer.io/#taps) for your source already exists,
it can easily be [added to your project as a custom extractor](/docs/command-line-interface.html#how-to-use-custom-plugins).
If not, you can learn how to [create your own from scratch](/tutorials/create-a-custom-extractor.html).

Once you've successfully added a previously unknown extractor to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!

:::
