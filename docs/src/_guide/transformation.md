---
title: Data Transformation (T)
description: Transform your data.
layout: doc
weight: 5
---

Data transformations in Meltano are implemented by using [dbt](https://www.getdbt.com/) (the "Data Build Tool") transformer plugins.
All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run the transformations.

Meltano supports installing adapter specific Transformer plugins (e.g. `dbt-snowflake`), in line with dbt's [available adapters documentation](https://docs.getdbt.com/docs/available-adapters).
If your project uses the older `dbt` plugin, we recommend [migrating](/guide/transformation#migrating-to-an-adapter-specific-dbt-transformer) your install to an adapter specific one (e.g. `dbt-snowflake`).

To learn more about the dbt Transformer package, please see the [dbt plugin](https://hub.meltano.com/transformers/dbt) documentation on [Meltano Hub](https://hub.meltano.com).

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

Dbt can also be run directly, via the [`invoke`]() command:

```bash
# run your entire dbt project
meltano invoke dbt-snowflake run

# run with node selection criteria
meltano invoke dbt-snowflake run --select +my_model_name

# run with a command specified in meltano.yml
meltano invoke dbt-snowflake:my_models
```

## Migrating to an Adapter Specific `dbt` Transformer
