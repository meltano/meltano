---
metaTitle: Introduction to Meltano
description: Learn where to use Meltano, how Meltano is built, and where to get started.
---

# Introduction

Meltano is an [open source](https://gitlab.com/meltano/meltano) platform for
building, running & orchestrating ELT pipelines made up of
[Singer](https://www.singer.io/) taps and targets and [dbt](https://www.getdbt.com)
models, that you can [run locally](/docs/installation.html) or [easily deploy in production](/docs/production.html).

## Mission

Our goal is to **make the power of data integration available to all** by building
a true open source alternative to existing proprietary hosted EL(T) solutions,
in terms of ease of use, reliability, and quantity and quality of supported data sources.

For more context, read the following blog post: [Why we are building an open source platform for ELT pipelines](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/).

## Focus

We have decided to focus on the following personas and use cases, in order of priority, to help us determine what improvements to prioritize building, and what [community contributions](/docs/contributor-guide.html) to accept:

1. Data engineers already using [Singer](https://www.singer.io/) taps and targets
   - They are running Singer-based data pipelines in production already, likely using a hand-rolled hard-to-reproduce deployment/orchestration strategy.
   - They have experience building and maintaining taps and targets.
   - They are comfortable using a CLI and want to manage their Meltano project like a software engineering project, with all of the benefits of version control and CI/CD.
   - They want to have the option of using a web-based UI to monitor (and possibly manage) their pipelines.
   - Meltano can learn from their experience and provide tooling and documentation to make it easier for them and new users to manage and deploy Singer-based data pipelines and build and maintain new and existing Singer taps and targets.

2. Data engineers or one-person data teams new to open source ELT
   - They may have come across Singer already, but haven't run Singer taps and targets in production yet.
   - Initially, they are primarily interested in using existing taps and targets instead of writing and maintaining their own, but if they run into issues, they would be comfortable attempting to fix bugs themselves and contributing the fixes upstream.
   - Later, they would not want to be limited by existing taps and targets and will want to learn how to build and maintain their own.
   - They are comfortable using a CLI and want to manage their Meltano project like a software engineering project, with all of the benefits of version control and CI/CD.
   - They want to have the option of using a web-based UI to monitor (and possibly manage) their pipelines.
   - They may also be interested in using Meltano to run [dbt](https://www.getdbt.com) model-based transformations as part of their data pipelines.

3. Hobbyists
   - They are capable of programming and comfortable using a CLI, but may not be data engineers.
   - They want to pull data from general or personal sources into a local database for personal use, e.g. basic analytics.
   - They want to run Meltano locally or in a non-production self-hosted environment.
   - They are primarily interested in using one or more specific existing extractors and loaders, but if they run into issues, they would be comfortable attempting to fix bugs themselves and contributing the fixes upstream.
   - They may also be interested in using Meltano's [built-in analytics functionality](/docs/analysis.html), and may look into building the transformation and model plugins that support it.

## History

Meltano, originally called BizOps, was founded inside [GitLab](https://about.gitlab.com/) [in 2018](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) to serve the GitLab Data Team. It is maintained primarily by [the Meltano team](https://about.gitlab.com/handbook/meltano/) at GitLab, which continues to sponsor its development.

To learn more about Meltano's history from 2018 through 2020, read the following blog post: [Revisiting the Meltano strategy: a return to our roots](https://meltano.com/blog/2020/05/13/revisiting-the-meltano-strategy-a-return-to-our-roots/).
