---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: open source ELT"
description: Meltano is an open source platform for building, running & orchestrating ELT pipelines built out of Singer taps and targets and dbt models, that you can run locally or easily deploy in production. Our goal is to make the power of data integration available to all by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.
installation:
  primaryAction:
    text: Get started
    link: /docs/getting-started.html
meltanoInit:
  primaryAction:
    text: Learn more about the Meltano project
    link: /docs/project.html
integration:
  primaryAction:
    text: Learn more about data integration using Meltano
    link: /docs/integration.html
transformation:
  primaryAction:
    text: Learn more about transformation using dbt
    link: /docs/transforms.html
orchestration:
  primaryAction:
    text: Learn more about orchestration using Airflow
    link: /docs/orchestration.html
containerization:
  primaryAction:
    text: Learn more about deployment in production
    link: /docs/production.html
---

::: slot installation

# Meltano: open source ELT

Meltano is an [open source](https://gitlab.com/meltano/meltano) platform for
building, running & orchestrating ELT pipelines built out of [Singer](https://www.singer.io/) taps and targets and [dbt](https://www.getdbt.com) models, that you can [run locally](/docs/installation.html) or [easily deploy in production](/docs/production.html).

Our goal is to [make the power of data integration available to all](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/)
by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.

Scroll down for details on
[Meltano projects](/#meltano-init),
[integration](/#integration),
[transformation](/#transformation),
[orchestration](/#orchestration), and
[containerization](/#containerization).

:::

::: slot installation-code

**Give it a try and be up and running in minutes!**

```bash
# For these examples to work, ensure that:
# - you are running Linux or macOS
# - Python 3.6 or 3.7 (NOT 3.8) has been installed
python3 --version

# Create directory for Meltano projects
mkdir meltano-projects
cd meltano-projects

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Meltano
pip3 install meltano
```

Meltano is now ready for its [first project](/#meltano-init)!

:::

::: slot meltano-init

## The Meltano project: your single source of truth

<!-- The following is reproduced from docs/src/project.md -->

At the core of the Meltano experience is the Meltano project,
which represents the single source of truth regarding your data pipelines:
how data should be [integrated](/#integration) and [transformed](/#transformation),
how the pipelines should be [orchestrated](/#orchestration),
and how the various components should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init).
:::

::: slot meltano-init-code

<small>Follow the [installation instructions above](/#installation) and then...</small>

```bash
# Initialize a new Meltano project
meltano init demo-project
```

Your Meltano project has now been initialized in the `demo-project` directory!

```bash
# Before using a `meltano` command, ensure that:
# - you have navigated to your Meltano project
cd demo-project
# - you have activated the virtual environment
source ../.venv/bin/activate
```

Your Meltano project is now ready for [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration)!

:::

::: slot integration

## Integration just a few keystrokes away

You can use existing Singer [taps](/plugins/extractors/) and [targets](/plugins/loaders/)
or [easily write your own](/tutorials/create-a-custom-extractor.html) to extract
data from any SaaS tool or database and load it into any data warehouse or file format.

Meltano [manages your tap and target configuration](/docs/configuration.html) for you,
makes it easy to [select which entities and attributes to extract](/docs/integration.html#selecting-entities-and-attributes-for-extraction),
and keeps track of [the state of your extraction](/docs/command-line-interface.html#pipeline-state),
so that subsequent pipeline runs with the same job ID will always pick up right where
the previous run left off.

Scroll down to learn more about [transformation](/#transformation) and [orchestration](/#orchestration).
:::

::: slot integration-code

<small>Follow the [project initialization instructions above](/#meltano-init) and then...</small>

```bash
# Add GitLab extractor to your project
meltano add extractor tap-gitlab

# Configure tap-gitlab to extract data from...
# - the https://gitlab.com/meltano/meltano project
meltano config tap-gitlab set projects meltano/meltano
# - going back to May 1st, 2020
meltano config tap-gitlab set start_date 2020-05-01T00:00:00Z

# Add JSONL loader
meltano add loader target-jsonl

# Ensure target-jsonl output directory exists
mkdir -p output

# Run data integration pipeline
meltano elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl

# Read latest tag
head -n 1 output/tags.jsonl
```

```json
{"name": "LATEST_TAG_NAME", "message": "", "target": "LATEST_TAG_SHA", "commit_id": "LATEST_TAG_SHA", "project_id": 7603319}
```

Your data has now been extracted and loaded!

:::

::: slot transformation

## Transformation as a first-class citizen

Once your raw data has arrived in your data warehouse, its schema will likely
need to be transformed to be more appropriate for analysis.

Meltano helps you out here as well, with built-in (but optional!) support for running
[dbt](https://www.getdbt.com/) models as part of your pipeline.

When you add the `dbt` transformer to your project, a full-fledged
[dbt project](https://docs.getdbt.com/docs/building-a-dbt-project/projects)
will automatically be initialized in the `transform` directory.
Any transform plugins added to your Meltano project will automatically be
added to the dbt project as well, but you can easily install
[existing dbt models from packages](https://hub.getdbt.com/)
or [write your own](/tutorials/create-custom-transforms-and-models.html#adding-custom-transforms).

:::

::: slot transformation-code

<small>Follow the [integration instructions above](/#integration) and then...</small>

```bash
# For these examples to work, ensure that:
# - you have PostgreSQL running somewhere
# - you have created a new database
# - you change the configuration below as appropriate

# Add PostgreSQL loader
meltano add loader target-postgres

# Configure target-postgres through the environment
export PG_ADDRESS=localhost
export PG_PORT=5432
export PG_USERNAME=meltano
export PG_PASSWORD=meltano
export PG_DATABASE=demo-warehouse

# Add dbt transformer and initialize dbt project
meltano add transformer dbt

# Add PostgreSQL-compatible dbt models for tap-gitlab
meltano add transform tap-gitlab

# Run data integration and transformation pipeline
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

# Start `psql` shell connected to warehouse database
PGPASSWORD=$PG_PASSWORD psql -U $PG_USERNAME -h $PG_ADDRESS -p $PG_PORT -d $PG_DATABASE
```

```sql
-- Read latest tag
SELECT * FROM analytics.gitlab_tags LIMIT 1;
```

```output
 project_id |                commit_id                 | tag_name |                  target                  | message
------------+------------------------------------------+----------+------------------------------------------+---------
    7603319 | LATEST_TAG_SHA | LATEST_TAG_NAME  | LATEST_TAG_SHA |
(1 row)
```

Your data has now been extracted, loaded, and transformed!

:::

::: slot orchestration

## Orchestration right out of the box

Once you've managed to successfully run your ELT pipeline once, you'll probably
want to run it again, and again, and again.

Meltano lets you set up pipeline schedules that can then automatically be fed
to and run by a supported orchestrator like [Apache Airflow](https://airflow.apache.org/).

When you add the `airflow` orchestrator to your project, a
[Meltano DAG generator](https://gitlab.com/meltano/files-airflow/-/blob/master/bundle/orchestrate/dags/meltano.py)
will automatically be added to the `orchestrate/dags` directory, where Airflow
will look for [DAGs](https://airflow.apache.org/docs/stable/concepts.html#dags) by default.
If the default behavior of simply running [`meltano elt`](/docs/command-line-interface.html#elt) on a
schedule is not going to cut it, you can easily modify the DAG generator or add your own.

:::

::: slot orchestration-code

<small>Follow the [transformation instructions above](/#transformation) and then...</small>

```bash
# Schedule pipelines
meltano schedule gitlab-to-jsonl tap-gitlab target-jsonl @hourly
meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily --transform=run

# List scheduled pipelines
meltano schedule list

# Add Airflow orchestrator and default DAG generator
meltano add orchestrator airflow

# Start the Airflow scheduler (add `-D` to background)
meltano invoke airflow scheduler
```

Your pipelines will now run on a schedule!

```bash
# Start the Airflow web interface (add `-D` to background)
meltano invoke airflow webserver
```

Airflow is now available at <http://localhost:8080>!

:::

::: slot containerization

## Instantly containerizable and production-ready

Now that you've got your pipelines running locally, it'll be time to repeat this trick in production!

Since your Meltano project is your [single source of truth](/#meltano-init),
moving your data pipelines to a new environment is as easy as
[getting your project onto the environment](/docs/production.html#your-meltano-project),
[installing Meltano](/docs/production.html#installing-meltano), and
[installing your project's plugins](/docs/production.html#installing-plugins).
Then, after you decide
[where to store your pipeline state and other metadata](/docs/production.html#storing-metadata) and
[how to manage your environment-specific and sensitive configuration](/docs/production.html#managing-configuration),
you'll be able to use [the `meltano` command](/docs/command-line-interface.html) to
[run your ELT pipelines](/docs/production.html#meltano-elt) or
[start an orchestrator](/docs/production.html#airflow-orchestrator)
just like you did locally.

<!-- The following is reproduced in docs/src/docs/production.md#containerized-meltano-project with minor edits -->

While you can get Meltano, your project, and all of its plugins onto a new environment one-by-one,
you can greatly simplify this process (and prevent issues caused by inconsistencies between environments!)
by wrapping them all up into a project-specific
[Docker container image](https://www.docker.com/resources/what-container):
"a lightweight, standalone, executable package of software that includes everything
needed to run an application: code, runtime, system tools, system libraries and settings."

This image can then be used on any environment running [Docker](https://www.docker.com/)
(or a compatible tool like [Kubernetes](https://kubernetes.io/)) to directly
[run](https://docs.docker.com/engine/reference/commandline/run/)
[`meltano` commands](/docs/command-line-interface.html)
in the context of your project, without needing to separately manage the installation of
Meltano, your project's plugins, or any of their dependencies.

If you're storing your Meltano project in version control on a
platform like [GitLab](https://about.gitlab.com) or [GitHub](https://github.com),
you can set up a CI/CD pipeline to run every time a change is made to your project,
which can automatically [build](https://docs.docker.com/engine/reference/commandline/build/)
a new version of the image and [push](https://docs.docker.com/engine/reference/commandline/push/)
it to a container registry.
The image can then be [pulled](https://docs.docker.com/engine/reference/commandline/pull/)
from that registry onto any local or cloud environment on which you'd like to run your project's pipelines.

If you'd like to containerize your Meltano project, you can easily add the
appropriate `Dockerfile` and `.dockerignore` files to your project by adding the
[`docker` file bundle](https://gitlab.com/meltano/files-docker).

If you'd like to use [GitLab CI/CD](https://docs.gitlab.com/ee/ci/) to continuously
build your Meltano project's Docker image and push it to GitLab's built-in
[Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/),
you can add the appropriate `.gitlab-ci.yml` and `.gitlab/ci/docker.gitlab-ci.yml`
files to your project by adding the
[`gitlab-ci` file bundle](https://gitlab.com/meltano/files-gitlab-ci).

:::

::: slot containerization-code

<small>Follow the [project initialization instructions above](/#meltano-init) and then...</small>

```bash
# For these examples to work, ensure that
# Docker has been installed
docker --version

# Add Docker files to your project
meltano add files docker

# Build Docker image containing
# Meltano, your project, and all of its plugins
docker build --tag meltano-demo-project:dev .
```

Your `meltano-demo-project:dev` Docker image is now ready for its first container!

```bash
# View Meltano version
docker run meltano-demo-project:dev --version

# Run gitlab-to-jsonl pipeline with
# mounted volume to exfiltrate target-jsonl output
docker run \
  --volume $(pwd)/output:/project/output \
  meltano-demo-project:dev \
  elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl

# Run gitlab-to-postgres pipeline with
# target-postgres configuration in environment
docker run \
  --env PG_ADDRESS=host.docker.internal \
  --env PG_PORT=5432 \
  --env PG_USERNAME=meltano \
  --env PG_PASSWORD=meltano \
  --env PG_DATABASE=demo-warehouse \
  meltano-demo-project:dev \
  elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres
```

Your Meltano project can now be continuously delivered to a container registry!

```bash
# For these examples to work, ensure that
# you have an account on GitLab.com or
# a self-hosted GitLab instance with
# GitLab CI/CD and Container Registry enabled

# Add GitLab CI/CD files to your project
meltano add files gitlab-ci

# Initialize Git repository, if you haven't already
git init

# Add and commit all files
git add -A
git commit -m "Set up Meltano project with Docker and GitLab CI"

# Push to GitLab, which will automatically create
# a new private project at the specified path
NAMESPACE="<your-gitlab-username-or-group>"
git push git@gitlab.com:$NAMESPACE/meltano-demo-project.git master
```

GitLab CI/CD is now building your Meltano project's dedicated Docker image,
which will be available at `registry.gitlab.com/$NAMESPACE/meltano-demo-project:latest`
once the CI/CD pipeline completes!

:::
