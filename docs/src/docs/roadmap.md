---
metaTitle: Meltano Roadmap, Mission, and Vision
description: Meltano's work plan and release schedule are publicly available at all times.
---

# Roadmap

Meltano is an end-to-end data pipeline and dashboarding tool. We offer a free open source alternative to expensive business intelligence software with an integrated workflow for modeling, extracting, loading, transforming, analyzing, notebooking, and orchestrating your data.

Meltano was [launched in August 2018](https://about.gitlab.com/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) by the GitLab Data & Analytics team, and is now an internal startup within GitLab.

## Mission

Meltano's mission aligns with the GitLab mission, which is "to change all creative work from read-only to read-write so that everyone can contribute."

When everyone can contribute, consumers become contributors and we greatly increase the rate of human progress.

## Vision

Our contribution to this progress comes through the democratization of data throughout organizations. We help our customers integrate a wide range of data sets to create a single source of truth.

Meltano develops powerful open source software enabling the creation of data pipelines and dashboards. By offering an integrated end-to-end solution leveraging best-in-class open source solutions, we deliver tools that are affordable for any company and easy to use at all levels of technical know-how.

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

## Release Schedule

Meltano currently follows a weekly release schedule on Mondays.

For our recent changes, you can check [our CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md#unreleased).

You can track our weekly progress and forward-looking plans in greater detail through [our milestones](https://gitlab.com/groups/meltano/-/milestones).

| Release Date | Release Owner | Speedrun Owner | Shadow |
| ------------ | ------------- | -------------- | ------ |
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

## Focus

The focus of our team is to grow [MAUI](#maui) by 10% every week.
A week is measured from Sunday to Saturday.
Every improvement we make should be optimized by that.
This means sometimes we should prioritize promotion (blog, twitter, video, talk) and usability (docs, UX) over new features.

### MAUI

Meltano's primary KPI is Monthly Active UI Users (MAUI). MAUI is pronounced like [the island](https://en.wikipedia.org/wiki/Maui).

The graph below shows our MAUI growth progress at the end of October 2019. At the target pace (in red) we will have 1,000 MAUI by the end of 2019. While we experienced significant month-over-month growth of MAUI relative to September (+90%), we are still behind pace.

<img src="https://meltano.com/blog/wp-content/uploads/2019/11/Meltano-MAUI-Growth_-Actual-vs.-10-WoW-Goal.png">

Read the [October 2019 recap post on the Meltano blog](https://meltano.com/blog/2019/11/04/meltano-month-in-review-october-2019/).


### Other Metrics

We track the leading indicators upstream of MAUI in the funnel to understand the health of our user adoption funnel from first impression to fully onboarded user:

1. [Meltano.com Website](https://meltano.com)
2. [Meltano Command Line Interface - CLI](https://meltano.com/docs/command-line-interface.html)
3. [Meltano UI](https://meltano.com/docs/architecture.html#meltano-ui)

Internal metrics:

- [Google Analytics for CLI MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192718180p188392047/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)
- [Google Analytics for Meltano.com Website MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192515807p188274549/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D)

## Monetization

We are building Meltano to solve a problem that software companies share: How to acquire the highest-value customers at the lowest cost of acquisition?

We are solving this problem by incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers. Next, we will focus on building a community around Meltano with more users and regular contributors to the code base.

Right now Meltano is open source. In the future we'll introduce proprietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. An example of a proprietary/source available feature is fine grained access controls. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

## Personas

Meltano provides tools to help data teams manage their end-to-end pipeline. This process usually involves collaboration between software engineers and data analysts. In the personas below, we have begun to capture our insights revealed from user interviews.

Ultimately, we are looking to help Meltano users successfully complete a wide range of user stories. To help users onboard quickly, we have created some [simple user stories](https://docs.google.com/document/d/1axKIKtC65Zf9yAV6pApwbZD6Hml-EPh7HEg7W-fPbg0/edit) and we are working to support them through our tutorials.

### Eric (Data Engineer)

Alternative Job Titles: Business Intelligence Engineer, Software Developer

#### Demographics

- Age: 38
- Location: Albany, NY
- Family: Married, two young kids

#### Job Summary

I am responsible for designing, constructing, installing, testing, and maintaining highly scalable data management systems. I improve data foundational procedures, guidelines, and standards. I work on integrating new data management technologies and software engineering tools into existing structures. I also create custom software components and analytics applications.

#### Motivations

- When I build data pipelines, I want to know the uptime, so I make sure they are well crafted.
- When I share data, it should be usable, so the data analyst can be integrated.
- When I don’t have to build custom solutions and instead use reliable solutions I can be more proactive.
- When all of my solutions are flexible, I can easily adapt them to the changing needs of the business.

#### Frustrations

- I’m frustrated when the tools are not reliable because this means the data does not move consistently.
- It is hard for me to maintain the management system when there is a problem with the foundation.

### Allie (Data Analyst)

Alternative Job Titles: Data Scientist - Analytics, Business Intelligence Engineer, Full Stack Data Analyst, Business Analyst

#### Demographics

- Age: 32
- Location: NYC, NY
- Family: Married, no children

#### Job Summary

I am responsible for retrieving and gathering data from the data warehouse, organizing it and making the data collected insightful and easy to understand. My goal is to help stakeholders make informed decisions for their business.

#### Motivations

- When collaborating with others, I want to receive and create clear requirements so I am able to execute and deliver a precise presentation.
- When I ask the right questions, I am more effective in communicating usable data.
- When I develop automated and reusable routines, I am confident in the quality of my pipelines and be more effective in my role.
- When I create meaningful reports, management has insights about new trends as well as areas the company may need to improve upon.

#### Frustrations

- I’m frustrated when I have to educate stakeholders on the meaning of data in their business expertise because it’s a symptom of lack of data adoption from an organization.
- I’m frustrated when data integrity is compromised because data becomes fragmented and full of holes and stakeholders no longer trust my analysis.
- It is hard to interpret data when I may not have the right data because I am unable to support my conclusions.
