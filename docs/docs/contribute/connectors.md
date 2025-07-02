---
title: "Connectors"
description: Details the Meltano Connector Quality Standards
layout: doc
sidebar_position: 5
sidebar_class_name: hidden
---

## Connector Maintainers

- **Official** - Official connectors and tools are built, maintained, supported, and tested by Meltano.
- **Partner** - Partner connectors and tools are built, maintained, supported, and tested by a partner organization of Meltano, including consultancies and other vendors.
- **Community** - Community connectors and tools are built and maintained by the wider open source community.

## Connector Quality

- **Gold** - Connectors built on the Meltano SDK with high usage, and broad coverage of data and features.
- **Silver** - Connectors built on the Meltano SDK with low to medium usage, and connectors not built on the Meltano SDK with high usage.
- **Bronze** - Connectors not built on the Meltano SDK with low to medium usage.
- **No Data** - Connectors for which we have no usage data. These may be poorly tested or out of date, and repository maintainers may be unresponsive.

### Connector Quality Matrix

To give users a better understanding of the overall quality of a connector, we have the following matrix and guidance on attributes that affect the quality rating.

|         | SDK-Based | Usage Data    | Maintainer                      | Repo Responsiveness |
| ------- | --------- | ------------- | ------------------------------- | ------------------- |
| Gold    | Yes       | > 5 Projects  | Official, Partner, or Community | High                |
| Silver  | Possibly  | >= 1 Projects | Partner or Community            | Medium              |
| Bronze  | No        | >= 1 Projects | Community                       | Low                 |
| No Data | No        | Unknown       | Community                       | Unknown             |

For all connectors we may apply feedback we get from the community or our judgement to adjust the quality indicator of a connector.

Please reach out to us to learn more about Platinum-level support for Gold connectors.

**Are these connectors production ready?**

Gold connectors are production ready. Silver connectors are very likely production ready. Bronze connectors and connectors on which we have No Data could be production ready, but you'll want to assess this yourself, and modifications may be necessary.

One additional factor is what stage of development the connector is in. We recommend [semantic versioning](https://semver.org/) for connector development. If a connector is at v1.0.0 or greater, then it is considered production ready by its creator. For connectors between versions 0.1.0 and 1.0.0, they could be production ready and a number of users could be using them actively, but it is worth considering your own use case and whether it has the streams and features you need. If the connector is &lt;0.1.0 then it is still in development and likely not ready for production, but feedback and contributions are welcomed to make it so.

**Why is Silver the maximum rating for connectors not based on the Meltano SDK?**

Connectors that are not based on the Meltano SDK typically do not use all the features and performance optimizations available in the Singer specification and the SDK implementation thereof. Even if they have high usage, their quality and feature and data coverage are harder to assess, they will not benefit from future improvements to the Singer spec and SDK, and that they are significantly harder to maintain and contribute to.

**What are the criteria for a connector to be considered an Official, Partner, or Community connector?**

Please [reach out to us](https://arch.dev/contact/) for more information on how to become a Partner.

**How is the repository responsiveness determined and what does “High”, “Medium”, and “Low” mean in this context?**

We look at the recent activity on issues and pull requests on the repository to determine this. Typically low responsiveness means there hasn't been any activity for more than 6 months. High activity means there are responses within a week.

**Can a connector’s quality rating change over time, and if so, how often are they updated?**

Yes. We have automated checks to notify us of meaningful changes to the properties of a connector. Please [reach out to us](https://meltano.com/contact/) if you have a question or think a quality rating should change.

**How can I contribute to improving a connector’s quality rating or help maintain it?**

There are multiple ways to improve a connector's quality. Please [review this page](https://hub.meltano.com/tap-target-maintenance) to learn more about connector maintenance.

**Can I request a connector to be built or improved if it doesn’t meet my needs?**

Yes. Please [reach out to us](https://arch.dev/contact/) with your request.

## Platinum Connector Support

Meltano offers Platinum Connectors Support for many connectors.

To learn more about which connectors are Platinum Certified, please [reach out to the team](https://arch.dev/contact/).

### Platinum Certified Connector - Guarantees

Each Platinum Connector will have the following guarantees:

- Built with the Meltano SDK
- Open Source License
- Semantic Versioning used in all releases
- Daily integration testing
- Priority bug fixes
- Proactive API and changelog monitoring

For our Customers, we offer additional SLAs around our responsiveness and notifications for any problems with the connectors.
[Reach out to the team](https://arch.dev/contact/) to learn more.
