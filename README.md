[![pipeline status](https://gitlab.com/meltano/meltano/badges/master/pipeline.svg)](https://gitlab.com/meltano/meltano/commits/master)

# Meltano

Meltano is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.
It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-science-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

## Data Science Lifecycle

| Stage     | Meltano selected | OSS considered but not selected | Proprietary alternatives |
| --------- | ------------ | -------------- | --------------------- |
| Model     | [Meltano Model](#meltano-model) | [Open ModelSphere](http://www.modelsphere.com/org/) | [LookML](https://looker.com/platform/data-modeling), [Matillion](http://www.stephenlevin.co/data-modeling-layer-startup-analytics-dbt-vs-matillion-vs-lookml/) |
| Extract   | [Singer Tap](#tap) | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/) | [Alooma](https://www.alooma.com/), [Fivetran](https://fivetran.com/) |
| Load      | [Signer Target](#target) | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/) | [Alooma](https://www.alooma.com/), [Fivetran](https://fivetran.com/) |
| Transform | [dbt](https://www.getdbt.com/), [Python scripts](#python-scripts) | [Stored procedures](#stored-procedures), [Pentaho DI](http://www.pentaho.com/product/data-integration) | [Alooma](https://www.alooma.com/) |  
| Analyze | [Meltano Analysis](https://gitlab.com/meltano/meltano/tree/master/src/meltano_ui) | [Metabase](https://www.metabase.com/) | [Looker](https://looker.com/), [Periscope](https://www.periscopedata.com/) |
| Notebook | [JupyterHub](https://github.com/jupyterhub/jupyterhub) | [GNU Octave](https://www.gnu.org/software/octave/) | [Nurtch](https://www.nurtch.com/), [Datadog notebooks](https://www.datadoghq.com/blog/data-driven-notebooks/) |
| Orchestrate | [GitLab CI](https://about.gitlab.com/features/gitlab-ci-cd/) | [Luigi](https://github.com/spotify/luigi), [Airflow](https://airflow.apache.org/), [Nifi](https://nifi.apache.org/) | [Fivetran](https://fivetran.com/) |

## Principles

We believe that information is the foundation of good decisions, and that companies of all sizes deserve insights into their operations. So Meltano provides broad, democratized access to detailed operational metrics, driving better decisions and shortening decision cycle time across the entire enterprise.

In addition, we believe that the information a business uses to make decisions must come from all parts of that business. Meltano joins data from multiple systems used by Sales, Marketing, Product and others, thereby providing a comprehensive view of the relationship between business activities, associated costs, and customer long-term value.

A data analyst or scientist should be able to easily use Meltano to add whatever data they need by writing the ELT, know the jobs that are running, and then analyze the data within Meltano Analyze. It should enable individual data people to own the full stack of their analysis, even [if they’re not engineers](https://multithreaded.stitchfix.com/blog/2016/03/16/engineers-shouldnt-write-etl/).

### How Meltano Does Version Control

**Note: This section is a WIP, and not currently functioning as written. This note will be removed once it does work as advertised.**

Meltano runs many different types of files and projects including but not limited to:

1. Extractors
1. Loaders
1. DBT Transforms
1. Meltano Models or .lookml Models
1. Jupyter Notebook files
1. Airflow DAGs as part of an orchestration step

First install Meltano through `pip`, via

**If you want to install Meltano in a venv: virtualenv and pipenv are not supported. Please use `python -m venv venv` to create your virtual environment. See [this issue](https://gitlab.com/meltano/meltano/issues/141).**

```bash
pip install meltano
# clone the gitlab-runner project
git clone https://gitlab.com/meltano/gitlab-runners
cd gitlab-runners
meltano orchestrate
```

After installing `meltano` CLI, you can choose to run meltano against your project.

The gitlab-runner project contains a `meltano.yml` file:

`meltano.yml`

```yml
version: 0.0.0
extractors:
- name: first
  url: https://gitlab.com/meltano/tap-first
- name: mysql
  url: https://gitlab.com/meltano/tap-mysql
- name: zendesk
  url: https://gitlab.com/meltano/tap-zendesk
  ...
loaders:
- name: snowflake
  url: https://gitlab.com/meltano/target-snowflake
  warehouse: main
- name: postgresql
  url: https://gitlab.com/meltano/target-postgresql
  warehouse: test
  ...
warehouses:
- name: main
  username: "$MAIN_WAREHOUSE"
  password: "$MAIN_WAREHOUSE_PW"
  host: "$MAIN_WAREHOUSE_HOST"
  db: "$MAIN_WAREHOUSE_DB"
  type: snowflake
  ...
orchestrate:
- name: first-to-csv
  extractor: first
  loader: csv
  transformer:
  - first
  ...
```

Your project should contains the following directory structure:

* model - For your `.lookml` files.
* transform - For your dbt `.sql` files.
* analyze - For your `.yml` dashboard files.
* notebook - For your `.ipynb` notebook files.
* orchestrate - For your airflow `.py` files.
* .meltano - A .gitignored directory for internal caching (venvs, pypi packages, etc.). 
* load - A directory where your configs for your loaders are placed. Each config should be in a directory with the name of the loader. e.g. For csv loader, the config would be in `load/target-csv/config.json`.
* extract - A directory where your configs for your extractors are placed. Each config should be in a directory with the name of the extractor. e.g. For zendesk extractor, the config would be in `extract/tap-zendesk/config.json`.
* .gitignore
* README.md
* meltano.yml - Config file which shows which extractors and loaders, etc. you would like to use and where to find them.

Here is a sample of what your project might look like:

```
├── extract
│   ├── tap-marketo
│   └── tap-zendesk
│       ├── config.json
│       └── properties.json
├── load
│   └── target-postgres
│       └── config.json
├── .meltano
│   ├── dbt
│   │   └── meltano.yml
│   ├── model
│   │   ├── base_ticket.model.lookml
│   │   └── ticket.model.lookml
│   ├── run
│   │   ├── dbt
│   │   │   ├── dbt_profile.yml
│   │   │   └── dbt_project.yml
│   │   └── singer
│   │       ├── tap.config.json
│   │       ├── tap.properties.json
│   │       └── target.config.json
│   └── transform
│       └── tap-zendesk
│           ├── base_ticket.sql
│           └── base_user.sql
├── meltano.yml
├── model
│   └── zendesk
│       ├── zendesk.model.lookml
│       └── zendesk.view.lookml
├── analyze
│   └── zendesk
│       └── zendesk.dashboard.yml
├── orchestrate
│   ├── dag_1.py
│   ├── dag_2.py
│   ├── dag_3.py
│   ├── dag_4.py
│   └── dag_5.py
└── transform
    └── tap-zendesk
        └── base.sql
```

Once you have your project, you can run `meltano` against it.

* `meltano init [project name]`: Create an empty meltano project.
* {: #meltano-add}`meltano add [extractor | loader] [name_of_plugin]`: Adds extractor or loader to your melatano.yml file and installs in `.meltano` directory with `venvs`, `dbt` and `pip`. 
* `meltano install`: Installs all the dependencies of your project based on the `meltano.yml` file.
* `meltano discover all`: list available extractors and loaders:
  * `meltano discover extractors`: list only available extractors
  * `meltano discover loaders`: list only available loaders
* `meltano extract [name of extractor] --to [name of loader]`: Extract data to a loader and optionally transform the data
* `meltano transform [name of transformation] --warehouse [name of warehouse]`: 
* `meltano elt <job_id> --extractor <extractor> --loader <loader> [--dry]`: Extract, Load, and Transform the data.
* `meltano invoke <plugin_name> PLUGIN_ARGS...`: Invoke the plugin manually. 

### Milestones

Meltano runs in parallel with the data team with its 2-week milestones. Meltano team runs with 1-week milestones.

### Loosely Coupled Tools

All extractors and loaders should be self-contained units and [loosely coupled](https://en.wikipedia.org/wiki/Loose_coupling), i.e. an extractor should output data in its final form. An extractor should not rely on a loader to clean up its data.

### Product

The product is the glue to adhere the complete data science life cycle together and is built for 2 different team personas.

1. Team 1 wants a CLI, they have engineers in place to write the code, e.g. to make needed extractors.
2. Team 2 wants a GUI, they do not have engineers in place to write a lot of code.

For both teams, we provide a complete single source of truth solution. Single source of truth solution means:
* CLI: One CLI, with one command, with one config to extract, load, transform, remove PII, mock data and orchestrate.
* GUI: One single application to extract, load, transform, remove PII, mock data and orchestrate. 

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

1. We are building Meltano to solve a problem that GitLab shares with all other software companies - how to acquire the highest-value customers at the lowest cost of acquisition?  We are solving this problem for ourselves first, incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers.
2. Next, we'll focus on building a community around Meltano with more users and regular contributors to the code base.
3. Right now Meltano is completely open source. After we have a community we'll introduce proprietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

## Roadmap

1. [MVC](https://gitlab.com/meltano/meltano/issues/10)
  * [Horizontal slice of ELT sources](https://gitlab.com/meltano/meltano/issues?scope=all&utf8=✓&state=opened&label_name[]=elt): Salesforce, Marketo, NetSuite, Zuora, etc.
  * [Data Pipeline](https://gitlab.com/meltano/meltano/issues?label_name[]=pipeline): container, CI pipeline, review apps
2. Data Model and Visualization
  * [Common Data Model](https://gitlab.com/meltano/meltano/issues?label_name[]=data-model): Conventions for common table and field names (but it allows you to make it organization specific)
  * [Field Mapping](https://gitlab.com/meltano/meltano/issues/121): Mapping of user fields to common data model, if required
  * [Visualization Sample](https://gitlab.com/meltano/meltano/issues/122): Documentation and samples for connecting a visualization engine
  * [JupyterHub deployment](https://gitlab.com/meltano/jupyter-hub): Easily deploy JupyterHub for data exploration
3. [Ease of use & Automation](https://gitlab.com/meltano/meltano/issues?label_name%5B%5D=ease-of-use)
  * Seamless handle some schema changes, like a field rename
  * Match user fields to common data model, without intervention

## Data security and privacy

When using Meltano, like any data science tool, it is important to consider the security and privacy implications.

* Meltano expects the required credentials for each extractor to be stored as a project variable. Project members with the role [`Maintainer` or `Owner`](https://docs.gitlab.com/ee/user/permissions.html#project-members-permissions) will be able to see these in plaintext, as well as any instance wide administrators. If you are using GitLab.com, this includes select GitLab employees responsible for the service.
  * Support for KMS systems is being considered for a future release.
* Because these variables are passed to GitLab CI jobs, it is possible to accidentally or maliciously compromise them: 
  * For example, a developer who normally cannot see the variables in project settings, could accidentally print the environment variables when debugging a CI job, causing them to be readable by a wider audience than intended.
  * Similarly it is possible for a malicious developer to utilize the variables to extract data from a source, then send it to an unauthorized destination.
  * These risks can be mitigated by [restricting the production variables](https://docs.gitlab.com/ee/ci/variables/#protected-variables) to only protected branches, so code is reviewed before it is able to run with access to the credentials. It is also possible to set job logs to be available to only those with `Developer` roles or above, in CI/CD settings.
* When designing your data warehouse, consider any relevant laws and regulations, like GDPR. For example, historical data being retained as part of a snapshot could present challenges in the event a user requests to be forgotten.

### Competition & Value

This should be a replacement for other ELT & Data Integration tools: [Boomi](https://boomi.com/), [Informatica Cloud](https://www.informatica.com/products/cloud-integration/cloud-data-integration.html), and [Alooma](https://www.alooma.com/).

## At GitLab

Meltano is a separate product made by a separate team. The goal is at some point to spin it out of GitLab as a new company.

For now we use [PostgreSQL](https://www.postgresql.org/) as the warehouse but we're open to support others such as [MariaDB AX](https://mariadb.com/products/solutions/olap-database-ax), [Redshift](https://aws.amazon.com/redshift/), [MemSQL](https://www.memsql.com/), and [Snowflake](https://www.snowflake.net/).

We use dbt for testing too, instead of [Great Expectations](https://github.com/great-expectations/great_expectations), [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), or closed source options such as [Informatica](https://marketplace.informatica.com/solutions/informatica_data_validation), [iCEDQ](https://icedq.com/), and [QuerySurge](http://www.querysurge.com/).

At GitLab we're using Looker instead of Superset, for sure for the rest of 2018.
If we switch we'll want to make sure that most of the functionality can be replicated in Superset, and the switch will be gradual.
For now, try to keep as much functionality as possible in DBT instead of Looker.

### Meltano data security and privacy at GitLab

We take user security and privacy seriously at GitLab. We internally use Meltano to learn about how users interact with GitLab.com, build a better product, and efficiently run our organization. We adhere to the following guidelines:

1. GitLab employees have access to the data warehouse and can see pseudonymized data. In some cases due to public projects, it is possible to tie a pseudonymized account to a public account. It is not possible to learn the private projects a user is working on or contents of their communications.
1. We will never release the pseudonymized dataset publicly, in the event it is possible to reverse engineer unintended content.
1. Select GitLab employees have administrative access to GitLab.com, and the credentials used for our extractors. As [noted above](#data-security-and-privacy), developers on the Meltano project could maliciously emit credentials into a job log, however, the logs are not publicly available.

## Metrics

We are targeting analytics for sales and marketing performance first. We plan to track the following metrics, in order of priority. These results will be reviewed over various time periods. Initially, we will support single touch attribution, with support for multitouch in a [later sprint](doc/development_plan.md#backlog).

1. SAOs by source
  1. Aggregated (SDR / BDR / AE generated / Other)
  1. Campaign level (AWS Reinvent / etc.)
1. SAOs by source by week and/or month
2. Acquisition cost per SAO
  * Cost per lead = dollar spend / number of attributed leads
3. Estimated IACV and LTV per SAO based on history (can do IACV if LTV is hard to calculate)
  * Estimated IACV = 2 *  IACV at median conversion time
  * LTV = IACV * margin * average retention time
4. Estimated IACV / marketing ratio.
  * CAC = cost per lead * conversion from lead to IACV
  * ROI = LTV / CAC

In the future, we plan to expand support to other areas of an organization like Customer Success, Human Resources, and Finance.

## Data sources

To achieve this, we bring data from all [data sources](data_sources.md) to a [common data model](doc/data_model.md) (that can and likely will be different for every organization) so it can be used easily and consistently across tools and teams. For example something as simple as unique customer ID, product or feature names/codes.

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

## How to Install and Run Meltano  

**Note:** Meltano requires Python version >= 3.6.6

### With Docker  

You can run a local copy of Meltano using [docker-compose][]. Run the following in your project directory:

```bash
# build the project
make

# initialize the db schema
make init_db

# bring up docker-compose
docker-compose up
```

### Without Docker

Run the following in your project directory:

```bash
python -m venv ~/path/to/melt_venv
source ~/path/to/melt_venv/bin/activate
pip install -r requirements.txt
pip install -e '.[all]'
python -m meltano.api
```

This will start:

- The front-end UI at [http://localhost:8080]()
- The API server [http://localhost:5000]() and an accompanying Postgres DB
- A mock warehouse Postgres DB

For more info see the [docker-compose.yml]()

## Tap

See our [sample first tap](https://gitlab.com/meltano/tap-first/) as a good tap starting point. 

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of taps](https://www.singer.io/#taps)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

## Target

See our [csv target](https://gitlab.com/meltano/target-csv) as a good starting point for targets.

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of targets](https://singer.io/#targets)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

## Workflow for tap/target development

### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

  1. Fork (using Meltano organization)
  1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
  1. Modify and submits PRs
  1. If there is resistance, fork as our tap (2)

### For taps/targets we create

  1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
  1. For target developement please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
  1. Use a separate repo (meltano/target|tap-x) in GitLab
e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
  1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
  1. Publish PyPI packages of these package (not for now)
  1. We could mirror this repo on GitHub if we want (not for now)

## Discoverability

We will maintain a curated list of taps/targets that are expected to work out of the box with Meltano.

Meltano should help the end-user find components via a `discover` command:

```
$ meltano discover extract
tap-demo==...
tap-zendesk==1.3.0
tap-marketo==...
...

$ meltano discover load
target-demo==...
target-snowflake==git+https://gitlab.com/meltano/target-snowflake@master.git
target-postgres==...
```

## How to install taps/targets

### Locally

See [meltano-add](#meltano-add)

### On a CI

A docker image should be build containing all the latest curated version of the taps/targets, each isolated into its own virtualenv.

This way we do not run into `docker-in-docker` problems (buffering, permissions, security).

Meltano should provide a wrapper script to manage the execution of the selected components:

`meltano extract tap-zendesk --to target-postgres`

## How to use

> Notes:
> * Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields.
> * The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription.

The Meltano product consists of three key components:

1. A SQL based data store, for example [PostgreSQL](https://www.postgresql.org/) or [Cloud SQL](https://cloud.google.com/sql/). We recommend using Postgres for [review apps](https://about.gitlab.com/features/review-apps/) and a more durable and scalable service for production.
1. This project, [`meltano`](https://gitlab.com/meltano/meltano), which contains the ELT scripts and CI jobs to refresh the data warehouse from the [configured sources](doc/data_sources.md). Typically configured to run on a [scheduled CI job](https://docs.gitlab.com/ce/user/project/pipelines/schedules.html) to refresh the data warehouse from the configured sources.
1. The [`meltano-elt`](https://gitlab.com/meltano/meltano-elt) container, which includes the necessary dependencies for the ELT scripts. Used as the base image for the CI jobs.

As development progresses, additional documentation on getting started along with example configuration and CI scripts will become available.

It is expected that the Meltano project will have many applications managed in the top level of the project. Some or parts of these applications could be useful to many organizations, and some may only be useful within GitLab. We have no plans on weighing the popularity of an individual application at the top level of the Meltano project for inclusion/exclusion.

## Meltano components

### Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the [Data Science Lifecycle].

Our CLI tool provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data science lifecycle.

#### meltano schema
Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

##### create <SCHEMA> <ROLES>
Create and grant usage for a database schema.

### Meltano Model

Meltano uses models based on the [LookML](https://docs.looker.com/data-modeling/learning-lookml/lookml-terms-and-concepts#model) language. They allow you to model your data so you can easily analyze and visualize it in Meltano Analysis.

### Meltano Transform

#### DBT

Meltano uses [dbt](https://docs.getdbt.com/) to transform the source data into the `analytics` schema, ready to be consumed by models.  

[Fishtown wrote a good article about what to model dynamically and what to do in dbt transformations](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304).

#### Python scripts

In certain circumstances transformations cannot be done in dbt (like API calls), so we use python scripts for these cases.

### Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.

#### Loading a CSV:

> Notes:
> - The naming format for the `FILES` must be `<schema>.<table>.csv`. This pattern is required and will be used to create/update the table in the DW.
> - Multiple `FILES` can be used, use spaces to separate.

  - Start the cloud sql proxy
  - Run the command:
  ```
  python3 elt/util/spreadsheet_loader.py csv FILES...
  ``` 
  - Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Loading a Google Sheet:

> Notes:
> - Each `FILES` will be located and loaded based on its name. The names of the sheets shared with the runner must be unique and in the `<schema>.<table>` format
> - Multiple `FILES` can be used, use spaces to separate.

  - Share the sheet with the required service account (if being used in automated CI, use the runner service account)
  - Run the command:
  ```
  python3 elt/util/spreadsheet_loader.py sheet FILES...
  ```
  - Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Further Usage Help:

  - Run the following command(s) for additional usage info `python3 elt/util/spreadsheet_loader.py <csv|sheet> -- --help`

### Docker images

Meltano provides the following docker images:

> Notes: All images are available in the GitLab's registry: `registry.gitlab.com`
  
  - `meltano/meltano`: Contains the API, CLI, and Meltano Analyze. This image should be deployed as Meltano Analyze.
  - `meltano/meltano/runner`: Contains the CLI and extra runner specific binaries. This image should be used on the CI runner. 
  - `meltano/meltano/singer_runner`: **DEPRECATED: Use `meltano/meltano/runner` instead** Contains the CLI, and all curated taps/targets pre-installed.

> Notes: These images are base images used as the basis of other images.

  - `meltano/meltano/cli`: Contains the meltano cli
  - `meltano/meltano/base`: Contains the requirements for `meltano/meltano`

## Best practices

### How to Use Sub pipelines to Effectively Create a DAG like Architecture

An example of this can be seen in the [gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/.gitlab-ci.yml#L251) which is being used to trigger the gitlab-qa project. This will trigger a [`SCRIPT_NAME`:`trigger-build`](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/scripts/trigger-build) which has the API calls written in Ruby, for which we can use Python. From there the sky is the limit.

### Managing API requests and limits

Many of the SaaS sources have various types of API limits, typically a given quota per day. If you are nearing the limit of a given source, or are iterating frequently on your repo, you may need to implement some additional measures to manage usage.

#### Reducing API usage by review apps

One of the easiest ways to reduce consumption of API calls for problematic ELT sources is to make that job manual for branches other than `master`. This way when iterating on a particular branch, this job can be manually run only if it specifically needs to be tested.

We don't want the job on `master` to be manual, so we will need to create two jobs. The best way to do this is to convert the existing job into a template, which can then be referenced so we don't duplicate most of the settings.

For example take a sample Zuora ELT job:

```yaml
zuora:
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

The first thing to do would to convert this into an anchor, and preface the job name with `.` so it is ignored:

```yaml
.zuora: &zuora
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

Next, we can define two new jobs. One for `master` and another manual job for any review branches:

```yaml
zuora_prod:
  <<: *zuora
  only:
    - master

zuora_review:
  <<: *zuora
  only:
    - branches
  except:
    - master
  when: manual
```

### Pipeline configuration

Data integration stages are configurable using `Project variables` for the CI/CD pipeline. The following variables may help you control what needs to run:

  - `EXTRACT_SKIP`: either `all` (to skip the `extract` stage) or job names, like `marketo,zendesk,zuora` to be skipped from the pipeline.
  - `UPDATE_SKIP`: either `all` (to skip the `update` stage) or job names, like `sfdc_update`.

### Stored procedures

We don't use stored procedures because they are hard to keep under version control.

## Contributing

### Code style

Meltano uses [Black](https://github.com/ambv/black) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

You can also have black run automatically using a `git` hook. See https://github.com/ambv/black#version-control-integration for more details.

### Merge Requests

Meltano uses an approval workflow for all merge requests.

  1. Create your merge request
  1. Assign the merge request to any Meltano maintainer for a review cycle
  1. Once the review is done the reviewer should approve the merge request
  1. Once approved, the merge request can be merged by any Meltano maintainer

## GitLab Data and Analytics - Internal

### Charter/Goals

* Build a centralized data warehouse that can support data analysis requirements from all functional groups within the company.
* Create a common data framework and governance practice.
* Establish the single source of truth for company metrics.
* Establish a change management processes for source systems.
* Develop a Data Architecture plan (in conjunction with functional teams).
* Develop a roadmap for systems evolution in alignment with the Company’s data architecture plan.

### GitLab Internal Analytics Architecture

![GitLab Internal Analytics Architecture](img/WIP_ GitLab_Analytics_Architecture.jpg)

#### Data Warehouse

* Using Cloud SQL.
* Consolidated repository of all source data - scrubbed and modeled into a format optimized for analytic workloads (Dimensional model).
* Serves as the Single Source of Truth for reporting, analysis, and visualization applications.
* Will need to be audited regularly back to the source.
* Should not be generally available - will require strict access controls for direct querying not done through a controlled application such as metabase.

#### Accessing the Data Warehouse
If you want direct access to the data warehouse (outside of Looker or JupyterHub), follow these steps.

* Request an account (username and password) from Taylor Murphy or Joshua Lambert through Slack.
* Verify your Google account is associated with the `gitlab-analysis` project, it should have the `Cloud SQL Client` role.
* Set up your local machine by installing the [gcloud SDK](https://cloud.google.com/sdk/docs/).
* Run `gcloud config set project gitlab-analysis`
* Run `gcloud auth application-default login`
* Connect to cloudsqlproxy `./cloud_sql_proxy -instances=gitlab-analysis:us-west1:dev-bizops=tcp:5432`
* Connect to the Data Warehouse through the terminal (a separate tab) with `psql "host=127.0.0.1 sslmode=disable dbname=dw_production user=<username>`
* Alternatively, use your favorite database tool with `host=127.0.0.1` and `dbname=dw_production`

#### Hosts Records Dataflow

From our on-premises installations, we recieve [version and ping information](https://docs.gitlab.com/ee/user/admin_area/settings/usage_statistics.html) from the software. This data is currently imported once a day from a PostgreSQL database into our enterprise data warehouse (EDW). We use this data to feed into Salesforce (SFDC) to aid our sales representatives in their work.

The domains from all of the pings are first cleaned by standardizing the URL using a package called [tldextract](https://github.com/john-kurkowski/tldextract). Each cleaned ping type is combined into a single host record. We make a best effort attempt to align the pings from the same install of the software. 

This single host record is then enriched with data from three sources: DiscoverOrg, Clearbit, and WHOIS. If DiscoverOrg has no record of the domain we then fall back to Clearbit, with WHOIS being a last resort. Each request to DiscoverOrg and Clearbit is cached in the database and is updated no more than every 30 days. The cleaning and enrichment steps are all accomplished using Python.

We then take all of the cleaned records and use dbt to make multiple transformations. The last 60 days of pings are aligned with Salesforce accounts using the account name or the account website. Based on this, tables are generated of host records to upload to SFDC. If no accounts are found, we then generate a table of accounts to create within SFDC. 

Finally, we use Python to generate SFDC accounts and to upload the host records to the appropriate SFDC account. We also generate any accounts necessary and update any SFDC accounts with DiscoverOrg, Clearbit, and WHOIS data if any of the relevant fields are not already present in SFDC.

#### Updating SFDC Extract
[Taylor explains Pentaho Data Integration](https://drive.google.com/open?id=1OD7QQ2aD-4LWL-ExM8WAyyeuBm2bTRa6) GitLab internal because of credentials being viewable.

As of 2018-05-24:

If removing a field from the extract, delete the fields from the `.ktr` file, similar to what was done in [this commit](https://gitlab.com/meltano/meltano/commit/0a76c160816d2505105eb4c2642b6b82ca9b1350).

If adding a field, take the following steps:

* Add to the appropriate `.ktr` file for the given object, similar to what was done [here](https://gitlab.com/meltano/meltano/commit/6b89bb592ee2389f91ebcb86102028ab87bb77d9)
* Add the column to the appropriate table in the database (requires access to `gitlab` user)
* Update all of the objects from SFDC because the database will have `null` for every row
  * Use Pentaho Data Integration locally to run the job based on query condition of `Your_added_field__c != null`
* Check for any snapshots of that table, if they exist, add the column to the tables as well.

#### Managing Roles

All role definitions are in [/elt/config/pg_roles/](https://gitlab.com/meltano/meltano/tree/master/elt/config)

Ideally we'd be using [pgbedrock](https://github.com/Squarespace/pgbedrock) to manage users. Since internally we are using CloudSQL, we're not able to access the superuser role which pgbedrock requires. However, the YAML format of the role definitions is convenient for reasoning about privileges and it's possible the tool could evolve to validate privileges against a given spec, so we are using the pgbedrock definition syntax to define roles here. 

The `readonly` role was generated using the following commands:

```sql
CREATE ROLE readonly;

GRANT USAGE on SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to readonly;

GRANT SELECT on ALL TABLES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to readonly;

-- Ensures all future tables are available to the role
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora 
  GRANT SELECT ON TABLES TO readonly;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sandbox TO readonly;

```

The `analytics` role was generated using the following commands:

```sql

CREATE ROLE analytics;

GRANT USAGE on SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to analytics;

GRANT SELECT on ALL TABLES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to analytics;

-- Ensures all future tables are available to the role
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora 
  GRANT SELECT ON TABLES TO analytics;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics, public, sandbox TO analytics;

``` 

New user roles are added to a specific role via:

```sql
CREATE ROLE newrole WITH PASSWORD 'tmppassword' IN ROLE metarole;

ALTER ROLE newrole WITH LOGIN;
```

New readonly and analytics users are then given instructions via Google Drive on how to connect their computer to the CloudSQL Proxy and on how to change their password once they log in.

By default, roles can log in to the main production instance of the data warehouse. Any password updates will propagate to `dev-bizops` and review instances when they are next refreshed.

Both readonly and analytics roles are not able to alter data in load only schemas. Currently, analytics, public, and sandbox are the only schemas which the `analytics` role can fully manipulate. Both roles have the ability to select from all schemas and tables. 

### Accessing peered VPCs

Some of the GitLab specific ELTs connect to databases which are in peered GCP projects, such as the usage ping. To allow connections, a few actions have been taken:
1. The Kubernetes cluster where the runner executes has been set up to use [IP aliasing](https://cloud.google.com/kubernetes-engine/docs/how-to/ip-aliases), so each pod gets a real routable IP within GCP.
1. A [VPC peering relationship](https://cloud.google.com/vpc/docs/vpc-peering) has been established between the two projects and their networks.
1. A firewall rule has been created in the upstream project to allow access from the runner Kubernetes cluster's pod subnet.

### dbt Coding Conventions

At Gitlab we use dbt for data transformation, as referenced in "Tools" above. What follows are the conventions we use internally. *Inspired by [Fishtown Analytics](https://github.com/fishtown-analytics/corp/blob/master/dbt_coding_conventions.md)*


#### Policy & Procedure

- Reviewers should have 48 hours to complete a review, so plan ahead with the end of your sprint.
- When possible, questions/problems should be discussed with your reviewer before MR time. MR time is by definition the worst possible time to have to make meaningful changes to your models, because you’ve already done all of the work!

#### Model Configuration

- Model-specific attributes (like sort/dist keys) should be specified in the model.
- If a particular configuration applies to all models in a directory, it should be specified in the project.
- In-model configurations should be specified like this:

```python
{{
  config(
    materialized = ’table’,
    sort = ’id’,
    dist = ’id’
  )
}}
```

#### Base Models

- Only base models should select from source tables / views.
- Only a single base model should be able to select from a given source table / view.
- Base models should be placed in a `base/` directory.
- Base models should perform all necessary data type casting.
- Base models should perform all field naming to force field names to conform to standard field naming conventions.
- Source fields that use reserved words must be renamed in base models.

#### Field Naming Conventions

- TBD

#### CTEs (Common Table Expressions)

- All `{{ ref('...') }}` statements should be placed in CTEs at the top of the file.
- Where performance permits, CTEs should perform a single, logical unit of work.
- CTE names should be as verbose as needed to convey what they do.
- CTEs with confusing or notable logic should be commented.
- CTEs that are duplicated across models should be pulled out into their own models.
- CTEs should be formatted like this:

``` sql
WITH events AS (

  ...

),

-- CTE comments go here
filtered_events AS (

  ...

)

SELECT * 
FROM filtered_events
```

#### Style Guide

- Indents should be four spaces (except for predicates, which should line up with the `where` keyword).
- Lines of SQL should be no longer than 80 characters.
- Field names should all be lowercase.
- Function names should all be capitalized.
- The `as` keyword should be used when projecting a field or table name.
- Fields should be stated before aggregates / window functions.
- Ordering and grouping by a number (eg. group by 1, 2) is ok.
- When possible, take advantage of `using` in joins.
- Prefer `union all` to `union` [*](http://docs.aws.amazon.com/redshift/latest/dg/c_example_unionall_query.html).
- *DO NOT OPTIMIZE FOR A SMALLER NUMBER OF LINES OF CODE. NEWLINES ARE CHEAP, BRAIN TIME IS EXPENSIVE*

##### Example Code
```sql
with my_data as (

    SELECT * 
    FROM {{ ref('my_data') }}

),

some_cte as (

    SELECT * 
    FROM {{ ref('some_cte') }}

)

SELECT [distinct]
    field_1,
    field_2,
    field_3,
    CASE
        WHEN cancellation_date is null and expiration_date is not null then expiration_date
        WHEN cancellation_date is null then start_date+7
        ELSE cancellation_date
    END AS canellation_date

    SUM(field_4),
    MAX(field_5)

FROM my_data
JOIN some_cte USING (id)

WHERE field_1 = ‘abc’
  AND (
    field_2 = ‘def’ OR
    field_2 = ‘ghi’
  )

GROUP BY 1, 2, 3
HAVING count(*) > 1
```

#### Testing

- Every model should be tested in a `schema.yml` file
- At minimum, unique, not nullable fields, and foreign key constraints should be tested (if applicable)
- The output of dbt test should be pasted into MRs
- Any failing tests should be fixed or explained prior to requesting a review

#### Docker Compose

1. Clone the repo
1. Customize the MELTANO directories as needed
1. From the main project directory, run `docker-compose up`
1. In your browser, navigate to `localhost:5000/drop_it_like_its_hot` to reset the schema of the database
1. Then navigate to `localhost:5000`. Click on add project, and specify `/meltano/model`

# Contributing to Meltano

We welcome contributions and improvements, please see the [contribution guidelines](CONTRIBUTING.md)

# License

This code is distributed under the MIT license, see the [LICENSE](LICENSE) file.

[docker-compose]: https://docs.docker.com/compose/
