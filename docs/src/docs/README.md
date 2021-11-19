---
description: Learn where to use Meltano, how Meltano is built, and where to get started.

members:
- name: Douwe Maan
  title: Founder & CEO
  location: Mexico City, Mexico 🇲🇽
  gravatar_hash: 73d1548ae618321220679b3a4fda7fb1 # md5(email)
  social:
    gitlab: DouweM
    twitter: DouweM
    linkedin: douwem
- name: Taylor Murphy
  title: Head of Product & Data
  location: Arlington, TX, USA 🇺🇸
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
- name: Emily Kyle
  title: Director of Marketing
  location: Austin, TX, USA 🇺🇸
  gravatar_hash: ad3bd918d010568b6ce9c5a6a08f0086
  social:
    gitlab: Emily
    twitter: emilylucie
    linkedin: emilylucie
- name: Amanda Folson
  title: Developer Relations Manager
  location: Land o' Lakes, FL, USA 🇺🇸
  gravatar_hash: fe416b883fb81a12313becdf9a29692c
  social:
    gitlab: afolson
    twitter: AmbassadorAwsum
    linkedin: violins
- name: Edgar Ramírez Mondragón
  title: Senior Backend Engineer
  location: Mexico City, Mexico 🇲🇽
  gravatar_hash: a89b7e5a5d6ea347878ea4042ae31dff
  social:
    gitlab: edgarrmondragon
    twitter: cofonlafaefe
    linkedin: edgarrmondragon
- name: Florian Hines
  title: Staff Backend Engineer
  location: San Antonio, TX, USA 🇺🇸
  gravatar_hash: 88529f59d3f298bcc9e2a705dc1f1c68
  social:
    gitlab: pandemicsyn
    twitter: pandemicsyn
    linkedin: florianhines
- name: Ken Payne
  title: Backend Engineer
  location: London, UK 🇬🇧
  gravatar_hash: 778b432070eba884662a752b184dac7b
  social:
    gitlab: kgpayne
    linkedin: k-g-payne
- name: Pat Nadolny
  title: Senior Data Engineer
  location: Brooklyn, NY, USA 🇺🇸
  gravatar_hash: aa4b6175db043b7bfe3177cdc18318c9
  social:
    gitlab: pnadolny13
    linkedin: patnadolny
- name: S. P.
  title: Operations Analyst
  location: CA, USA 🇺🇸
openings:
- title: Head of Partnerships
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4088646004
- title: Technical Marketing Manager
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4075560004
- title: Content Marketing Manager
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4144713004
- title: DataOps Evangelist
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148045004
- title: Senior Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4117149004
- title: Senior Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4117149004
- title: Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148049004
- title: Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148049004
- title: Senior Frontend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4067842004
- title: Senior UI/UX Designer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4147449004
---

# Introduction

