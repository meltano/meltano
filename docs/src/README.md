---
home: true
heroImage: /meltano-logo.svg
metaTitle: "Meltano: open source data pipelines"
description: Meltano is an open source platform for building, running & orchestrating ELT pipelines built out of Singer taps and targets and dbt models, that you can run locally or easily deploy in production. Our goal is to make the power of data integration available to all by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.
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

# Open source data pipelines

Meltano is an [open source](https://gitlab.com/meltano/meltano) platform for
building, running & orchestrating ELT pipelines built out of [Singer](https://www.singer.io/) taps and targets and [dbt](https://www.getdbt.com) models, that you can [run locally](/docs/installation.html) or [easily deploy in production](/docs/production.html).

Our goal is to [make the power of data integration available to all](https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/)
by building a true open source alternative to existing proprietary hosted EL(T) solutions, in terms of ease of use, reliability, and quantity and quality of supported data sources.

Scroll down for details on
[Meltano projects](/#meltano-init),
[integration](/#integration),
[transformation](/#transformation),
[orchestration](/#orchestration), and
[containerization](/#containerization),
followed by instructions on
[adding extractors and loaders to your project](/#meltano-add),
[managing the configuration of your plugins](/#meltano-config), and
[selecting entities and attributes to extract](/#meltano-select).

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

At the core of the Meltano experience is the Meltano project,
which represents the single source of truth regarding your data pipelines:
how data should be [integrated](/#integration) and [transformed](/#transformation),
how the pipelines should be [orchestrated](/#orchestration),
and how the various components should be [configured](/#meltano-config).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init),
which will create a new directory with:

- a `meltano.yml` file that will list any [`plugins` you'll add](/#meltano-add) and [pipeline `schedules` you'll create](/#orchestration),
- stubs for `.gitignore`, `README.md`, and `requirements.txt` for you to edit (or delete) as appropriate, and
- empty `model`, `extract`, `load`, `transform`, `analyze`, `notebook`, and `orchestrate` directories for you to use (or delete) as you please.

Whenever you [add a new plugin](/#meltano-add) to a Meltano project, it will be
installed into your project's `.meltano` directory automatically.
However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](/docs/command-line-interface.html#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in `meltano.yml`.
:::

::: slot meltano-init-code

<small>Follow the [installation instructions above](/#installation) and then...</small>

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
makes it easy to [select which entities and attributes to extract](/#meltano-select),
and keeps track of [the state of your extraction](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file),
so that subsequent pipeline runs with the same job ID will always pick up right where
the previous run left off.

Scroll down to learn more about [transformation](/#transformation) and [orchestration](/#orchestration), or jump straight to:
- [Adding extractors and loaders to your project](/#meltano-add)
- [Managing the configuration of your plugins](/#meltano-config)
- [Selecting entities and attributes to extract](/#meltano-select)
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

::: slot meltano-add

## Adding extractors and loaders to your project

Like all types of plugins, extractors and loaders can be added to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add).
Plugins that are already [known to Meltano](/docs/contributor-guide.html#known-plugins) can be added by simply specifying their `type` and `name`, while adding a plugin that Meltano isn't familiar with yet requires adding the `--custom` flag.

To find out what plugins are already known to Meltano and supported out of the box, you can use [`meltano discover`](/docs/command-line-interface.html#discover), with an optional pluralized `plugin type` argument.
You can also check out the lists of supported [extractors](/plugins/extractors/) and [loaders](/plugins/loaders/) on this website.

If the Singer tap or target you'd like to use with Meltano doesn't show up in any of these places, you're going to want to add a custom plugin.
When you run `meltano add --custom <type> <name>`, Meltano will ask you some additional questions to learn where the package can be found, how to interact with it, and how it can be expected to behave.

If the tap or target in question is listed on Singer's [index of taps](https://www.singer.io/#taps) or [targets](https://www.singer.io/#targets), simply providing the package name as `name`, `pip_url`, and `executable` should suffice. If it's a tap or target you have developed or are developing yourself, you'll want to set `pip_url` to either a VCS repository URL or local directory path. To find out what `settings` a tap or target supports, reference its documentation. If the `capabilities` a tap supports are not described in its documentation, try [one of these tricks](/docs/contributor-guide.html#how-to-test-a-tap).

Once your plugin has been added, it will be ready for [configuration](/#meltano-config)!
:::

::: slot meltano-add-code

<small>Follow the [project initialization instructions above](/#meltano-init) and then...</small>

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
# - prefix for configuration environment variables
# - identifier to find related/compatible plugins
# - default value for the `schema` setting when used
#   with loader target-postgres or target-snowflake
(namespace): tap_covid_19

# Specify `pip install` argument, for example:
# - PyPI package name:
(pip_url): tap-covid-19
# - VCS repository URL:
(pip_url): git+https://github.com/singer-io/tap-covid-19.git
# - local directory, in editable/development mode:
(pip_url): -e extract/tap-covid-19

# Specify the package's executable name
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

If the plugin you'd like to use and configure is already [known to Meltano](/docs/contributor-guide.html#known-plugins) (that is, it shows up when you run [`meltano discover`](/docs/command-line-interface.html#discover)), Meltano already knows what settings it supports.
If you're [adding a custom plugin](/#meltano-add), on the other hand, you will be asked to specify the names of the supported configuration options yourself.

To determine the values of these settings, Meltano will look in 4 places, with each taking precedence over the next:

<!-- The following is reproduced in docs/src/docs/command-line-interface.md#config with minor edits -->

1. **Environment variables**, set through your shell, a [`.env` file](https://github.com/theskumar/python-dotenv#usages) in your project directory, a [scheduled pipeline](/#orchestration)'s `env` object in `meltano.yml`, or any other method. You can use `meltano config <plugin> list` to list the available variable names.
2. **Your project's `meltano.yml` file**, under the plugin's `config` key. Inside values, [environment variables](/docs/command-line-interface.html#pipeline-environment-variables) can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
3. **Your project's [**system database**](/docs/settings.html#database-uri)**, which lives at `.meltano/meltano.db` by default and (among other things) stores configuration set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/command-line-interface.html#ui) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
4. **The default `value`s** set on the plugin's `settings` object in the global `discovery.yml` file (in the case of [known plugins](/docs/contributor-guide.html#known-plugins)) or your project's `meltano.yml` file (in the case of custom plugins). `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in your project's `meltano.yml` file and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, a (`.gitignore`d) `.env` file in your project directory, or the system database.

[`meltano config <plugin> set`](/docs/command-line-interface.html#config) will automatically store settings in `meltano.yml` or `.env` as appropriate.

:::

::: slot meltano-config-code

<small>Follow the [custom extractor instructions above](/#meltano-add) and then...</small>

```bash
# List all plugin settings with their names,
# environment variables, and current values
meltano config tap-covid-19 list

# Store non-sensitive plugin configuration in
# your project's `meltano.yml` file
meltano config tap-covid-19 set start_date "2020-01-01T00:00:00Z"
meltano config tap-covid-19 set user_agent "tap-covid-19 via meltano <api_user_email@your_company.com>"

# Store sensitive plugin configuration in...
# - the current shell environment:
export TAP_COVID_19_API_TOKEN="<your-github-api-token>"
# - OR a (gitignored) `.env` file:
meltano config tap-covid-19 set api_token <your-github-api-token>

# Unset specific setting
# meltano config tap-covid-19 unset start_date

# Reset configuration back to defaults
# meltano config tap-covid-19 reset

# View current configuration
meltano config tap-covid-19
```

```json
{"api_token": "<your-github-api-token>", "user_agent": "tap-covid-19 via meltano <api_user_email@your_company.com>", "start_date": "2020-01-01T00:00:00Z"}
```

Your plugin has now been configured
and is [ready for its first pipeline](/#integration)!

:::

::: slot meltano-select

## Selecting entities and attributes for extraction

Extractors are often capable of extracting many more entities and attributes than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and attributes you actually plan on using.

With stock Singer taps, entity selection (and specification of other [metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)) involves a few steps. First, you run a tap in
[discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
to generate a `catalog.json` file describing all available entities and attributes.
Then, you edit this file and add `"selected": true` (and any other metadata) to the `metadata` objects for all of the desired entities and attributes.
Finally, you pass this file to the tap using the `--catalog` flag when you run it in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md).
Because these catalog files can be very large and can get outdated as data sources evolve, this process can be tedious and error-prone.

Meltano makes it easy to select specific entities and attributes for inclusion or exclusion using [`meltano select`](/docs/command-line-interface.html#select),
which lets you specify inclusion and exclusion rules using [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like patterns with wildcards (`*`, `?`) and character groups (`[abc]`, `[!abc]`).

Additional [Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
(like `replication-method` and `replication-key`) can be specified like
any other [plugin configuration](/#meltano-config), using a special
[`_metadata` setting](/docs/command-line-interface.html#extractor-extra-metadata) with
[nested properties](/docs/command-line-interface.html#nested-properties)
`_metadata.<entity>.<key>` and `_metadata.<entity>.<attribute>.<key>`.

Similarly, a special [`_schema` setting](/docs/command-line-interface.html#extractor-extra-schema)
is available that lets you easily override
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) descriptions.
Like selection rules, these metadata and schema rules allow for [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like
patterns in the entity and attribute identifiers.

Whenever an extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt)
or [`meltano invoke`](/docs/command-line-interface.html#invoke), Meltano will
generate the desired catalog on the fly by running the tap in
discovery mode and applying the selection and metadata rules to the resulting catalog file
before passing it to the tap in sync mode.

Note that exclusion takes precedence over inclusion: if an entity or attribute is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your project's `meltano.yml` file first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and attributes are selected.

:::

::: slot meltano-select-code

<small>Follow the [configuration instructions above](/#meltano-config) and then...</small>

```bash
# List all available entities and attributes
meltano select --list --all tap-covid-19

# Include all attributes of an entity
meltano select tap-covid-19 eu_ecdc_daily "*"

# Include specific attributes of an entity
meltano select tap-covid-19 eu_daily date
meltano select tap-covid-19 eu_daily country
meltano select tap-covid-19 eu_daily cases
meltano select tap-covid-19 eu_daily deaths

# Exclude matching attributes of all entities
meltano select tap-covid-19 --exclude "*" "git_*"

# List selected (enabled) entities and attributes
meltano select --list tap-covid-19

# (Optional)
# Set stream metadata for all matching entities
# meltano config tap-covid-19 set _metadata "eu_*" replication-method INCREMENTAL
# meltano config tap-covid-19 set _metadata "eu_*" replication-key date
# meltano config tap-covid-19 set _metadata "eu_*" date is-replication-key true

# Override schema for matching attributes
# meltano config tap-covid-19 set _schema "eu_*" date type string
# meltano config tap-covid-19 set _schema "eu_*" date format date
```

```output
Enabled patterns:
    eu_ecdc_daily.*
    eu_daily.date
    eu_daily.country
    eu_daily.cases
    eu_daily.deaths
    !*.git_*

Selected attributes:
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

Your entities and attributes have now been selected for [extraction](/#integration)!

:::
