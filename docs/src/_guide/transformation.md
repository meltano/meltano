---
title: Transform Data
description: Transform your data with dbt
layout: doc
weight: 5
---

Transformations in Meltano are implemented using dbt. All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run the transformations. A transform in Meltano is simply a set of dbt models that can be installed as a package. See the [transform plugin](/concepts/plugins#transforms) docs for more details.

## Adapter-Specific dbt Transformation

In alignment with the [dbt documentation](https://docs.getdbt.com/docs/available-adapters), we support adapter-specific installations of `dbt`.
We currently support Snowflake, Postgres, Redshift, and BigQuery.

If you are interested in another adapter, please consider contributing its definition to [MeltanoHub](https://hub.meltano.com/transformers/).
Alternatively, all others are currently supported by the [`dbt` transformer](/guide/transformation#dbt-installation-and-configuration-classic).

### Install `dbt`

To install an adapter-specific variant of dbt to your project, run:

```bash
# list available transformer plugins
meltano discover transformers

# install adapter-specific dbt, e.g. for snowflake
meltano add transformer dbt-snowflake
```

After dbt is installed you can configure it using `config` CLI commands, [Meltano environments](/concepts/environments) or environment variables:

```bash
# list available settings
meltano config dbt-snowflake list

# set the Snowflake user in the `dev` environment
meltano --environment=dev config dbt-snowflake set user DEV_USER

# set the Snowflake user in the `prod` environment
meltano --environment=prod config dbt-snowflake set user PROD_USER
```

More details on [configuring plugins](/guide/configuration), including with [environment variables](/guide/configuration#environment-variables).

### Running `dbt` in Meltano

There are two ways to run adapter-specific dbt plugins using Meltano; in a pipeline using the [`run`](/reference/command-line-interface#run) command or standalone with arguments using the [`invoke`](/reference/command-line-interface#invoke) command.

#### Running `dbt` as part of a Pipeline

Once you have created your models in dbt, run them as part of a pipeline:

```bash
# run a complete ELT pipeline using the `dev` environment config
meltano --environment=dev run tap-gitlab target-snowflake dbt-snowflake:run
```

To run a subset of your dbt project, define a [plugin command](/concepts/project#plugin-commands) with your desired dbt selection filters:

```yaml
# meltano.yml
plugins:
  transformers:
    - name: dbt-snowflake
      commands:
        my_models:
          args: run --select +my_model_name
          description: Run dbt, selecting model `my_model_name` and all upstream models. Read more about the dbt node selection syntax at https://docs.getdbt.com/reference/node-selection/syntax
```

This can then be executed as follows:

```bash
meltano --environment=dev run tap-gitlab target-snowflake dbt-snowflake:my_models
```

#### Invoking `dbt`

Dbt can also be run directly, via the [`invoke`](/reference/command-line-interface#invoke) command:

```bash
# run your entire dbt project
meltano invoke dbt-snowflake run

# run with node selection criteria
meltano invoke dbt-snowflake run --select +my_model_name

# run with a command specified in meltano.yml
meltano invoke dbt-snowflake:my_models
```

## `dbt` Installation and Configuration (Classic)

<div class="notification is-warning">
  <p> These instructions are the classic way of installing and running dbt. </p>
  <p> Users can still install dbt in this manner but we are prioritizing <a href="/guide/transformation#adapter-specific-dbt-transformation">adapter-specific dbt plugin installations for new and existing users</a>.</p>
</div>

To learn more about the dbt Transformer package, please see the
[dbt plugin](https://hub.meltano.com/transformers/dbt) documentation on [Meltano Hub](https://hub.meltano.com).

To install the dbt transformer to your project run:

```bash
meltano add transformer dbt
```

After dbt is installed you can change the default configurations using environment variables or `config` CLI commands like the following:

```bash
meltano config dbt set target <target>

# For example:
meltano config dbt set target postgres
```

For more details, [pipeline environment variables](/guide/integration#pipeline-environment-variables) and [dbt transform settings](https://hub.meltano.com/transformers/dbt#settings).

## Working with Transform Plugins

<div class="notification is-danger">
  <p> <b>WARNING</b>: Transform plugins are currently de-prioritized by the Meltano project due to the difficulty of maintaining them at scale.</p>
  <p>Users can still install and maintain them as they please but many have grown outdated and unmaintained.</p>
  <p>Some users chose to install the existing transform plugins as a starting point then customize them for their own transformations.</p>
</div>

`Transform` plugins are dbt packages that reside in their own repositories.

When a transform is added to a project, it is added as a dbt package in `transform/packages.yml`, enabled in `transform/dbt_project.yml`, and loaded for usage the next time dbt runs.

_**Note:** You do not have to use `transform` plugin packages in order to use dbt. Many teams instead choose to create their own custom transformations._

For more information on how to build your own dbt models or to customize your project directly, see the [dbt docs](https://docs.getdbt.com/).

### Configuring Transform Plugins

Transform plugins may have additional configuration options in `meltano.yml`. For example, the `tap-gitlab` dbt package requires three variables, which are used for
finding the tables where raw data has been loaded during the Extract-Load phase:

```yml
{% raw %}
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "{{ env_var('PG_SCHEMA') }}.entry"
    generationmix_table: "{{ env_var('PG_SCHEMA') }}.generationmix"
    region_table: "{{ env_var('PG_SCHEMA') }}.region"
{% endraw %}
```

As an alternative to providing values from environment variables, you can also set values directly in `meltano.yml`:

```yml
transforms:
  - name: tap-gitlab
    pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
    vars:
      entry_table: "my_raw_schema.entry"
      generationmix_table: "my_raw_schema.generationmix"
      region_table: "my_raw_schema.region"
```

Whenever Meltano runs a new transformation, `transform/dbt_project.yml` is updated using the values provided in `meltano.yml`.

### Running a Transform in Meltano

The two main ways to run your dbt transforms using Meltano are by calling them inline with your ELT pipeline using `--transform run` or decoupled from your pipeline using `invoke dbt:run`.

#### Transform in your ELT pipeline

When `melatno elt` runs with the `--transform run` option, Meltano uses the convention that the transform has the same namespace as the extractor in its pipeline, except with snake_case (tap-gitlab -> tap_gitlab).
As an example, assume that the following command runs:

```bash
meltano elt <tap> <target> --transform run

# For example:
meltano elt tap-gitlab target-postgres --transform run
```

After the Extract and Load steps are successfully completed meaning data has been extracted from the GitLab API and loaded to a Postgres DB, the dbt transform in the `/transform/models/tap_gitlab/` directory is run.

Under the hood this `--transform run` option is telling Meltano to run multiple dbt commands.
First it installs any required dbt package dependencies using `dbt deps` then it runs your models using `dbt run --models <models>`.
The `<models>` argument is populated using the Meltano transform `models` setting [documented here](https://hub.meltano.com/transformers/dbt#models).

Using this method for executing transforms allows Meltano to make some assumptions about the appropriate configurations for running dbt.
Based on the target loader you are using, Meltano is able to default your dbt transform `target` [config setting](https://hub.meltano.com/transformers/dbt#target) to the correct SQL dialect (e.g. Snowflake, Postgres, etc.). Meltano also auto populates the `source_schema` and `target_schema` [settings](https://hub.meltano.com/transformers/dbt#source-schema) using the loader schema setting from the pipeline.

#### Transform directly

Just like other Meltano plugins, dbt transforms can be executed directly using `invoke`.
Using this method decouples dbt transformations from ELT pipelines which could be preferred for certain users depending on their dbt project.

Users might choose this approach if they want to replicate data from many sources before running a set of dbt models that blend all of them together or maybe multiple models reference the same source data but are refreshed on different cadences (i.e. one is updated right when data arrives while another is only refreshed once a week).

For example, to run the same transforms as the tap-gitlab `--transform=run` example above, the following command can be run:

```bash
meltano invoke dbt:<command>

# For example:
meltano invoke dbt:run --models tap_gitlab.*
```

Again, this runs all dbt models in the `/transform/models/tap_gitlab/` directory.

The downside of running directly vs in a pipeline is that Meltano can't infer anything about how dbt should run so more settings might need to be explictly set by the user. This includes target dialet `DBT_TARGET`, source schema `DBT_SOURCE_SCHEMA`, target schema `DBT_TARGET_SCHEMA`, and models `DBT_MODELS`.

See the [transformer docs](https://hub.meltano.com/transformers/dbt#commands) from other dbt commands.

### Adding a Transform to your Meltano Project

Once the dbt transformer has been installed in your Meltano project you will see the `/transform` directory populated with dbt artifacts.
If you chose to use the `--transform run` option in an ELT pipeline, its important to note that Meltano uses the convention that the transform has the same namespace as the extractor in its pipeline, except with snake_case (tap-gitlab -> tap_gitlab).
For instance, all you need to do is start writing your dbt models in the appropriate `/transform/models/<tap_name>/` directory.

See the [dbt documentation](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for more details on writing models.

Another common option is to install your dbt project as a package from a separate git repository.
See [dbt package management](https://docs.getdbt.com/docs/building-a-dbt-project/package-management).
To do this you just add a `/transform/packages.yml` file to your project with your dbt project referenced.
For instance your yaml file might look like this:

```yaml
packages:
  - git: https://gitlab.com/your_repo/your-dbt-project.git
    revision: 1.0.0
```

If you plan to call dbt directly using `invoke` then you have to first run `meltano invoke dbt:deps` to install your package dependencies.
Using the `--transform=run` option in your pipeline takes care of this step for you automatically.