[Meltano](https://meltano.com) is ELT for the DataOps era:
[open source](https://gitlab.com/meltano/meltano),
[self-hosted](/docs/production.html),
[CLI-first](/docs/command-line-interface.html),
[debuggable](/docs/command-line-interface.html#debugging), and
[extensible](/docs/plugins.html).

This page covers the project's [Mission](#mission), [Focus](#focus), [Roadmap](#roadmap), [History](#history), and [Team](#team).

To find guides and references on other topics, use the Table of Contents in the sidebar.

## Mission

Our mission is to enable everyone to realize the full potential of their data.

Our vision is for Meltano to become the foundation of every team's ideal data stack.

Our CEO, Douwe Maan, wrote a detailed post about why we believe in this mission and vision [here](https://meltano.com/blog/meltano-the-strategic-foundation-of-the-ideal-data-stack/).

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

We've also [launched](https://meltano.com/blog/launching-meltanolabs-your-home-for-singer-connectors-dbt-packages-and-all-meltano-plugins/) [MeltanoLabs](https://github.com/MeltanoLabs) which is the best place for the community to collaboratively support open source connectors. 

We've also [created an interpretation of the Singer specification](https://hub.meltano.com/singer/spec)
that aims to be clearer for newcomers to the project. We believe the spec is great in its current version, but
confusing documentation has made it challenging for some to onboard to the community.

Last but not least, we're also **[**unlocking the evolution**](https://gitlab.com/groups/meltano/-/epics/88) of the
[**Singer spec**](https://hub.meltano.com/singer/spec)** through the [Singer Working Group](https://meltano.com/blog/2021/10/13/announcing-the-singer-working-group-the-future-of-singer-is-bright/).
This is a framework built with the community for the proposal and consideration of optional extensions to the spec
that compatible tools, including the SDK and Meltano, can choose to support,
while maintaining compatibility between all taps and targets.

## Focus

Our vision for ELT in the DataOps era involves
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

Meltano is developed completely in the open on GitLab: <https://gitlab.com/meltano/meltano>. Our [issue tracker](https://gitlab.com/groups/meltano/-/issues), [epics](https://gitlab.com/groups/meltano/-/epics), and [weekly milestones](https://gitlab.com/groups/meltano/-/milestones) can be found there as well.

To get an idea of what the team and community are currently working on, check out the upcoming milestone's [Development Flow board](https://gitlab.com/groups/meltano/-/boards/536761?scope=all&utf8=%E2%9C%93&milestone_title=%23upcoming).

If you'd like to look further into the future, the [Milestones board](https://gitlab.com/groups/meltano/-/boards/1933232) has a column for each upcoming weekly milestone.

Be aware that issue milestones serve more as a rough indication of relative priority than as hard deadlines,
since short-term priorities can change quickly in response to community feedback, and it's hard to predict how much progress can be made in a week.
Also note that issues labeled `flow::To Do` have higher priority and are more likely to be completed in a given week than those labeled `flow::Triage`, which are often moved to the next milestone at the end of the week, with issues already scheduled for the next week pushed out to make room for them.

Below you will found our current roadmap.
Each item should link to an Epic with the relevant issue linked to that epic.
As this projects out into the future it is subject to change based on feedback.
Don't see something you want on the roadmap? [Make an issue](https://gitlab.com/meltano/meltano/-/issues) and let us know!

Our focus for the rest of the year is going to mainly be in two categories:
* Improving the overall quality of the Singer ecosystem
* Making Meltano the best data integration (ELT) tool on the market

These efforts are the foundation of our larger vision to enable a full DataOps platform.


### November 2021

* Composable Meltano Pipelines - [Epic](https://gitlab.com/groups/meltano/-/epics/116)
  * `meltano run` [Issue](https://gitlab.com/meltano/meltano/-/issues/2301)
  * Stream Maps [Issue](https://gitlab.com/meltano/meltano/-/issues/2300)
* Structured Logging [Issue](https://gitlab.com/meltano/meltano/-/issues/2772)
* Easy deployment of Meltano for production development - [Epic](https://gitlab.com/groups/meltano/-/epics/124)
* Add validator plugin type with Great Expectations and `dbt test` support  - [Epic](https://gitlab.com/groups/meltano/-/epics/111)
* Telemetry Enhancements for Meltano, Meltano SDK, and MeltanoHub - [Epic](https://gitlab.com/groups/meltano/-/epics/122)

### December 2021

* Release v1.0 of Meltano SDK - [Epic](https://gitlab.com/groups/meltano/-/epics/121)
* Documentation Overhaul - [Epic](https://gitlab.com/groups/meltano/-/epics/81)
* Support non-Python plugins - [Issue](https://gitlab.com/meltano/meltano/-/issues/2205)
* Add support for OpenMetadata observability - [Epic](https://gitlab.com/groups/meltano/-/epics/93) & [Issue](https://gitlab.com/meltano/meltano/-/issues/2805)
* Add Fast Sync / `BATCH` Messages to Meltano SDK - [Epic](https://gitlab.com/groups/meltano/-/epics/114)
* Add Dagster as an Orchestrator - [Epic](https://gitlab.com/groups/meltano/-/epics/113) & [Issue](https://gitlab.com/meltano/meltano/-/issues/2393)


### January 2022

* Add Pluggable Log / Metadata Shipping for Observability Enhancement - [Issue](https://gitlab.com/meltano/meltano/-/issues/3008) & [Epic](https://gitlab.com/groups/meltano/-/epics/93)
* Support Secrets Backends Natively -[Issue](https://gitlab.com/meltano/meltano/-/issues/2918)
* UI Improvements and Parity - [Issue](https://gitlab.com/groups/meltano/-/epics/78)

### 2022-H1

Next year will be continuing to make Meltano the best data integration tool on the market and Singer the best open source ecosystem.
With this great foundation in place, we'll continue to invest in making Meltano the best DataOps platform on the market.
This means focusing more on the user interface and on adding features that enable our DataOps vision.

* [SaaS Deployment of Meltano](https://gitlab.com/groups/meltano/-/epics/94)
* [Out-of-the-box support for an OLAP Database](https://gitlab.com/meltano/meltano/-/issues/2634)
* [Initial conversion of MeltanoHub to dynamic site](https://gitlab.com/groups/meltano/-/epics/101)
* [Prefect](https://gitlab.com/meltano/meltano/-/issues/2668)
* [Jupyter Notebooks](https://gitlab.com/meltano/meltano/-/issues/2595)
* [Git-provider Integrations](https://gitlab.com/groups/meltano/-/epics/92)

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

Meltano was [founded](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) inside [GitLab](https://about.gitlab.com/) in 2018 to serve the GitLab Data Team. Meltano started as an open source tool built for GitLab’s data and analytics team, who wanted an end-to-end data platform built around open source components and DevOps principles. You can read more about our history via our [handbook](https://handbook.meltano.com/timeline).

## Team

Meltano is built by an all-remote team of {{$frontmatter.members.length}} and a [community](/docs/community.html) of [contributors](/docs/contributor-guide.html).
If you'd like to join the team, check out the [career opportunities](#careers) below!

<TeamGrid :members="$frontmatter.members" />

## Values

Our values define how we work together and make decisions. You can read them in [our handbook](https://handbook.meltano.com/values).

## Careers <a name="job-openings" />

The team is growing: we're planning to bring on {{$frontmatter.openings.length}} more people in the near future! 

If our [mission](#mission) excites you, and you think could make a difference, we'd love to talk to you. Apply directly through the [job openings](https://boards.greenhouse.io/meltano) below!

<TeamGrid :openings="$frontmatter.openings" />

### Employee Perks
* Unlimited PTO
* Professional Development Support and Budget
* Remote Working
* Reimbursable coworking fees and external office space
* Budget for Office equipment and workspace supplies
* Team Offsites
* Access to world class founders, investors and mentors
