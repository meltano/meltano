---
description: Various data consultants have adopted Meltano and Singer as part of the stack they offer to clients.
---

# Partners

This page lists [consulting firms](#consulting-firms) that can help you take Meltano and Singer into production,
[maintainers of connectors](#connector-maintainers) that are supported out of the box, and
[data products](#data-products) that use Meltano to offer built-in data integration.

## Consulting firms

Meltano and [Singer](https://www.singer.io/) are [popular with data consultants](/docs/#focus), and various consulting firms have adopted both as part of the stack they offer to clients.

If you lack the time and/or expertise to do so yourself, they can help you
[set up](/docs/getting-started.html) your pipelines, deploy them to [production](/docs/production.html),
[improve](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin) existing Singer taps and targets to fit your use case,
and [build new ones](/tutorials/create-a-custom-extractor.html) for any [sources](/plugins/extractors/) and [destinations](/plugins/loaders/)
that are not supported yet.

More active [contributors](/docs/contributor-guide.html) to Meltano and [related open source projects](https://gitlab.com/meltano) are listed first:

| Consulting Firm | Locations | Contributions |
| --------------- | --------- | ------------- |
| [Slalom](https://www.slalom.com/) | United States: [various](https://www.slalom.com/locations); Canada: Montréal, Toronto, Vancouver; United Kingdom: London, Manchester; Australia: Melbourne, Sydney; Japan: Tokyo | [10+](https://gitlab.com/groups/meltano/-/merge_requests?author_username=aaronsteers&state=all) |
| [Applied Labs](https://appliedlabs.io/) | United States: New York; Russia: Moscow; United Kingdom: London; Uzbekistan: Tashkent | 5+ ([1](https://gitlab.com/groups/meltano/-/merge_requests?author_username=kaboomdev&state=all), [2](https://gitlab.com/groups/meltano/-/merge_requests?author_username=dmitry-stadnik&state=all)) |
<<<<<<< HEAD
| [Mashey](https://www.mashey.com/) | United States: Denver, CO | [1](https://gitlab.com/meltano/meltano/-/issues/2614), [2](https://gitlab.com/meltano/meltano/-/merge_requests/2074/diffs) |
| [AMEND](https://amendllc.com/) | United States: Cincinnati, OH |
| [b.telligent](https://www.btelligent.com/) | Germany: Berlin, Düsseldorf, Frankfurt, Hamburg, Hannover |
| [Commencis](https://www.commencis.com/) | Turkey: Istanbul; United Kingdom: London |
| [Datateer](https://www.datateer.com/) | United States: Denver, CO |
| [Ryan-Miranda](https://www.ryan-miranda.com/) | United States: Pasadena, CA; Boston, MA |
| [Wheelhouse](https://www.wheelhousedmg.com/) | United States: Seattle, WA; Richmond, VA |

::: tip Don't see your consulting firm listed here?

If you have experience with Meltano and Singer, you can add your company to this page by [viewing the source](https://gitlab.com/meltano/meltano/-/blob/master/docs/src/partners/README.md) and submitting a change using a [merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html).

:::

## Connector maintainers

Any [Singer](https://www.singer.io/) tap or target can be used with Meltano as a [custom plugin](/docs/plugin-management.html#custom-plugins),
but [extractors](/docs/plugins.html#extractors) and [loaders](/docs/plugins.html#loaders) for various
[sources](/plugins/extractors/) and [destinations](/plugins/extractors/) are supported out of the box.

Their maintainers are:

| Maintainer | Connectors |
| ---------- | ---------- |
| Meltano community | 9 extractors, 3 loaders |
| [Stitch](https://www.stitchdata.com/) | 5 extractors, 1 loader |
| [Wise](https://wise.com/) | 2 extractors, 2 loaders |
| [Hotglue](https://hotglue.xyz/) | 3 extractors |
| [Data Mill](https://datamill.co/) | 2 loaders |
| [Adswerve](https://adswerve.com/) | 1 loader |
| [Andy Huynh](https://github.com/andyh1203) | 1 loader |
| [Anelen](https://anelen.co/) | 1 extractor |
| [Eric Simmerman](https://github.com/ets) | 1 extractor |
| [Mashey](https://www.mashey.com/) | 1 extractor |

::: tip Don't see your organization listed here?

If you maintain a connector that could be supported by Meltano out of the box, please [contribute its description](/docs/contributor-guide.html#discoverable-plugins) to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins) and you'll be added to this page!

:::

## Data products

Meltano is a great fit for data products that want to let their users directly connect their own sources to the platform,
since connectors for many [sources](/plugins/extractors/) and [destinations](/plugins/extractors/) are already available,
new connectors can be created easily, and connectors and pipelines can be configured programmatically.

These are some of the tools powered by Meltano:

- [Blotout](https://blotout.io)
- [Halosight](https://halosight.com)
- [Matatika](https://matatika.com)
- [Qualytics](https://qualytics.co)

::: tip Don't see your product listed here?

If your product is powered by Meltano, you can add your company to this page by [viewing the source](https://gitlab.com/meltano/meltano/-/blob/master/docs/src/partners/README.md) and submitting a change using a [merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html).

:::
