---
description: Learn where to use Meltano, how Meltano is built, and where to get started.

members:
- name: Douwe Maan
  title: General Manager
  location: Mexico City, Mexico 🇲🇽
  gravatar_hash: 73d1548ae618321220679b3a4fda7fb1 # md5(email)
  social:
    gitlab: DouweM
    twitter: DouweM
    linkedin: douwem
- name: Taylor Murphy
  title: Head of Product & Data
  location: Nashville, TN, USA 🇺🇸
  gravatar_hash: b4936f876b1093f90d7246b264084ddd
  social:
    gitlab: tayloramurphy
    twitter: tayloramurphy
    linkedin: tayloramurphy
- name: AJ Steers
  title: Head of Engineering
  location: Seattle, WA, USA 🇺🇸
  gravatar_hash: 80b61ad103a8d9fd989893b757b15dac
  social:
    gitlab: aaronsteers
    twitter: aaronsteers
    linkedin: aaronsteers
---

# Introduction

[Meltano](https://meltano.com) is ELT for the DataOps era:
[open source](https://gitlab.com/meltano/meltano),
[self-hosted](/docs/production.html),
[CLI-first](/docs/command-line-interface.html),
[debuggable](/docs/command-line-interface.html#debugging), and
[extensible](/docs/plugins.html).

This page covers the project's [Mission](#mission), [Focus](#focus), [Roadmap](#roadmap), and [History](#history).

To find guides and references on other topics, use the Table of Contents in the sidebar.

## Mission

Our mission is to enable every organization to make the
best decisions possible by becoming data-informed.

To achieve this mission we are building an **open source platform for the complete DataOps lifecycle**
that is optimized for the happiness and productivity of Data Teams and Data Professionals.
It integrates best-in-class [open source components](/docs/plugins.html) and
enables teams to collaborate on data projects and pipelines more efficiently and with higher confidence.

Our focus has been on bringing these qualities to the first step in any data journey:
integration and transformation, aka EL(T): [Extract, Load, Transform](https://en.wikipedia.org/wiki/Extract,_load,_transform),
where traditional solutions are either off-the-shelf and near-impossible to extend, tweak, and debug,
or fully custom and a pain to maintain.

We believe that [data integration is ripe for commoditization](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/),
and are building towards a future in which fast and reliable **open source connectors
for every data source and destination** in the world will be freely available,
collectively maintained by a community of data engineers in consulting and at in-house data teams,
and by API vendors themselves, just like we see with API client libraries today.

### Embracing Singer

To make this a reality, we have embraced [Singer](https://www.singer.io/)
and are committed to providing its community and ecosystem with all of the tools and support
needed for it to realize its full potential as the **de-facto standard for open source connectors**,
to be used with Meltano or any other tool that supports them.

To further support the community and ecosystem, we have launched the [MeltanoHub for Singer](https://hub.meltano.com/singer/).
This is the Singer equivalent of [PyPI](https://pypi.org/) or [Docker Hub](https://hub.docker.com/),
to give users (and tools) a **central place to learn** about the behavior, supported features,
and maintenance status of **all taps and targets in the ecosystem**,
which are currently scattered across Git repos and PyPI packages.
As we continue to develop and enhance the [MeltanoHub](https://gitlab.com/groups/meltano/-/epics/83)
we will encourage decentralized maintenance of connectors
to prevent individual organizations from becoming bottlenecks as the ecosystem grows,
and will support the adoption of abandoned connectors by new maintainers.

With Meltano, we are providing a **clear path to production** with existing Singer taps and targets where there wasn't one before,
thereby lowering the barrier to adoption and motivating people who run into an issue with an existing connector
to debug it, contribute a fix, and see it through, instead of giving up.
Meltano's index of discoverable [extractors](https://hub.meltano.com/extractors/) and [loaders](https://hub.meltano.com/loaders/) will grow as the
number of [Singer Taps and Targets grows](https://hub.meltano.com/singer/).

In addition to the MeltanoHub, the [**SDK for Singer Taps and Targets**](https://sdk.meltano.com) enables
developers to build **connectors with all the bells and whistles** without having to be become an expert on the spec.
This further lowers the barrier to creating new connectors and contributing to existing ones,
and will lead to increased reliability and consistency.

We've also [created an interpretation of the Singer specification](https://hub.meltano.com/singer/spec)
that aims to be clearer for newcomers to the project. We believe the spec is great in its current version, but
confusing documentation has made it challenging for some to onboard to the community.

Last but not least, we intend to **[**unlock the evolution**](https://gitlab.com/groups/meltano/-/epics/88) of the
[**Singer spec**](https://hub.meltano.com/singer/spec)** through
a framework for the proposal and consideration of optional extensions to the spec
that compatible tools, including the SDK and Meltano, can choose to support,
while maintaining compatibility between all taps and targets.

## Focus

As described above, our vision for ELT in the DataOps era involves
a decentralized ecosystem of open source connectors and
a community of data engineers maintaining and contributing to these projects.

To make this happen, we are primarily focused on users and teams
that have the potential and the necessary technical skills to become
**active participants in this community**,
rather than those who prefer a hands-off approach with off-the-shelf connectors maintained by a single (paid) provider.

In order of priority, our target personas are:

1. **Data consultants** who may become [implementation partners](/partners/)
   - They frequently write one-off (Python) scripts to extract data from niche sources that aren't supported by commercial EL(T) vendors.
   - They want to stop reinventing the wheel and standardize their approach to building reliable and reusable custom connectors.
   - They are willing to open source their custom connectors to share the maintenance burden with the community and,
      in return, get access to connectors built and maintained by other consulting firms and data engineers.
   - They want a consistent approach to extracting data from common sources (that are supported by commercial vendors) and niche ones (that aren't).
   - They want the ability to customize and fix bugs in connectors without having to wait on a vendor.
   - They want to save their clients money by self-hosting pipelines instead of being beholden to vendor pricing.
   - They want to give their clients the option of never having their sensitive data pass through systems out of their control for privacy or compliance reasons.
   - They want to manage their data projects like any other software engineering project, with all of the benefits of version control and CI/CD.
   - They want to offer clients a (whitelabel) web UI to set up their connections and manage their pipelines.
2. **Data engineers** with a software development background
   - They are comfortable using a CLI and want to manage their data project like any other software engineering project, with all of the benefits of version control and CI/CD.
   - They recognize that connectors are like API client libraries, and are comfortable using open source options even if they may require some tweaking and contributing fixes upstream.
   - They want a consistent approach to extracting data from common sources (that are supported by commercial vendors) and niche ones (that aren't).
   - They want the ability to customize and fix bugs in connectors without having to wait on a vendor.
   - They may not want their sensitive data to pass through systems out of their control for privacy or compliance reasons.
   - They may want to extract data from region-specific sources and SaaS tools that are not supported by the US-centric commercial vendors.
   - They may have more development time to spend than money and would rather build and contribute to connectors than pay an expensive vendor.
3. Developers of **data products**
   - They want to let their users connect sources directly to their product.
   - They want to be able to configure and run pipelines programmatically.
   - They want to leverage existing connectors so they can focus on what their product does with the data instead of getting access to it.
   - They want to open source any custom connectors they write to share the maintenance burden with the community.

## Roadmap

Meltano is developed completely in the open on GitLab: <https://gitlab.com/meltano/meltano>. Our [issue tracker](https://gitlab.com/meltano/meltano/-/issues), [epics](https://gitlab.com/groups/meltano/-/epics), and [weekly milestones](https://gitlab.com/groups/meltano/-/milestones) can be found there as well.

To get an idea of what the team and community are currently working on, check out the upcoming milestone's [Development Flow board](https://gitlab.com/groups/meltano/-/boards/536761?scope=all&utf8=%E2%9C%93&milestone_title=%23upcoming).

If you'd like to look further into the future, the [Milestones board](https://gitlab.com/groups/meltano/-/boards/1933232) has a column for each upcoming weekly milestone.

Be aware that issue milestones serve more as a rough indication of relative priority than as hard deadlines,
since short-term priorities can change quickly in response to community feedback, and it's hard to predict how much progress can be made in a week.
Also note that issues labeled `flow::To Do` have higher priority and are more likely to be completed in a given week than those labeled `flow::Triage`, which are often moved to the next milestone at the end of the week, with issues already scheduled for the next week pushed out to make room for them.

Below you will found our current roadmap. As this projects out into the future it is subject to change based on feedback. Don't see something you want on the roadmap? [Make an issue](https://gitlab.com/meltano/meltano/-/issues) and let us know!

#### June 2021

Our focus for June will be to launch the Target SDK, to add support for inline mapping transformations to the SDK and Meltano, enhance the dbt experience within Meltano, and supporting the "Reverse ELT" use case of loading data into a SaaS API.

* [SDK for Singer Targets](https://gitlab.com/meltano/sdk/-/issues/96)
* [Enhanced dbt integration](https://gitlab.com/groups/meltano/-/epics/82)
* [Mapping SDK for inline transformation use cases](https://gitlab.com/meltano/meltano/-/issues/2300)
* [Support Reverse ETL Use Case](https://gitlab.com/meltano/meltano/-/issues/2665)

#### July 2021

Our focus for July will be to expand our integrations for orchestration, data quality, and analysis. We will also work to add support for the fast sync / batch message type to enable higher throughput for extraction and loading.

* [Dagster](https://gitlab.com/meltano/meltano/-/issues/2393 )
* [Great Expectations](https://gitlab.com/meltano/meltano/-/issues/2454)
* [Fast Sync / Batch Messages](https://gitlab.com/meltano/meltano/-/issues/2364)
* [Superset](https://gitlab.com/meltano/meltano/-/issues/2605)
* [Meltano Academy](https://gitlab.com/meltano/meta/-/issues/63)
* [MeltanoHub as SSOT for Meltano](https://gitlab.com/groups/meltano/-/epics/102)

#### August 2021

Our focus for August will be to continue expanding integrations as well as having full out-of-the-box support for an OLAP Database.

* [Jupyter Notebooks](https://gitlab.com/meltano/meltano/-/issues/2595)
* [Prefect](https://gitlab.com/meltano/meltano/-/issues/2668)
* [Out-of-the-box support for an OLAP Database](https://gitlab.com/meltano/meltano/-/issues/2634)
* [Decentralized Management of MeltanoHub Connectors](https://gitlab.com/meltano/meta/-/issues/73)

#### September 2021

Our focus for September will be to enable simple cloud deployments, improve the integration with git providers, and begin the conversion of MeltanoHub to a dynamic site.

* [Simple Cloud Deploys](https://gitlab.com/groups/meltano/-/epics/28)
* [Git-provider Integrations](https://gitlab.com/groups/meltano/-/epics/92)
* [Initial conversion of MeltanoHub to dyanmic site](https://gitlab.com/groups/meltano/-/epics/101)

#### 2021-Q4

Our focus for Q4 will be on creating a compelling monitoring, observability, and data lineage featureset. We also aim to improve the UI and potentailly start offering a SaaS deployment of Meltano.

* [Monitoring, observability, and data lineage](https://gitlab.com/groups/meltano/-/epics/93)
* [Fully featured UI](https://gitlab.com/groups/meltano/-/epics/78)
* [SaaS Deployment of Meltano](https://gitlab.com/groups/meltano/-/epics/94)

## Contributing

Meltano is built for and by its community, and we welcome your contributions to our [GitLab repository](https://gitlab.com/meltano/meltano),
which houses Meltano's
[core](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/core),
[CLI](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/cli),
[UI](https://gitlab.com/meltano/meltano/-/tree/master/src/webapp),
[UI API](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/api),
[these docs](https://gitlab.com/meltano/meltano/-/tree/master/docs/src), and
the [index of discoverable plugins](/docs/contributor-guide.html#discoverable-plugins),
which feeds the lists of [Extractors](https://hub.meltano.com/extractors/) and [Loaders](https://hub.meltano.com/loaders/) that are supported out of the box.

To learn more about contributing to Meltano, refer to the [Contributor Guide](/docs/contributor-guide.html).

## History

Meltano, originally called BizOps, was founded inside [GitLab](https://about.gitlab.com/) [in 2018](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) to serve the GitLab Data Team. It is maintained primarily by [the Meltano team](https://about.gitlab.com/handbook/meltano/) at GitLab, which continues to sponsor its development.

To learn more about Meltano's history from 2018 through 2020, read the following blog post: [Revisiting the Meltano strategy: a return to our roots](https://meltano.com/blog/2020/05/13/revisiting-the-meltano-strategy-a-return-to-our-roots/).

In the first half of 2021, the team grew to include AJ Steers and Taylor Murphy who are leading the Engineering and Product/Data organizations respectively. The 3-person team was able to launch the [SDK for Taps](https://meltano.com/blog/2021/04/05/meltano-launches-v0-1-0-of-the-singer-tap-sdk/), [MeltanoHub](https://meltano.com/blog/2021/06/01/meltanohub-for-singer-launches-with-over-200-taps-and-targets/), and the SDK for Targets while also growing the [Slack community to over 1000 people](https://meltano.com/blog/2021/04/23/community-milestone-1000-slack-members/).

## Team

Meltano is built by an all-remote team of {{$frontmatter.members.length}} and a [community](/docs/community.html) of [contributors](/docs/contributor-guide.html).

<TeamGrid :members="$frontmatter.members" />
