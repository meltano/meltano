---
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

For more background on the project and its current and future goals, watch this talk: [Open source EL(T) with Meltano and Singer](https://meltano.com/blog/2020/10/27/watch-now-open-source-elt-with-meltano-and-singer/) ([recording](https://www.youtube.com/watch?v=n9xZYng0Mgk), [slides](https://docs.google.com/presentation/d/1QXxoniEx7Okbsmc3jiFhKd1LScR8Drd2SE7Ah7mzsww/edit)). Or read this slightly older blog post: [Why we are building an open source platform for ELT pipelines](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/)


## Focus

We have decided to focus on the following personas and use cases, in order of priority, to help us determine what improvements to prioritize building, and what [community contributions](/docs/contributor-guide.html) to accept:

1. Data engineers already using [Singer](https://www.singer.io/) taps and targets
   - They are running Singer-based EL(T) pipelines in production already, likely using a hand-rolled hard-to-reproduce deployment/orchestration strategy.
   - They have experience building and maintaining taps and targets.
   - They are comfortable using a CLI and want to manage their Meltano project like a software engineering project, with all of the benefits of version control and CI/CD.
   - They want to have the option of using a web-based UI to monitor (and possibly manage) their pipelines.
   - Meltano can learn from their experience and provide tooling and documentation to make it easier for them and new users to manage and deploy Singer-based EL(T) pipelines and build and maintain new and existing Singer taps and targets.

2. Data engineers or one-person data teams new to open source ELT
   - They may have come across Singer already, but haven't run Singer taps and targets in production yet.
   - Initially, they are primarily interested in using existing taps and targets instead of writing and maintaining their own, but if they run into issues, they would be comfortable attempting to fix bugs themselves and contributing the fixes upstream.
   - Later, they would not want to be limited by existing taps and targets and will want to learn how to build and maintain their own.
   - They are comfortable using a CLI and want to manage their Meltano project like a software engineering project, with all of the benefits of version control and CI/CD.
   - They want to have the option of using a web-based UI to monitor (and possibly manage) their pipelines.
   - They may also be interested in using Meltano to run [dbt](https://www.getdbt.com) model-based transformations as part of their pipelines.

3. Hobbyists
   - They are capable of programming and comfortable using a CLI, but may not be data engineers.
   - They want to pull data from general or personal sources into a local database for personal use, e.g. basic analytics.
   - They want to run Meltano locally or in a non-production self-hosted environment.
   - They are primarily interested in using one or more specific existing extractors and loaders, but if they run into issues, they would be comfortable attempting to fix bugs themselves and contributing the fixes upstream.
   - They may also be interested in using Meltano's [built-in analytics functionality](/docs/analysis.html), and may look into building the transformation and model plugins that support it.

## Roadmap

Meltano is developed completely in the open on GitLab: <https://gitlab.com/meltano/meltano>. Our [issue tracker](https://gitlab.com/meltano/meltano/-/issues), [epics](https://gitlab.com/groups/meltano/-/epics), and [weekly milestones](https://gitlab.com/groups/meltano/-/milestones) can be found there as well.

To get an idea of what the team and community are currently working on, check out the upcoming milestone's [Development Flow board](https://gitlab.com/groups/meltano/-/boards/536761?scope=all&utf8=%E2%9C%93&milestone_title=%23upcoming).

If you'd like to look further into the future, the [Milestones board](https://gitlab.com/groups/meltano/-/boards/1933232) has a column for each upcoming weekly milestone.

Be aware that issue milestones serve more as a rough indication of relative priority than as hard deadlines,
since short-term priorities can change quickly in response to community feedback, and it's hard to predict how much progress can be made in a week.
Also note that issues labeled `flow::To Do` have higher priority and are more likely to be completed in a given week than those labeled `flow::Triage`, which are often moved to the next milestone at the end of the week, with issues already scheduled for the next week pushed out to make room for them.

## Contributing

Meltano is built for and by its community, and we welcome your contributions to our [GitLab repository](https://gitlab.com/meltano/meltano),
which houses Meltano's
[core](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/core),
[CLI](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/cli),
[UI](https://gitlab.com/meltano/meltano/-/tree/master/src/webapp),
[UI API](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/api),
[these docs](https://gitlab.com/meltano/meltano/-/tree/master/docs/src), and
the [index of discoverable plugins](/docs/contributor-guide.html#discoverable-plugins),
which feeds the lists of [Extractors](/plugins/extractors/) and [Loaders](/plugins/loaders/) that are supported out of the box.

To learn more about contributing to Meltano, refer to the [Contributor Guide](/docs/contributor-guide.html).

## History

Meltano, originally called BizOps, was founded inside [GitLab](https://about.gitlab.com/) [in 2018](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) to serve the GitLab Data Team. It is maintained primarily by [the Meltano team](https://about.gitlab.com/handbook/meltano/) at GitLab, which continues to sponsor its development.

To learn more about Meltano's history from 2018 through 2020, read the following blog post: [Revisiting the Meltano strategy: a return to our roots](https://meltano.com/blog/2020/05/13/revisiting-the-meltano-strategy-a-return-to-our-roots/).
