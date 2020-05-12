---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: open source data pipelines"
description: Meltano is an open source platform for building, running & orchestrating Singer- and dbt-based ELT pipelines, that you can run locally or host on any cloud. Use existing Singer taps and targets or easily write your own to extract data from any SaaS tool or database and load it into any data warehouse or file format.
installation:
  primaryAction:
    text: Install now
    link: /docs/installation.html
integration:
  primaryAction:
    text: Learn more
    link: /plugins/extractors/
transformation:
  primaryAction:
    text: Learn more
    link: /docs/transforms.html
orchestration:
  primaryAction:
    text: Learn more
    link: /docs/orchestration.html
---

::: slot installation

# Open source data pipelines

Meltano is an [open source](https://gitlab.com/meltano/meltano) platform for
building, running & orchestrating ELT pipelines built out of [Singer](https://www.singer.io/) taps and targets and [dbt](https://www.getdbt.com) models, that you can [run locally or host on any cloud](/docs/installation.html).

Scroll down for details on [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration).

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
meltano init demo-project # --no_usage_stats
```

Your Meltano project is now ready for [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration)!

:::

::: slot integration

## Integration just a few keystrokes away

Use existing Singer [taps](/plugins/extractors/) and [targets](/plugins/loaders/)
or [easily write your own](/tutorials/create-a-custom-extractor.html) to extract
data from any SaaS tool or database and load it into any data warehouse or file format.

Meltano manages your [tap and target configuration](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#config-file)
for you and keeps track of [the state of your extraction](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file),
so that subsequent ELT runs with the same job ID will always pick up right where
the previous run left off.

Scroll down to learn more about [adding extractors and loaders to your project](#meltano-add).
:::

::: slot integration-code

```bash
# Before you use any `meltano` command, ensure that:
# - you have activated the virtual environment
source ../.venv/bin/activate
# - you have navigated to your Meltano project directory
cd demo-project

# Add GitLab extractor to your project
meltano add extractor tap-gitlab

# Configure tap-gitlab
meltano config tap-gitlab set projects meltano/meltano
meltano config tap-gitlab set start_date 2018-01-01

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
export PG_PORT=5432
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

::: slot meltano-add

## How to: add extractors and loaders to your project

Like all types of plugins, extractors and loaders can be added to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add).
Plugins that are already known to Meltano can be added by simply specifying their `type` and `name`, while adding a plugin that Meltano isn't familiar with yet requires adding the `--custom` flag.

To find out what plugins are already known to Meltano and supported out of the box, you can use [`meltano discover`](/docs/command-line-interface.html#discover), with an optional pluralized `plugin type` argument.
You can also check out the lists of supported [extractors](/plugins/extractors/) and [loaders](/plugins/loaders/) on this website.

If the Singer tap or target you'd like to use with Meltano doesn't show up in any of these places, you're going to want to add a custom plugin.
When you run `meltano add --custom [type] [name]`, Meltano will ask you some additional questions to learn where the package can be found, how to interact with it, and how it can be expected to behave.

If the tap or target in question is listed on Singer's [index of taps](https://www.singer.io/#taps) or [targets](https://www.singer.io/#targets), simply providing the package name as `name`, `pip_url`, and `executable` should suffice. If it's a tap or target you have developed or are developing yourself, you'll want to set `pip_url` to either a Git URL or local directory path. To find out what `settings` a tap or target supports, reference its documentation. If the `capabilities` a tap supports are not described in its documentation, try [one of these tricks](/docs/contributor-guide.html#how-to-test-a-tap).

Once your plugin has been added, it will be ready for [configuration](/docs/command-line-interface.html#config)!
:::

::: slot meltano-add-code

```bash
# List extractors and loaders known to Meltano
meltano discover extractors
meltano discover loaders

# Add a known extractor or loader by name
meltano add extractor tap-salesforce
meltano add loader target-snowflake

# Add an unknown (custom) extractor or loader
meltano add --custom extractor tap-covid-19
```

```bash
# Specify namespace, which will serve as the:
# - target database schema when used with
#   loader target-postgres or target-snowflake
# - prefix for configuration environment variables
# - identifier to find related/compatible plugins
(namespace): tap_covid_19

# Specify `pip install` argument, for example:
# - PyPI package name:
(pip_url): tap-covid-19
# - VCS URL:
(pip_url): git+https://github.com/singer-io/tap-covid-19.git
# - local directory, in editable/development mode:
(pip_url): -e extract/tap-covid-19

# Specify executable name
(executable): tap-covid-19

# Specify supported Singer features (executable flags)
(capabilities): catalog,discover,state

# Specify supported settings (`config.json` keys)
(settings): api_token,user_agent,start_date
```

Your extractor or loader is now ready for [configuration](/docs/command-line-interface.html#config)!

:::