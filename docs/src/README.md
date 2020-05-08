---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: open source data pipelines"
description: Meltano is an open source platform for building, running & orchestrating Singer- and dbt-based ELT pipelines, that you can run locally or host on any cloud. Use existing Singer taps and targets or easily write your own to extract data from any SaaS tool or database and load it into any data warehouse or file format.
installation:
  primaryAction:
    text: Get Started
    link: /docs/getting-started.html
integration:
  primaryAction:
    text: Learn More
    link: /plugins/extractors/
transformation:
  primaryAction:
    text: Learn More
    link: /docs/transforms.html
orchestration:
  primaryAction:
    text: Learn More
    link: /docs/orchestration.html
---

::: slot installation

# Open source data pipelines

Meltano is an [open source](https://gitlab.com/meltano/meltano) platform for
building, running & orchestrating ELT pipelines built out of [Singer](https://www.singer.io/) taps and targets and [dbt](https://www.getdbt.com) models, that you can [run locally or host on any cloud](/docs/self-hosted-installation.html).

Scroll down for details on [integration](/#integration-just-a-few-keystrokes-away), [transformation](/#transformation-as-a-first-class-citizen), and [orchestration](/#orchestration-right-out-of-the-box).

:::

::: slot installation-code

```bash
# For these examples to work, ensure that:
# - you are running Linux or macOS
# - Python 3.6 or 3.7 has been installed
python3 --version

# Create directory for Meltano projects
mkdir meltano-projects
cd meltano-projects

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Meltano
pip3 install meltano

# Initialize Meltano project "demo-project"
meltano init demo-project
```

Your Meltano project is now ready!

:::

::: slot integration

## Integration just a few keystrokes away

Use existing Singer [taps](/plugins/extractors/) and [targets](/plugins/loaders/)
or [easily write your own](/tutorials/create-a-custom-extractor.html) to extract
data from any SaaS tool or database and load it into any data warehouse or file format.

Meltano manages your [tap and target configuration](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#config-file)
for you and keeps track of [the state of you extraction](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file),
so that subsequent ELT runs with the same job ID will always pick up right where
the previous run left off.
:::

::: slot integration-code

```bash
# Before you use any `meltano` command, ensure that:
# - you have navigated to your Meltano project directory
cd demo-project
# - you have activated the virtual environment
source ../.venv/bin/activate

# Add GitLab extractor to your project
meltano add extractor tap-gitlab

# Configure tap-gitlab
meltano config tap-gitlab set projects meltano/meltano
meltano config tap-gitlab set start_date 2018-01-01

# Add JSONL loader
meltano add loader target-jsonl

# Run data integration pipeline
mkdir -p output
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

A Meltano project's `transform` directory contains a full-fledged
[dbt project](https://docs.getdbt.com/docs/building-a-dbt-project/projects),
so you can easily install [existing dbt models from packages](https://hub.getdbt.com/)
or [write your own](/tutorials/create-custom-transforms-and-models.html#adding-custom-transforms).

:::

::: slot transformation-code

```bash
# For these examples to work, ensure that:
# - you have PostgreSQL running somewhere
# - you have created a new database
# - you change the configuration below as appropriate

# Add PostgreSQL loader
meltano add loader target-postgres

# Configure target-postgres through the environment
export PG_ADDRESS=localhost
export PG_PORT=5502
export PG_USERNAME=meltano
export PG_PASSWORD=meltano
export PG_DATABASE=demo-warehouse

# Add PostgreSQL-compatible dbt models for tap-gitlab
meltano add transformer dbt
meltano add transform tap-gitlab

# Run data integration and transformation pipeline
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

# Connect to database
PGPASSWORD=$PG_PASSWORD psql -U $PG_USERNAME -h $PG_ADDRESS -p $PG_PORT -d $PG_DATABASE
```

```sql
-- Read latest tag
SELECT * FROM analytics.gitlab_tags LIMIT 1;
```

```
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

Airflow will look for [DAGs](https://airflow.apache.org/docs/stable/concepts.html#dags)
in a Meltano project's `orchestrate/dags` directory, so if the
[default Meltano DAG](https://gitlab.com/meltano/meltano/blob/master/src/meltano/core/bundle/dags/meltano.py)'s
behavior of simply running `meltano elt` on a schedule is not going to cut it,
you can easily modify it or add your own.

:::

::: slot orchestration-code

```bash
# Schedule pipelines
meltano schedule gitlab-to-jsonl tap-gitlab target-jsonl @hourly
meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily --transform=run

# Add Airflow orchestrator
meltano add orchestrator airflow

# Start the Airflow scheduler in the background
meltano invoke airflow scheduler -D

# Optional: start the Airflow web interface (add -D to move to background)
meltano invoke airflow webserver
open http://localhost:8080
```

Your pipelines have now been scheduled!

:::