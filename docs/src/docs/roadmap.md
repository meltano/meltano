---
metaTitle: Meltano Roadmap, Mission, and Vision
description: Meltano's work plan and release schedule are publicly available at all times.
---

# Roadmap

Meltano is an end-to-end data pipeline and dashboarding tool. We offer a free open source alternative to expensive business intelligence software with an integrated workflow for modeling, extracting, loading, transforming, analyzing, notebooking, and orchestrating your data.

Meltano was [launched in August 2018](https://about.gitlab.com/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) by the GitLab Data & Analytics team, and is now an internal startup within GitLab.

## Mission

Meltano enables anyone with access to SaaS APIs and spreadsheets to generate dashboards summarizing the status of their business operations.

We provide a simple way to connect data source(s) and generate reports in minutes. The unique value of Meltano is in its all-in-one bundled solution, which is optimized for [breadth over depth](https://about.gitlab.com/company/strategy/#breadth-over-depth) to offer basic functionality at each step of the data pipeline.

## Vision

Meltano's mission aligns with the GitLab mission, which is "to change all creative work from read-only to read-write so that everyone can contribute". When everyone can contribute, consumers become contributors and we greatly increase the rate of human progress.

Our contribution to this progress comes through the democratization of data throughout organizations. We help our customers integrate a wide range of data sets to create a single source of truth.

## Strategy

### Path to v1.0

Meltano is approaching its v1 release. The criteria we have chosen for validating that we have achieved v1 are:

- Users can successfully run Meltano end-to-end
- Users can do everything from the UI (without having to run any commands on the command line)
- Users have clear documentation, including indication of all limitations to existing taps and targets
- Meltano core team is prepared to support backward compatibility to v1 (no breaking changes to architecture) until v2 version

### Beyond v1.0

There is a lot more to build. A few key areas we know we need to invest more time after V1 are:

- Data Analysis: adopt open source solution so we can bring in many more features without building from scratch
- One-click deployment to popular hosting solutions (e.g. Amazon AMI marketplace, DigitalOcean droplets, etc.)
- Creating and managing databases and warehouses
- Ongoing inclusion of more pre-built taps, targets, and default transforms for popular data sources

## Focus

The focus of our team is to grow [MAUI](#maui) by 10% every week.
A week is measured from Sunday to Saturday.
Every improvement we make should be optimized by that.
This means sometimes we should prioritize promotion (blog, twitter, video, talk) and usability (docs, UX) over new features.

## Metrics

### MAU

We track the Monthly Active Users (MAU) of three things to understand the health of our user adoption funnel from first impression to fully onboarded user:

1. [Meltano.com Website](https://meltano.com)
2. [Meltano Command Line Interface - CLI](https://meltano.com/docs/command-line-interface.html)
3. [Meltano UI](https://meltano.com/docs/architecture.html#meltano-ui)

Internal metrics:

- [Google Analytics for CLI MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192718180p188392047/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)
- [Google Analytics for Meltano.com Website MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192515807p188274549/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D)

### MAUI

We also track the Monthly Active UI Users (MAUI). MAUI is pronounced like [the island](https://en.wikipedia.org/wiki/Maui).

Internal metrics:

- [Google Analytics for MAUI](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192645310p188384771/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)

## Monetization

We are building Meltano to solve a problem that software companies share: How to acquire the highest-value customers at the lowest cost of acquisition?

We are solving this problem by incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers. Next, we will focus on building a community around Meltano with more users and regular contributors to the code base.

Right now Meltano is open source. In the future we'll introduce proprietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. An example of a proprietary/source available feature is fine grained access controls. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

## Personas

Meltano is a small startup within GitLab, and in order to be successful we have chosen to ruthlessly focus on a serving a single person.

### Target Persona Type: Founder

Our target persona has the following traits:
*  One busy person at a startup *using Meltano in single player mode*
*  They have access to all systems and data across the company
*  New to data (does not write code, queries, etc.)
*  Need to do analysis to run the business 
*  Needs to do both engineering tasks and analyst tasks because there is nobody else

What they are **not**:
*  **Don't have "analyst" in their job title.** They perform that function because they have to, and likely are CEO/founder running a department that has a lot of SaaS tools and data, likes sales or marketing. They are setting up the foundational systems in the company.
*  **Don't have technical know-how or the time** for setting up a server, using the command line, writing code, creating custom taps, targets, transforms or models. They are running their company, and have a thousand other things to do.

### Other Persona Types

There are other personas we are **explicitly NOT building Meltano for** who may discover our tools and become users or contributors:

* Data Analysts
* Data Engineers
* Machine Learning Engineers

 ## Cadence

 ### Release Schedule

Meltano currently follows a weekly release schedule on Mondays.

For our recent changes, you can check [our CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md#unreleased).

You can track our weekly progress and forward-looking plans in greater detail through [our milestones](https://gitlab.com/groups/meltano/-/milestones).

| Release Date | Release Owner | Speedrun Owner | Shadow |
| ------------ | ------------- | -------------- | ------ |
| 2019-10-07   | Ben H.        | Ben H.         |        |
| 2019-10-14   | Derek K.      | Derek K.       |        |
| 2019-10-21   | Ben H.        | Ben H.         |        |
| 2019-10-28   | Micael B.     | Micael B.      |        |
| 2019-11-04   | Derek K.      | Derek K.       |        |
| 2019-11-11   | Yannis R.     | Yannis R.      |        |
| 2019-11-18   | Douwe M.      | Douwe M.       |        |
| 2019-11-25   | Ben H.        | Ben H.         |        |
| 2019-12-02   | Micael B.     | Micael B.      |        |
| 2019-12-09   | Derek K.      | Derek K.       |        |
| 2019-12-16   | Yannis R.     | Yannis R.      |        |
| 2019-12-23   | Ben H.        | Ben H.         |        |
| 2019-12-30   | Ben H.        | Ben H.         |        |

:::tip Can't make your scheduled release?
If you are unable to cover an assigned week, please find someone to cover for you and submit an MR to this page with the new owner.
:::