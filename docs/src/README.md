---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: open source data pipelines"
description: Meltano is an open source platform for building, running & orchestrating ELT pipelines built out of Singer taps and targets and dbt models, that you can run locally or host on any cloud. Our goal is to make the power of data integration available to all by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.
installation:
  primaryAction:
    text: Install now
    link: /docs/installation.html
# integration:
#   primaryAction:
#     text: Learn more
#     link: /#meltano-add
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

Our goal is to [make the power of data integration available to all](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/)
by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.

Scroll down for details on [Meltano projects](/#meltano-init), [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration).

:::

::: slot installation-code

**Give it a try and be up and running in minutes!**

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
```

Meltano is now ready for its [first project](/#meltano-init)!

:::

::: slot meltano-init

## The Meltano project: your single source of truth

At the core of the Meltano experience is the Meltano project,
which respresents the single source of truth regarding your data pipelines:
how data should be [integrated](/#integration) and [transformed](/#transformation),
how the pipelines should be [orchestrated](/#orchestration),
and how the various components should be [configured](/#meltano-config).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can use it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and delivery.

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init),
which will create a new directory with:

- a `meltano.yml` file that will list any [`plugins` you'll add](/#meltano-add) and [pipeline `schedules` you'll create](/#orchestration),
- a `transform` directory containing a full-fleged [dbt project](https://docs.getdbt.com/docs/building-a-dbt-project/projects) (that you're free to delete if you don't plan on using the [`dbt` transformer](/#transformation)),
- an [`orchestrate/dags/meltano.py`](https://gitlab.com/meltano/meltano/blob/master/src/meltano/core/bundle/dags/meltano.py) file defining [Airflow DAGs](https://airflow.apache.org/docs/stable/concepts.html#dags) to run your [scheduled pipelines](/#orchestration) (that you're free to delete if you don't plan on using the [`airflow` orchestrator](/#orchestration)),
- stubs for `.gitignore`, `docker-compose.yml`, `README.md`, and `requirements.txt` for you to edit (or delete) as appropriate, and
- empty `model`, `extract`, `load`, `analyze`, and `notebook` directories for you to use (or delete) as you please.

Note that whenever you [add a new plugin](/#meltano-add), it will be installed into your project's (gitignored) `.meltano` directory automatically.
However, when you clone or pull an existing Meltano project from version control, you'll want to explicitly run [`meltano install`](/docs/command-line-interface.html#install) before any other `meltano` commands to install (or update) all plugins specified in `meltano.yml`.
:::

::: slot meltano-init-code

```bash
# Initialize a new Meltano project in the
# "demo-project" directory, and...
# - share anonymous usage data with the Meltano team
#   to help them gauge interest in Meltano and its
#   features and drive development time accordingly:
meltano init demo-project
# - OR don't share anything with the Meltano team
#   about this specific project:
meltano init demo-project --no_usage_stats
# - OR don't share anything with the Meltano team
#   about any project I initialize ever:
SHELLRC=~/.$(basename $SHELL)rc # ~/.bashrc, ~/.zshrc, etc
echo "export MELTANO_DISABLE_TRACKING=1" >> $SHELLRC
meltano init demo-project # --no_usage_stats is implied
```

```output
Project demo-project has been created.

Next steps:
  cd demo-project
  Visit https://meltano.com/ to learn where to go from here
```

Your Meltano project has now been initialized in the `demo-project` directory!

```shell
# Before you use any `meltano` command, ensure that:
# - you have navigated to your Meltano project directory
cd demo-project
# - you have activated the virtual environment
source ../.venv/bin/activate

# If this were an existing Meltano project you just
# cloned or pulled, install any missing plugins
# meltano install
```

Your Meltano project is now ready for [integration](/#integration), [transformation](/#transformation), and [orchestration](/#orchestration)!

:::

::: slot integration

## Integration just a few keystrokes away

You can use existing Singer [taps](/plugins/extractors/) and [targets](/plugins/loaders/)
or [easily write your own](/tutorials/create-a-custom-extractor.html) to extract
data from any SaaS tool or database and load it into any data warehouse or file format.

Meltano [manages your tap and target configuration](/#meltano-config) for you,
makes it easy to [select which entities and properties to extract](/#meltano-select),
and keeps track of [the state of your extraction](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file),
so that subsequent pipeline runs with the same job ID will always pick up right where
the previous run left off.

Scroll down to learn more about [transformation](/#transformation) and [orchestration](/#orchestration), or jump straight to:
- [Adding extractors and loaders to your project](/#meltano-add)
- [Managing the configuration of your plugins](/#meltano-config)
- [Selecting entities and properties to extract](/#meltano-select)
:::

::: slot integration-code

```bash
# Add GitLab extractor to your project
meltano add extractor tap-gitlab

# Configure tap-gitlab to extract data from...
# - the https://gitlab.com/meltano/meltano project
meltano config tap-gitlab set projects meltano/meltano
# - going back to May 1st, 2020
meltano config tap-gitlab set start_date 2020-05-01

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

Airflow will look for [DAGs](https://airflow.apache.org/docs/stable/concepts.html#dags)
in a Meltano project's `orchestrate/dags` directory, so if the
[default Meltano DAG](https://gitlab.com/meltano/meltano/blob/master/src/meltano/core/bundle/dags/meltano.py)'s
behavior of simply running [`meltano elt`](/docs/command-line-interface.html#elt) on a schedule is not going to cut it,
you can easily modify it or add your own.

:::

::: slot orchestration-code

```bash
# Schedule pipelines
meltano schedule gitlab-to-jsonl tap-gitlab target-jsonl @hourly
meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily --transform=run

# Add Airflow orchestrator
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

::: slot meltano-add

## Adding extractors and loaders to your project

Like all types of plugins, extractors and loaders can be added to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add).
Plugins that are already [known to Meltano](/docs/contributor-guide.html#known-plugins) can be added by simply specifying their `type` and `name`, while adding a plugin that Meltano isn't familiar with yet requires adding the `--custom` flag.

To find out what plugins are already known to Meltano and supported out of the box, you can use [`meltano discover`](/docs/command-line-interface.html#discover), with an optional pluralized `plugin type` argument.
You can also check out the lists of supported [extractors](/plugins/extractors/) and [loaders](/plugins/loaders/) on this website.

If the Singer tap or target you'd like to use with Meltano doesn't show up in any of these places, you're going to want to add a custom plugin.
When you run `meltano add --custom <type> <name>`, Meltano will ask you some additional questions to learn where the package can be found, how to interact with it, and how it can be expected to behave.

If the tap or target in question is listed on Singer's [index of taps](https://www.singer.io/#taps) or [targets](https://www.singer.io/#targets), simply providing the package name as `name`, `pip_url`, and `executable` should suffice. If it's a tap or target you have developed or are developing yourself, you'll want to set `pip_url` to either a Git URL or local directory path. To find out what `settings` a tap or target supports, reference its documentation. If the `capabilities` a tap supports are not described in its documentation, try [one of these tricks](/docs/contributor-guide.html#how-to-test-a-tap).

Once your plugin has been added, it will be ready for [configuration](/#meltano-config)!
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

Your extractor or loader is now ready for [configuration](/#meltano-config)!

:::

::: slot meltano-config

## Managing the configuration of your plugins

Meltano is responsible for managing the configuration of all of a project's plugins, including its extractors and loaders.
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

This means that you do not need to manually craft the
[`config.json` files](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#config-file) expected by Singer taps and targets,
because Meltano will generate them on the fly whenever an extractor or loader is used through [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If the plugin you'd like to use and configure is already known to Meltano (that is, it shows up when you run [`meltano discover`](/docs/command-line-interface.html#discover)), Meltano already knows what settings it supports.
If you're [adding a custom plugin](/#meltano-add), on the other hand, you will be asked to specify the names of the supported configuration options yourself.

To determine the values of these settings, Meltano will look in 4 places, with each taking precedence over the next:

1. **Environment variables**, set through your project's `.env` file or any other method. You can use `meltano config <plugin> list` to list the available variable names.
2. **The plugin's `config` object** in your project's `meltano.yml` file.
3. **Your project's SQLite database** at `.meltano/meltano.db`, which stores configuration set using [`meltano config`](/docs/command-line-interface.html#config) among other things.
4. **The plugin's `default` values** set on its `settings` object in your project's `meltano.yml` file (in the case of custom plugins) or the global `discovery.yml` (in the case of "known" plugins).

Since `.env` and `.meltano/meltano.db` are both included in your project's `.gitignore` file by default, sensitive values like passwords and tokens are more appropriately stored in either of these places than in `meltano.yml`.

:::

::: slot meltano-config-code

```bash
# List available plugin settings
# with their names and environment variables
meltano config tap-covid-19 list

# Store non-sensitive plugin configuration in
# your project's `.meltano/meltano.db`
meltano config tap-covid-19 set start_date "2020-01-01T00:00:00Z"
meltano config tap-covid-19 set user_agent "tap-covid-19 via meltano <api_user_email@your_company.com>"

# Store sensitive plugin configuration in...
# - the current shell environment, for one-off use:
export TAP_COVID_19_API_TOKEN="<your_github_api_token>"
# - OR your project's `.env`, for repeated use:
touch .env
echo "TAP_COVID_19_API_TOKEN=<your_github_api_token>" >> .env

# Unset configuration stored in `.meltano/meltano.db`
# meltano config tap-covid-19 unset api_token

# Reset configuration stored in `.meltano/meltano.db`
# meltano config tap-covid-19 reset

# View configuration, independent of storage method
meltano config tap-covid-19
```

```json
{"api_token": "<your_github_api_token>", "user_agent": "tap-covid-19 via meltano <api_user_email@your_company.com>", "start_date": "2020-01-01T00:00:00Z"}
```

Your plugin has now been configured
and is [ready for its first pipeline](/#integration)!

:::

::: slot meltano-select

## Selecting entities and properties for extraction

Extractors are often capable of extracting many more entities and properties than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and properties you actually plan on using.

With stock Singer taps, entity selection involves a few steps. First, you run a tap in
[discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
to generate a massive `catalog.json` file describing all available entities and properties.
Then, you edit this file and add `"selected": true` to the `metadata` objects for all of the desired entities and properties.
Finally, you pass this file to the tap when you run it in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md) using the `--catalog` flag.
Because these catalog files can be very large, this process can be tedious and error-prone.

Meltano makes it easy to select specific entities and properties for inclusion or exclusion using [`meltano select`](/docs/command-line-interface.html#select),
which lets you define inclusion and exclusion rules using [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like patterns with wildcards (`*`, `?`) and character groups (`[abc]`, `[!abc]`).

Whenever an extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt), Meltano will automatically run the tap in discovery mode, apply the rules to the resulting catalog file, and pass it to the tap in sync mode.

Note that exclusion takes precedence over inclusion: if an entity or property is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your project's `meltano.yml` file first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and properties are selected.

:::

::: slot meltano-select-code

```bash
# List all available entities and properties
meltano select --list --all tap-covid-19

# Include all properties of an entity
meltano select tap-covid-19 "eu_ecdc_daily" "*"

# Include specific properties of an entity
meltano select tap-covid-19 "eu_daily" "date"
meltano select tap-covid-19 "eu_daily" "country"
meltano select tap-covid-19 "eu_daily" "cases"
meltano select tap-covid-19 "eu_daily" "deaths"

# Exclude matching properties of all entities
meltano select tap-covid-19 --exclude "*" "git_*"

# List selected (enabled) entities and properties
meltano select --list tap-covid-19
```

```output
Enabled patterns:
    eu_ecdc_daily.*
    eu_daily.date
    eu_daily.country
    eu_daily.cases
    eu_daily.deaths
    *.git_*

Selected properties:
    [automatic] eu_daily.__sdc_row_number
    [automatic] eu_daily.git_path
    [selected ] eu_daily.date
    [selected ] eu_daily.country
    [selected ] eu_daily.cases
    [selected ] eu_daily.deaths
    [automatic] eu_ecdc_daily.__sdc_row_number
    [automatic] eu_ecdc_daily.git_path
    [selected ] eu_ecdc_daily.date
    [selected ] eu_ecdc_daily.datetime
    [selected ] eu_ecdc_daily.country
    [selected ] eu_ecdc_daily.cases
    [selected ] eu_ecdc_daily.deaths
```

Your entities and properties have now been selected for [extraction](/#integration)!

:::
