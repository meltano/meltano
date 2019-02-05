# Concepts

Below are common terms used within the Meltano ecosystem arranged alphabetically.

## Aggregate

An `Aggregate` relates to a calculable column, via `count`, `sum` or other (i.e., aggregate definitions). These are limited to predefined methods with no custom SQL as well since custom SQL will be handled through transforms with dbt.

## Collection

A `Collection` is a group of one or many `Designs` that determines how they will be mapped together.

A `Collection` can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

## Column

A `Column` relates directly to a column in a table of a database. Some limitations of this are that it will be limited to column only and no custom SQL.

## Dashboard

A `Dashboard` is a group of many `Reports`.

A `Dashboard` is identified by the file naming schema: `set-name.dashboard.m5o` and should be stored in the `/dashboards` directory.

## Design

A `Design` maps multiple tables together via joins. It points to many tables by names and can also add filters. At a high level, it does the following:

1. Takes selected columns to generate SQL from the `.m5oc` file
1. Runs the SQL query
1. Outputs the desired graph

In addition, a `Design` is the file that you would use to do the actual analysis because it defines the relationship between the tables.

A `Design` can be identified by the file naming schema: `design-name.design.m5o` and should be stored in the `/collections` directory.

## M5O Files

There are two types of `.m5o` files:

1. `.m5o` are user defined files that model the data in your database
2. `.m5oc` are compiled files generated from multiple `m5o` files

The `.m5o` files are based on the JSON-like HOCON syntax and serve as input for the compiled `.m5oc` files that Meltano UI then leverages.

## Report

A `Report` is a saved state of selecting and analyzing a `Design`. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

A `Report` can be identified by the file naming schema: `report-name.report.m5o` and should be stored in the `/reports` directory.

## Table

A `Table` relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains `columns` and `aggregates` so you can select which you want to show.

A `Table` can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

## Taps & Targets

### Tap

See our [sample first tap](https://gitlab.com/meltano/tap-gitlab/) as a good tap starting point.

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of taps](https://www.singer.io/#taps)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

### Target

See our [csv target](https://gitlab.com/meltano/target-csv) as a good starting point for targets.

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of targets](https://singer.io/#targets)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

### Workflow for tap/target development

#### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

#### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target developement please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitLab
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

### Discoverability

We will maintain a curated list of taps/targets that are expected to work out of the box with Meltano.

Meltano should help the end-user find components via a `discover` command:

```
$ meltano discover extract
tap-demo==...
tap-zendesk==1.3.0
tap-marketo==...
...

$ meltano discover load
target-demo==...
target-snowflake==git+https://gitlab.com/meltano/target-snowflake@master.git
target-postgres==...
```

#### How to install taps/targets

##### Locally

See `meltano-add`

##### On a CI

A docker image should be build containing all the latest curated version of the taps/targets, each isolated into its own virtualenv.

This way we do not run into `docker-in-docker` problems (buffering, permissions, security).

Meltano should provide a wrapper script to manage the execution of the selected components:

`meltano extract tap-zendesk --to target-postgres`
