---
metaTitle: Meltano Roadmap, Mission, and Vision
description: Meltano's work plan and release schedule are publicly available at all times.
---

# Roadmap

Meltano enables anyone with access to SaaS APIs and spreadsheets to generate dashboards summarizing the status of their business operations.

## Mission

Provide a simple way to connect data source(s) and generate reports in minutes. through an all-in-one bundled solution, which is optimized for [breadth over depth](https://about.gitlab.com/company/strategy/#breadth-over-depth) to offer basic functionality at each step of the data pipeline.

## Vision

Meltano's mission aligns with the GitLab mission, which is "to change all creative work from read-only to read-write so that everyone can contribute". When everyone can contribute, consumers become contributors and we greatly increase the rate of human progress.

Our contribution to this progress comes through the democratization of data throughout organizations. We help our customers integrate a wide range of data sets to create a single source of truth.

## Persona

Meltano is a small startup within GitLab, and in order to be successful we have chosen to ruthlessly focus on serving a single person.

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

### MAUI

We also track the Monthly Active UI Users (MAUI). MAUI is pronounced like [the island](https://en.wikipedia.org/wiki/Maui).

Internal metrics:

- [Google Analytics for MAUI](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192645310p188384771/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)

## Business Model

Meltano is a free and open source project, and the team is employed by GitLab. In the future, we are likely to introduce proprietary features as we work toward a sustainable business model. At this time, we do not have specific plans in that regard.

 ## Cadence

 ### Release Schedule

Meltano currently follows a weekly release schedule on Mondays.

For our recent changes, you can check [our CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md#unreleased).

You can track our weekly progress and forward-looking plans in greater detail through [our milestones](https://gitlab.com/groups/meltano/-/milestones).

The release process is covered in more detail in [the Handbook](https://about.gitlab.com/handbook/meltano/engineering/#release-process).

### History

Meltano was [launched in August 2018](https://about.gitlab.com/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) by the GitLab Data & Analytics team, and is now an internal startup within GitLab.
