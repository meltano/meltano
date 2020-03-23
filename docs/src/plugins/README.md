---
metaTitle: Meltano Plugins, Extractors, and Loaders
description: Meltano Extractors and Loaders connect to external services to extract and load data for analysis.
sidebarDepth: 2
---

# Data Sources

To connect your data sources to Meltano you will use plugins called Extractors, which can be configured to pull data from the tools you use to conduct business every day.

Hosted Meltano accounts currently support extracting data from:

* [Facebook Ads](/plugins/extractors/facebook.html)
* [Google Ads](/plugins/extractors/adwords.html)
* [Google Analytics](/plugins/extractors/google-analytics.html)
* [Salesforce](/plugins/extractors/salesforce.html)
* [Stripe](/plugins/extractors/stripe.html)

::: tip
If you don't see the extractor you need here, we have a [tutorial for creating your extractor](/tutorials/create-a-custom-extractor.html). We are constantly working to build new extractors, and our current roadmap includes: Google Ads, Shopify and Segment as next on the list.
:::

#### Reporting Database

Meltano hosted accounts come with a pre-configured [Postgres](/plugins/loaders/postgres.html) database, which acts as the reporting database where all your extracted data from the sources above will live.
