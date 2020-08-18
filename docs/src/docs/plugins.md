---
metaTitle: Meltano plugins
description: XXX
---

# Meltano plugins

A [Meltano project](/docs/project.html) is primarily comprised of plugins,
that implement the various details of your data pipelines.

Meltano knows the following types of plugins:

- [Extractors](#extractors)
- [Loaders](#loaders)
- [Transforms](#transforms)
- [Models](#models)
- [Dashboards](#dashboards)
- [Orchestrators](#orchestrators)
- [Transformers](#transformers)
- [File bundles](#file-bundles)

## Extractors

Extractors are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for pulling data out of an arbitrary data source: a database, SaaS API, or file with a specific format.

Meltano supports [Singer taps](https://singer.io): executables that implement the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

## Loaders

Loaders are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for taking extracted data and putting it in an arbitrary data destination: a database, SaaS API, or file with a specific format.

Meltano supports [Singer targets](https://singer.io): executables that implement the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

## Transforms

Transforms are [dbt packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) containing [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models),
that are used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).

Together with the [dbt](https://www.getdbt.com) [transformer](#transformers), they are responsible for transforming data that has been loaded into a database (data warehouse) into a different format, usually one more appropriate for [analysis](/docs/analysis.html).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the [dbt package Git repository](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages) referenced by its `pip_url`
will be added to your project's `transform/packages.yml` and the package will be enabled in `transform/dbt_project.yml`.

## Models

Models are [pip packages](https://pip.pypa.io/en/stable/) used by [Meltano UI](/docs/command-line-interface.html#ui) to aid in [data analysis](/docs/analysis.html).
They describe the schema of the data being analyzed and the ways different tables can be joined,
and are used to automatically generate SQL queries using a point-and-click interface.

## Dashboards

Dashboards are [pip packages](https://pip.pypa.io/en/stable/) bundling curated [Meltano UI](/docs/command-line-interface.html#ui) dashboards and reports.

When a dashboard is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled dashboards and reports will automatically be added to your project's `analyze` directory as well.

## Orchestrators

Orchestrators are [pip packages](https://pip.pypa.io/en/stable/) responsible for [orchestrating](/docs/orchestration.html) a project's [scheduled pipelines](/docs/command-line-interface.html#schedule).

Meltano supports [Apache Airflow](https://airflow.apache.org/) out of the box, but can be used with any tool capable of reading the output of [`meltano schedule list --format=json`](/docs/command-line-interface.html#schedule) and executing each pipeline's [`meltano elt`](/docs/command-line-interface.html#elt) command on a schedule.

When the `airflow` orchestrator is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

## Transformers

Transformers are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).
They are responsible for running [transforms](#transforms).

Meltano supports [dbt](https://www.getdbt.com) and its [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) out of the box.

When the `dbt` transformer is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

## File bundles

File bundles are [pip packages](https://pip.pypa.io/en/stable/) bundling files you may want in your Meltano project.

When a file bundle is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled files will automatically be added as well.
The file bundle itself will not be added to `meltano.yml` unless it contains files that are
[managed by the file bundle](#update-extra) and to be updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run.
