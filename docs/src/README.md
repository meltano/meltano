---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: ELT for the DataOps era"
description: Open source, self-hosted, CLI-first, debuggable, and extensible. Embraces Singer and its library of connectors, and leverages dbt for transformation.
installation:
  primaryAction:
    text: Get started
    link: /docs/getting-started.html
meltanoInit:
  primaryAction:
    text: Learn more about Meltano projects
    link: /docs/project.html
integration:
  primaryAction:
    text: Learn more about data integration using Singer
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
    text: Learn more about containerization using Docker
    link: /docs/containerization.html
ui:
  primaryAction:
    text: Learn more about Meltano UI
    link: /docs/ui.html
---

::: slot installation

# ELT for the DataOps era

Meltano is
[open source](https://gitlab.com/meltano/meltano),
[self-hosted](/docs/production.html),
[CLI-first](/docs/command-line-interface.html),
[debuggable](/docs/command-line-interface.html#debugging), and
[extensible](/docs/plugins.html).

[Pipelines are code](#meltano-init),
ready to be version controlled,
[containerized](#containerization), and
[deployed continuously](/docs/production.html#and-onto-the-production-environment).
Develop and test
[locally](/docs/getting-started.html#local-installation),
then
[deploy in production](/docs/production.html)
along with the built-in
[Airflow integration](/docs/production.html#airflow-orchestrator),
or inside your
[orchestrator of choice](/docs/production.html#meltano-elt).

Meltano [embraces](https://handbook.meltano.com/product/singer) the [Singer](https://www.singer.io/) standard and its community-maintained library of open source
[extractors](https://hub.meltano.com/extractors/) and
[loaders](https://hub.meltano.com/loaders/),
and leverages [dbt](https://www.getdbt.com) for [transformation](#transformation).

:::

::: slot read-on-for-more

Read on for more about
[Meltano projects](/#meltano-init),
[data integration (EL)](/#integration),
[transformation (T)](/#transformation),
[orchestration](/#orchestration),
[containerization](/#containerization), and
[Meltano UI](/#ui).

:::

::: slot installation-code

**Experience it for yourself in just a few minutes,**
or watch the ["from 0 to ELT in 90 seconds" speedrun](https://meltano.com/blog/2021/04/28/speedrun-from-0-to-elt-in-90-seconds/)

```bash
# For these examples to work, ensure that:
# - you are running Linux or macOS
# - Python 3.6, 3.7, 3.8, or 3.9 has been installed
python3 --version

# Create directory for Meltano projects
mkdir meltano-projects
cd meltano-projects

# Install pipx package manager
python3 -m pip install --user pipx
pipx ensurepath

# Install Meltano
pipx install meltano --include-deps
```

Meltano is now ready for its [first project](/#meltano-init)!

:::

::: slot logos

- [![GitLab logo](images/home/logos/gitlab.png)](https://about.gitlab.com/)
- [![HackerOne logo](images/home/logos/hackerone.png)](https://www.hackerone.com/)
- [![Remote logo](images/home/logos/remote.png)](https://remote.com/)
- [![Netlify logo](images/home/logos/netlify.png)](https://www.netlify.com/)
- [![Zapier logo](images/home/logos/zapier.png)](https://zapier.com/)

:::

::: slot meltano-init

## Your Meltano project: a single source of truth

<!-- The following is reproduced from docs/src/project.md -->

At the core of the Meltano experience is your Meltano project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/#integration) and [transformed](/#transformation),
how the pipelines should be [orchestrated](/#orchestration),
and how the various [plugins](/docs/plugins.html) that make up your pipelines should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
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
cd demo-project
```

Your Meltano project is now ready for [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration)!

:::

::: slot integration

## Integration just a few keystrokes away

You can use existing Singer [taps](https://hub.meltano.com/extractors/) and [targets](https://hub.meltano.com/loaders/)
or [easily write your own](/tutorials/create-a-custom-extractor.html) to extract
data from any SaaS tool or database and load it into any data warehouse or file format.

Meltano [manages your tap and target configuration](/docs/configuration.html) for you,
makes it easy to [select which entities and attributes to extract](/docs/integration.html#selecting-entities-and-attributes-for-extraction),
and keeps track of [the incremental replication state](/docs/integration.html#incremental-replication-state),
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
meltano config tap-gitlab set start_date 2021-03-01T00:00:00Z

# Select all attributes of the "tags" entity
meltano select tap-gitlab tags "*"

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
meltano add loader target-postgres --variant meltano

# Configure target-postgres through the environment
export TARGET_POSTGRES_HOST=localhost
export TARGET_POSTGRES_PORT=5432
export TARGET_POSTGRES_USER=meltano
export TARGET_POSTGRES_PASSWORD=meltano
export TARGET_POSTGRES_DBNAME=demo-warehouse

# Add dbt transformer and initialize dbt project
meltano add transformer dbt

# Add PostgreSQL-compatible dbt models for tap-gitlab
meltano add transform tap-gitlab

# Select all attributes of all entities
meltano select tap-gitlab "*" "*"

# Run data integration and transformation pipeline
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

# Start `psql` shell connected to warehouse database
PGPASSWORD=$TARGET_POSTGRES_PASSWORD psql -U $TARGET_POSTGRES_USER -h $TARGET_POSTGRES_HOST -p $TARGET_POSTGRES_PORT -d $TARGET_POSTGRES_DBNAME
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
will look for [DAGs](https://airflow.apache.org/docs/apache-airflow/1.10.14/concepts.html#dags) by default.
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

![Airflow webserver](images/home/airflow-webserver.png)

:::

::: slot containerization

## Instantly containerizable and production-ready

Now that you've got your pipelines running locally, it'll be time to repeat this trick in production!

Since your Meltano project is your [single source of truth](/#meltano-init),
[deploying your pipelines in production](/docs/production.html) is pretty straightforward, but
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
```

Your data has now been extracted and loaded!

:::

::: slot ui

## A UI for management and monitoring

Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

However, a web-based UI is also available for when you want to quickly check the
status and most recent logs of your project's [scheduled pipelines](/#orchestration),
or if you want to give less technical team members or clients the option to [configure](/docs/configuration.html) their
extractors, loaders, and pipelines themselves.

:::

::: slot ui-code

<small>Follow the [project initialization instructions above](/#meltano-init) and then...</small>

```bash
# Start Meltano UI
meltano ui
```

Meltano UI is now available at <http://localhost:5000>!

![Meltano UI](images/home/ui-pipelines.png)

:::
