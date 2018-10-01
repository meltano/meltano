[![pipeline status](https://gitlab.com/meltano/meltano/badges/master/pipeline.svg)](https://gitlab.com/meltano/meltano/commits/master)

# Meltano

## Overview
Meltano is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.
It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-engineering-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

## Solution
1. _M:_ Provide Modeling via [Meltano Model and Analyze (MMA)](https://gitlab.com/meltano/meltano/tree/master/src/meltano_ui), a modeling layer, which works via [lkml files](https://docs.looker.com/data-modeling/getting-started/model-development).
1. _E, L:_ Provide a solid and extract, load structure via the singer spec.
  1. [Getting Started](https://github.com/singer-io/getting-started)
  1. [Specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification)
1. _T:_ Provide transforms via [DBT](https://www.getdbt.com/)
1. _A:_ Provide Analysis via [Meltano Model and Analyze (MMA)](https://gitlab.com/meltano/meltano/tree/master/src/meltano_ui), an analysis layer, which works via [lkml files](https://docs.looker.com/data-modeling/getting-started/model-development).
1. _N:_ Provide Notebooking via [Jupyter Notebooks](https://jupyter.org/)
1. _O:_ Provide Orchestration via [GitLab CI](https://about.gitlab.com/features/gitlab-ci-cd/)
  1. Provide a way to easily generate orchestration files ([gitlab-ci.yml](https://docs.gitlab.com/ee/ci/yaml/) files)
1. We provide tools and specs to create, extractors, loaders and transformers. 
1. We provide tools to run extractors in your orchestrator seamlessly via [containerization](https://www.digitalocean.com/community/tutorials/the-docker-ecosystem-an-overview-of-containerization).


## Team Personas / The Problem
Meltano is solving a use case for 3 different team personas, which simultaneously presents the problem we are trying to solve:

1. Team 1: The Data Engineering Team
  * This team has data engineers on hand who have time and knowhow to write high quality python. 
  * They have explored many different tools and currently use a mixture of different tools for getting the job done. 
  * This team needs:
    1. A tool like [Stitch](https://www.stitchdata.com/) to choose and run extractors and loaders (known as taps and targets). 
    1. A transformation tool like DBT to transform the data. 
    1. A modeling and analysis layer to dashboard their transformations in charts for the executive teams.
    1. A modeling and analysis layer for their data analysts to answer questions.
    1. A orchestration tool to run these orchestrations such as Airflow or GitLab CI.
  * The problems they will face:
    1. Expense: 
      1. Looker is expensive, and running many different tools together can get very expensive. 
    1. Scope:
      1. You want everyone in the company to be able to see the results of that data which is hard when the tools are too expensive to allow access to everyone.
    1. Complexity:
      1. This solution already involves a ton of customizations including creating lkml files, and writing DBT transforms, as well as pipeline creation via yml files or python files for GitLab CI.
  * The solutions to this problem is Meltano:
    1. Expense:
      1. Meltano is open source, so the cost is far less.
      1. Meltano is one tool for the complete data science life cycle, compacting the entire multi-expense toolchain into one tool. 
    1. Scope:
      1. Because Meltano is open source, there isn't a cost to adding users.
    1. Complexity:
      1. Meltano will provide tools to automate the complex scripting parts of the data science workflow.
        1. Singer taps and targets are a great spec, but not complete in their implementation. 
          1. We provide a complete working open source implementation of popular taps and targets, that we support and use ourselves. 
        1. Singer taps and targets are missing tests or the taps are not open source.
          1. We've added open source tests to singer taps and targets.
        1. Singer taps are missing some implementations
          1. We provide implementations of all of our internal worksflows open source.
        1. Building CI Workflows for GitLab CI is complex via yml files.
          1. We provide a GitLab CI builder to help build a great data science orchestration so anyone can build a workflow.
        1. Running Singer taps and targets is sometimes impossible in a single tenant solution due to the need for oauth2
          1. We remove oauth2 where we can and replace with API key authentication so all our taps and targets can operate behind a firewall.
        1. Dockerizing singer taps and targets is ideal for orchestrating them. 
          1. We provide a documentated and open source way to dockerize your singer taps and targets. 
      1. Our goal is to take as much configuration step out of your data science lifecycle. 
  * Conclusion: Meltano will reduce complexity, and time to get from extract to load to transform to analyze.
<!-- 1. Team 2: The Data Analysis Team
  * This team has limited resources to a complex setup in both time and programming experience. 
  * They have explored a wide range of tools and currently use a mixture of Talend -->

## How to Install and Run Meltano  

### With Docker  

You can run local copy of Meltano using [docker-compose][].

```bash
# build the project
make

# initialize the db schema
make init_db

# bring up docker-compose
docker-compose up
```

### Without Docker
```bash
python -m virtualenv ~/path/to/melt_venv 
source ~/path/to/melt_venv/bin/activate
pip install -e '.[api]' 
python -m meltano.api
```

This will start:

- The front-end UI at [http://localhost:8080]()
- The api server [http://localhost:5000]() and an accompanying Postgres DB
- A mock warehouse Postgres DB

For more info see the [docker-compose.yml]()

## Resources
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

