---
description: Meltano takes a modular approach to data engineering and EL(T), where your project and pipelines are composed of plugins.
---

# Meltano Plugins

Meltano takes a modular approach to data engineering in general and EL(T) in particular,
where your [project](/docs/project.html) and pipelines are composed of plugins of [different types](#types), most notably
[**extractors**](#extractors) ([Singer](https://singer.io) taps),
[**loaders**](#loaders) ([Singer](https://singer.io) targets),
[**transformers**](#transformers) ([dbt](https://www.getdbt.com) and [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)), and
[**orchestrators**](#orchestrators) (currently [Airflow](https://airflow.apache.org/), with [Dagster](https://dagster.io/) [in development](https://gitlab.com/meltano/meltano/-/issues/2393)).

Meltano provides the glue to make these components work together smoothly and enables consistent [configuration](/docs/configuration.html) and [deployment](/docs/production.html).

To learn how to manage your project's plugins, refer to the [Plugin Management guide](/docs/plugin-management.html).

