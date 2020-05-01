---
metaTitle: Extracting Data with Meltano
description: Use Meltano to extract raw data from numerous sources including CSV, Google Analytics, Stripe, and more. 
---

# Data Sources (Extractors)

**E**xtracting data is the **E** in the term **ELT**. To pull data from your sources, Meltano uses Extractor plugins that are also known as [taps](/developer-tools/architecture.html#taps).

Meltano currently supports importing data from the following sources out of the box:

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

::: tip
If you don't see the extractor you need here, you can easily add any [existing Singer tap](https://www.singer.io/#taps) as a [custom extractor](/tutorials/create-a-custom-extractor.html#add-the-plugin-to-your-meltano-project-custom) or [create your own extractor from scratch](/tutorials/create-a-custom-extractor.html).
:::
