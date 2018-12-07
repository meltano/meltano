---
title: 'About'
sidebar: auto
---

# About :tada:

Meltano is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.

It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-science-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

[Introduction to Meltano (Google Slides)](https://docs.google.com/presentation/d/1elX6ChyOxWnwtYQUuZOe1rMLPxP7sUle49iaaFKOcTo/edit?usp=sharing)

## Principles

We believe that information is the foundation of good decisions, and that companies of all sizes deserve insights into their operations. So Meltano provides broad, democratized access to detailed operational metrics, driving better decisions and shortening decision cycle time across the entire enterprise.

In addition, we believe that the information a business uses to make decisions must come from all parts of that business. Meltano joins data from multiple systems used by Sales, Marketing, Product and others, thereby providing a comprehensive view of the relationship between business activities, associated costs, and customer long-term value.

A data analyst or scientist should be able to easily use Meltano to add whatever data they need by writing the ELT, know the jobs that are running, and then analyze the data within Meltano Analyze. It should enable individual data people to own the full stack of their analysis, even [if they’re not engineers](https://multithreaded.stitchfix.com/blog/2016/03/16/engineers-shouldnt-write-etl/).

### Milestones

Meltano runs in parallel with the data team with its 2-week milestones. Meltano team runs with 1-week milestones.

### Loosely Coupled Tools

All extractors and loaders should be self-contained units and [loosely coupled](https://en.wikipedia.org/wiki/Loose_coupling), i.e. an extractor should output data in its final form. An extractor should not rely on a loader to clean up its data.

### Product

The product is the glue to adhere the complete data science life cycle together and is built for 2 different team personas.

1. Team 1 wants a CLI, they have engineers in place to write the code, e.g. to make needed extractors.
2. Team 2 wants a GUI, they do not have engineers in place to write a lot of code.

For both teams, we provide a complete single source of truth solution. Single source of truth solution means:

- CLI: One CLI, with one command, with one config to extract, load, transform, remove PII, mock data and orchestrate.
- GUI: One single application to extract, load, transform, remove PII, mock data and orchestrate.

One GUI is also available for both personas for modeling and analysis. All data comes from files which are version controlled.

The orchestration will use the GitLab CI, but running it and configuring it will happen from the CLI or GUI.

## Media

- [Google Docs Meeting Agenda](https://docs.google.com/document/d/1nayKquFLL8DN3h8mnLo3pVZsEKyPcBgQm2mqc5GggPA)
- [Youtube Channel](https://www.youtube.com/meltano/videos)
- [Issue board](https://gitlab.com/meltano/meltano/boards)
- [Functional Group Update (PDF format)](https://drive.google.com/open?id=1oNiCtHkorYKq19kx8CwGr8Z7QCjVQiOj)
- [Functional Group Update (Keynote format)](https://drive.google.com/open?id=1WmleHjP41nsxszGV50ionZKx-b2X3PvF)
- [Blog post](https://about.gitlab.com/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/)
- [Hacker News discussion](https://news.ycombinator.com/item?id=17667399)
- [Call with Hacker News commenter](https://www.youtube.com/watch?v=F8tEDq3K_pE)
- [Article in SD times](https://sdtimes.com/data/gitlab-to-create-tool-for-data-teams/)

## Press Kit

### Logos

<LogoList />

## Approach

### Meltano is the market (data science) lifecycle, just like GitLab is the product (DevOps) lifecycle.

For many companies GitLab serves as the single data store for their engineering organization, shepherding their ideas all the way through to delivering them to customers. There are key gaps however in understanding the effectiveness of sales and marketing. By expanding the common data store to include go to market information, additional insights can be drawn across the customer lifecycle. This evolution is as follows:

1. Business intelligence; this is the current state of the project.
2. Data science; add more machine learning (ML) and Artificial Intelligence (AI)
3. Market lifecycle; the complete go-to-market lifecycle with the user/customer journey.

### Meltano is business intelligence (BI) as code.

Meltano uses [GitLab CI/CD](https://about.gitlab.com/features/gitlab-ci-cd/) to set up and maintain its stack, so software and scripts required are checked into SCM with the attendant benefits: full version control, history, easy collaboration and reviews. Automated management of the BI environment means it is easy to make alterations, re-deploy in the event of an issue or outage, as well as provision new environments for different uses like a staging server.

Meltano also makes use of [review apps](https://docs.gitlab.com/ee/ci/review_apps/), making a fresh clone of the data warehouse for each development branch. This means engineers can test changes to the data pipeline on real data, as well as major schema changes. Once everything is working, the changes can be reviewed, then merged and reflected safely in production.

### Evolution from an internal project, to a community, to open core

1. We are building Meltano to solve a problem that GitLab shares with all other software companies - how to acquire the highest-value customers at the lowest cost of acquisition? We are solving this problem for ourselves first, incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers.
2. Next, we'll focus on building a community around Meltano with more users and regular contributors to the code base.
3. Right now Meltano is open source. In the future we'll introduce proprietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. An example of a proprietary/source available feature is fine grained access controls. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

### Competition & Value

This should be a replacement for other ELT & Data Integration tools: [Boomi](https://boomi.com/), [Informatica Cloud](https://www.informatica.com/products/cloud-integration/cloud-data-integration.html), and [Alooma](https://www.alooma.com/).

## At GitLab

Meltano is a separate product made by a separate team. The goal is at some point to spin it out of GitLab as a new company.

For now we use [PostgreSQL](https://www.postgresql.org/) as the warehouse but we're open to support others such as [MariaDB AX](https://mariadb.com/products/solutions/olap-database-ax), [Redshift](https://aws.amazon.com/redshift/), [MemSQL](https://www.memsql.com/), and [Snowflake](https://www.snowflake.net/).

We use dbt for testing too, instead of [Great Expectations](https://github.com/great-expectations/great_expectations), [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), or closed source options such as [Informatica](https://marketplace.informatica.com/solutions/informatica_data_validation), [iCEDQ](https://icedq.com/), and [QuerySurge](http://www.querysurge.com/).

At GitLab we're using Looker instead of Superset, for sure for the rest of 2018.
If we switch we'll want to make sure that most of the functionality can be replicated in Superset, and the switch will be gradual.
For now, try to keep as much functionality as possible in DBT instead of Looker.

## Metrics

We are targeting analytics for sales and marketing performance first. We plan to track the following metrics, in order of priority. These results will be reviewed over various time periods. Initially, we will support single touch attribution, with support for multitouch in a later sprint.

1. SAOs by source
1. Aggregated (SDR / BDR / AE generated / Other)
1. Campaign level (AWS Reinvent / etc.)
1. SAOs by source by week and/or month
1. Acquisition cost per SAO

- Cost per lead = dollar spend / number of attributed leads

3. Estimated IACV and LTV per SAO based on history (can do IACV if LTV is hard to calculate)

- Estimated IACV = 2 \* IACV at median conversion time
- LTV = IACV _ margin _ average retention time

4. Estimated IACV / marketing ratio.

- CAC = cost per lead \* conversion from lead to IACV
- ROI = LTV / CAC

In the future, we plan to expand support to other areas of an organization like Customer Success, Human Resources, and Finance.

## Data sources

To achieve this, we bring data from all data sources to a common data model (that can and likely will be different for every organization) so it can be used easily and consistently across tools and teams. For example something as simple as unique customer ID, product or feature names/codes.

### Personally Identifiable Information

It is important to be cognizant of the personally identifiable information which is extracted into the data warehouse. Warehouses are at their best when they are leveraged across many parts of the organization, and therefore it is hard to predict which users will ultimately have access and how each user will treat the data.

We recommend the following best practices:

1. Avoid extracting any personally identifiable information in the first place. For example, consider extracting only company names from your CRM and avoid extracting individual contact details.
1. If it is important to collect data about individual users, for example, to learn more about user behavior, pseudonymize the data prior to writing it into the data warehouse.
1. Consider how you are persisting any PII data, and its impact on compliance requirements like GDPR.

## Tools

We want the tools to be open source so we can ship this as a product.

1. Extract and Load (EL): Python scripts, [Singer taps](https://www.singer.io/).
1. Transformation: [dbt](https://docs.getdbt.com/) to handle transforming the raw data into a normalized data model within PG.
1. Warehouse: Any SQL based data warehouse. We recommend [PostgeSQL](https://www.postgresql.org/) and include it in the Meltano pipeline. Postgres cloud services like [Google Cloud SQL](https://cloud.google.com/sql/) are also supported, for increased scalability and durability.
1. Orchestration/Monitoring: [GitLab CI](https://about.gitlab.com/features/gitlab-ci-cd/) for scheduling, running, and monitoring the ELT jobs. In the future, [DAG](https://gitlab.com/gitlab-org/gitlab-ce/issues/41947) support will be added. Non-GitLab alternatives are [Airflow](https://airflow.incubator.apache.org) or [Luigi](https://github.com/spotify/luigi). GitLab CI can handle 1000's of distributed runners to run for example Python scripts.
1. Visualization/Dashboard: Meltano is compatible with nearly all visualization engines, due to the SQL based data store. For example commercial products like [Looker](https://looker.com/) or [Tableau](https://www.tableau.com/), as well as open-source products like [Superset](https://github.com/airbnb/superset) or [Metabase](https://metabase.com) can be used.

## Differences between DAG and CI

We use Airflow to orchestrate Meltano jobs. Jobs can be Extract, Load, Transform etc. To see the difference between the GitLab CI and Airflow which would cover the difference between DAGs and a CI, see this [comprehensive issue](https://gitlab.com/meltano/analytics/issues/458).
