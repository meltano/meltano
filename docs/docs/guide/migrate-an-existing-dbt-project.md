---
title: Migrate an Existing dbt Project
description: Learn how to import an existing dbt project into your Meltano project.
layout: doc
redirect_from:
  - /guide/existing-dbt-project
sidebar_position: 25
---

This guide will describe how to bring existing dbt code into the your Meltano project.
Meltano uses some suggested patterns for organizing your dbt project so it integrates well with core features of Meltano like [environments](https://docs.meltano.com/concepts/environments).
You can organize your project whatever way you chose but this guide will describe how to import it so it matches the default transformer installation.

### Pre-requisites

As always, we highly recommend git versioning your Meltano project prior to following this guide so you have the ability to roll back and not affect your existing Meltano project configurations.

### Add dbt Transformer

Add your adapter-specific dbt variant (e.g. dbt-postgres) that can be found on [MeltanoHub](https://hub.meltano.com/utilities/).

```
meltano add dbt-<adapter_name>

# For example
meltano add dbt-postgres
```

Next configure your transformer to include database names, connection credentials, etc.
See the [transform data guide](/guide/transformation#install-dbt) for more details.
Or use the [interactive config flag](/reference/command-line-interface#how-to-use-interactive-config) to follow prompts.

```
meltano config dbt-snowflake set --interactive
```

Once you've configured your transformer you should be able to run the following command to test your connection and credentials.

```
meltano invoke dbt-postgres debug
```

### Migrating dbt Code Into Meltano

Note that the `initialize` command for a dbt transformer utility creates the expected scaffolding within your Meltano `/transform` directory including a `dbt_project.yml` and `/profile/profiles.yml`.
If you have an existing dbt project you can skip running the `initialize` because you will already have your own version of these files in your other repo, so we'll describe how to merge what you have and what Meltano provides and expects.

#### Meltano's Default Structure For dbt

Meltano expects dbt project files to exist in the default directories listed below.
You can either place your files in the appropriate directories or you can update the given `dbt_project.yml` to follow the directory structure of your existing project, if thats preferred.

- data - this is where seed files are stored. See [seeds dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/seeds)
- models - this is where models are stored. See [models dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)
- analysis - analysis sql that shouldnt be materialized. See [analyses dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/analyses)
- tests - this is where singular dbt test are stored. See [tests dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/tests)
- macros - jinja macros. See [macros dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros)
- snapshots - this is where snapshot models are stored. See [snapshots dbt docs](https://docs.getdbt.com/docs/building-a-dbt-project/snapshots)

#### dbt Profiles

Meltano's default dbt project scaffolding comes with a profiles.yml (see [dbt profiles docs](https://docs.getdbt.com/dbt-cli/configure-your-profile) for details) that is configured to take advantage of the [environments](https://docs.meltano.com/concepts/environments) feature.
This means that you configure dbt using the provided Meltano settings and they get automatically passed to dbt based on what Meltano environment is active.
Meltano's dbt installation comes with pre-configured [dbt targets](https://docs.getdbt.com/dbt-cli/configure-your-profile#understanding-targets-in-profiles) mapped to the default environment names (i.e. dev, staging, prod), avoiding the need to toggle credentials manually and allowing sharing of settings/credentials across plugins.

#### Custom `dbt_projects.yml` Configurations

If you had any configurations in your dbt_project.yml such as definitions of how models are materialized, target databases, schemas, etc. you can directly copy them into your new Meltano dbt_project.yml file.

Again Meltano doesn't require this structure, any valid dbt project will work, but this is the default recommended structure with some base configurations for a simple integration between Meltano and dbt.
