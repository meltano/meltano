---
metaTitle: Extracting Data with Meltano
description: Use Meltano to extract raw data from numerous sources including CSV, Google Analytics, Stripe, and more.
---

# Extractors: Data Sources

**E**xtracting data is the **E** in the term **ELT**. To pull data from your sources, Meltano uses Extractor plugins that are also known as [taps](/docs/architecture.html#taps).

The following extractors are currently [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box on both the [CLI](/docs/command-line-interface.html#add) and [UI](/docs/analysis.html#set-up-meltano):

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
- [Stripe](/plugins/extractors/stripe.html)
- [Zendesk](/plugins/extractors/zendesk.html)

**Please note, all trademarks and logos are owned by their respective owners.**

::: tip Don't see your data source here?
You can easily add [any existing Singer tap](https://www.singer.io/#taps) as a [custom extractor](/docs/command-line-interface.html#how-to-use-custom-plugins) or [create your own from scratch](/tutorials/create-a-custom-extractor.html).

Don't forget to make your new plugin [known to Meltano](/docs/contributor-guide.html#known-plugins) if you'd like to make it available to other people!
:::
