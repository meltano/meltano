---
title: Data Transformation (preview)
description: Transform your data.
layout: doc
weight: 9
---

<div class="notification">
  <p>In alignment with the <a href="https://docs.getdbt.com/docs/available-adapters">dbt documentation</a>, we are working towards supporting adapter specific installations of `dbt`, starting with `dbt-snowflake` (available below).</p>
  <p>If you are interested in another adapter, all others are currently supported by the <a href="/guide/transformation">`dbt` transformer.</a></p>
  <p>You can also check in on <a href="https://gitlab.com/meltano/meltano/-/issues/3298">#3298</a> where we are tracking progress on Postgres, Redshift, Bigquery and more!</p>
</div>

Data transformation in Meltano is implemented using [dbt](https://www.getdbt.com/) (the "Data Build Tool").
All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run data transformations.

Meltano supports installing adapter specific Transformer plugins (e.g. `dbt-snowflake`).
If you are working from an existing Meltano project that uses the [`dbt` transformer plugin](/guide/transformation), we recommend [migrating](/guide/transformation#migrating-to-an-adapter-specific-dbt-transformer) your install to an adapter specific one (e.g. `dbt-snowflake`).

## Install `dbt`

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

## Running `dbt` in Meltano

There are two ways to run adapter-specific dbt plugins using Meltano; in a pipeline using the [`run`](/reference/command-line-interface#run) command or standalone with arguments using the [`invoke`](/reference/command-line-interface#invoke) command.

### Running `dbt` as part of a Pipeline

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

### Invoking `dbt`

Dbt can also be run directly, via the [`invoke`](/reference/command-line-interface#invoke) command:

```bash
# run your entire dbt project
meltano invoke dbt-snowflake run

# run with node selection criteria
meltano invoke dbt-snowflake run --select +my_model_name

# run with a command specified in meltano.yml
meltano invoke dbt-snowflake:my_models
```

## Migrating to an Adapter Specific `dbt` Transformer

If you previously used the `dbt` Transformer, we recommend migrating to an adapter specific installation as per the `dbt` [available adapters documentation](https://docs.getdbt.com/docs/available-adapters).

### Install `dbt`

This is easy to do! Following the instructions from above to discover and install your chosen adapter:


```bash
# list available transformer plugins
meltano discover transformers

# install adapter-specific dbt, e.g. for snowflake
meltano add transformer dbt-snowflake
```

### Update your `dbt_project.yml`

Installation of a new Transformer will introduce two important files to your `transform/` directory:

- A new `profiles.yml` file in `transform/profiles/<adapter name>/profiles.yml`
- A new `dbt_project.yml` file in `transform/dbt_project (<adapter name>).yml`

The new `profiles.yml` will only be used by adapter specific `dbt` executions (e.g. `dbt-snowflake`), and can be customized to meet your requirements.
Your existing `profiles.yml` will remain in use by your existing `dbt` Transformer plugin (via `elt` and `invoke`).

It is likely that the new `dbt_project (<adapter name>).yml` will contain changes from your previous `dbt_project.yml` file, especially if you haven't already upgraded to [`dbt` v1.0](https://docs.getdbt.com/docs/guides/migration-guide/upgrading-to-v1.0).
To complete your migration, consolidate `dbt_project.yml` and `dbt_project (<adapter name>).yml` into a single file called `dbt_project.yml`.
As this project file will be used by both `dbt` and `dbt-<adapter>` Transformer plugins by default, you must ensure you are running an up-to-date installation of plugin `dbt` if you intend to use both adapter specific and legacy `dbt` installs together (not recommended).

If you make use of [Transform](/guide/transforms) plugins, these will continue to work as regular `dbt` packages. However adding new Transform plugins will currently (tracking at [#3382](https://gitlab.com/meltano/meltano/-/issues/3382)) re-add the legacy `dbt` Transformer plugin.
To avoid this we recommend adding Transforms as regular packages directly via the dbt CLI as per the [`dbt` Packages documentation](https://docs.getdbt.com/docs/building-a-dbt-project/package-management).

### Remove the `dbt` Transformer plugin and associated files

To remove the legacy `dbt` Transformer plugin, run:

```bash
# remove the transformer `dbt`
meltano remove transformer dbt

# remove the file bundle `dbt`
meltano remove files dbt
```

Removing a file bundle _does not_ remove any files from your `transform/` directory.
Manually remove `transform/profiles.yml` to complete clean-up (as adapter specific installs come with their own `profiles.yml` in `transform/profiles/<adapter name>/profiles.yml`).
