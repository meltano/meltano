---
sidebar: auto
---

# Guide

## Getting Started

### Requirements

- Python Version >= 3.6.6

### Installation & Setup

#### With Docker

You can run a local copy of Meltano using [docker-compose][https://docs.docker.com/compose/]. Run the following in your project directory:

```bash
# build the project
make

# initialize the db schema
make init_db

# bring up docker-compose
docker-compose up
```

#### Without Docker

You will need to have postgres installed and available >= 10.5.

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

For more info see the [docker-compose.yml](https://gitlab.com/meltano/meltano/blob/master/docker-compose.yml)

### Your First Meltano Project

::: warning Note
**If you want to install Meltano in a venv: virtualenv and pipenv are not supported. Please use `python -m venv venv` to create your virtual environment. See [this issue](https://gitlab.com/meltano/meltano/issues/141).**
:::

After installing `meltano` CLI, you can choose to run meltano against your project.

The gitlab-runner project contains a `meltano.yml` file:

`meltano.yml`

```yml
version: 0.0.0 **
extractors:
- name: tap-gitlab
  url: https://gitlab.com/meltano/tap-gitlab
- name: tap-mysql
  url: https://gitlab.com/meltano/tap-mysql
- name: tap-zendesk
  url: https://gitlab.com/meltano/tap-zendesk
  ...
loaders:
- name: target-snowflake
  url: https://gitlab.com/meltano/target-snowflake
  database: main **
- name: target-postgresql
  url: https://gitlab.com/meltano/target-postgresql
  database: test **
  ...
databases:
- name: main
  username: "$MAIN_WAREHOUSE"
  password: "$MAIN_WAREHOUSE_PW"
  host: "$MAIN_WAREHOUSE_HOST"
  db: "$MAIN_WAREHOUSE_DB"
  type: snowflake
  ...
orchestrate: **
- name: first-to-csv
  extractor: first
  loader: csv
  transformer:
  - first
  ...
```

Your project should contains the following directory structure:

- model - For your `.lookml` files.
- transform - For your local dbt project files.
- analyze - For your `.yml` dashboard files.
- notebook - For your `.ipynb` notebook files.
- orchestrate - For your airflow `.py` files.
- .meltano - A .gitignored directory for internal caching (virtualenvs, pypi packages, generated configuration files, etc.).
- load - A directory where your configs for your loaders are placed. Each config should be in a directory with the name of the loader. e.g. For csv loader, the config would be in `load/target-csv/tap.config.json`. \*\*
- extract - A directory where your configs for your extractors are placed. Each config should be in a directory with the name of the extractor. e.g. For zendesk extractor, the config would be in `extract/tap-zendesk/target.config.json`. \*\*
- .gitignore
- README.md
- meltano.yml - Config file which shows which extractors and loaders, etc. you would like to use and where to find them.

Here is a sample of what your project might look like:

```
.
├── analyze
│   └── zendesk
│       └── zendesk.dashboard.yml
├── dbt_project.yml
├── extract
│   └── tap-...
│       ├── tap.config.json
│       └── tap.properties.json
├── load
│   └── target-...
│       └── target.config.json
├── .meltano
│   ├── dbt
│   │   └── venv
│   ├── extractors
│   │   └── tap-...
│   ├── loaders
│   │   └── target-...
│   ├── model
│   │   ├── base_ticket.lookml
│   │   └── ticket.lookml
│   └── run
│       ├── dbt
│       ├── tap-...
│       └── target-...
├── meltano.yml
├── model
│   └── zendesk
│       ├── zendesk.model.lookml
│       └── zendesk.view.lookml
├── orchestrate
│   ├── dag_1.py
│   ├── dag_2.py
│   ├── dag_3.py
│   ├── dag_4.py
│   └── dag_5.py
├── packages.yml
├── profiles.yml
└── transform
    └── tap-zendesk
        └── base.sql
```

## Overview

The Meltano product consists of three key components:

1. A SQL based data store, for example [PostgreSQL](https://www.postgresql.org/) or [Cloud SQL](https://cloud.google.com/sql/). We recommend using Postgres for [review apps](https://about.gitlab.com/features/review-apps/) and a more durable and scalable service for production.
1. This project, [`meltano`](https://gitlab.com/meltano/meltano), which contains the ELT scripts and CI jobs to refresh the data warehouse from the [configured sources](https://gitlab.com/meltano/meltano/master/data_sources.md). Typically configured to run on a [scheduled CI job](https://docs.gitlab.com/ce/user/project/pipelines/schedules.html) to refresh the data warehouse from the configured sources.
1. The [`meltano-elt`](https://gitlab.com/meltano/meltano-elt) container, which includes the necessary dependencies for the ELT scripts. Used as the base image for the CI jobs.

As development progresses, additional documentation on getting started along with example configuration and CI scripts will become available.

It is expected that the Meltano project will have many applications managed in the top level of the project. Some or parts of these applications could be useful to many organizations, and some may only be useful within GitLab. We have no plans on weighing the popularity of an individual application at the top level of the Meltano project for inclusion/exclusion.

**Notes**

- _Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields._
- _The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription._

### Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the data life cycle.

Our CLI tool provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data life cycle.

#### Meltano Schema

Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

#### Create Schema and Roles

Create and grant usage for a database schema.

### Meltano Model

Meltano uses models based on the [LookML](https://docs.looker.com/data-modeling/learning-lookml/lookml-terms-and-concepts#model) language. They allow you to model your data so you can easily analyze and visualize it in Meltano UI.

### Meltano Transform

### dbt

Meltano uses [dbt](https://docs.getdbt.com/) to transform the source data into the `analytics` schema, ready to be consumed by models.

[Fishtown wrote a good article about what to model dynamically and what to do in dbt transformations](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304).

#### Python scripts

In certain circumstances transformations cannot be done in dbt (like API calls), so we use python scripts for these cases.

### Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.

#### Loading a CSV:

> Notes:
>
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
>
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

- `meltano/meltano`: Contains the API, CLI, and Meltano UI. This image should be deployed as Meltano UI.
- `meltano/meltano/runner`: Contains the CLI and extra runner specific binaries. This image should be used on the CI runner.
- `meltano/meltano/singer_runner`: **DEPRECATED: Use `meltano/meltano/runner` instead** Contains the CLI, and all curated taps/targets pre-installed.

> Notes: These images are base images used as the basis of other images.

- `meltano/meltano/cli`: Contains the meltano cli
- `meltano/meltano/base`: Contains the requirements for `meltano/meltano`

## Best practices

### How to use sub pipelines to effectively create a DAG like architecture

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

## Release

Meltano uses [semver](https://semver.org/) as its version number scheme.

### Requirements

Meltano has a number of dependencies for the deployment toolchain that are required when performing a release. If you haven't already, please run the following command to install everything:

```bash
pip install '.[dev]'
```

### Release process

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.

```bash
$ git fetch origin
$ git checkout -b release-next origin/master
$ changelog view ;; make sure to validate the CHANGELOG changes
$ make release
$ git push --tags
$ git push origin release-next
```

Create a merge request from `release-next` targeting `master` and make sure to `delete the source branch when the changes are merged`.
Make sure to link to the pipeline that does the actual deployment: go to the commit's pipelines tab and select the one that has the **publish** stage.

## Contributing to Meltano

We welcome contributions and improvements, please see the contribution guidelines below:

### Code style

Meltano uses [Black](https://github.com/ambv/black) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

You can also have black run automatically using a `git` hook. See https://github.com/ambv/black#version-control-integration for more details.

### Merge Requests

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer should approve the merge request
1. Once approved, the merge request can be merged by any Meltano maintainer

### Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

#### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.

# From Old About Section

We believe that information is the foundation of good decisions, and that companies of all sizes deserve insights into their operations. So Meltano provides broad, democratized access to detailed operational metrics, driving better decisions and shortening decision cycle time across the entire enterprise.

In addition, we believe that the information a business uses to make decisions must come from all parts of that business. Meltano joins data from multiple systems used by Sales, Marketing, Product and others, thereby providing a comprehensive view of the relationship between business activities, associated costs, and customer long-term value.

A data analyst or scientist should be able to easily use Meltano to add whatever data they need by writing the ELT, know the jobs that are running, and then analyze the data within Meltano UI. It should enable individual data people to own the full stack of their analysis, even [if they’re not engineers](https://multithreaded.stitchfix.com/blog/2016/03/16/engineers-shouldnt-write-etl/).

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