# Overview

## Introduction

Meltano is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.

Meltano does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It also leverages open source software and software development best practices including

- Consistent primitives and naming
- Clear and powerful line interface
- Version control
- Easy to get started
- Consistent locations for storing data
- Continuous integration / deployment
- Review apps

[![Meltano Diagram](/meltano-diagram.png)](/meltano-diagram.png)

Meltano stands for the steps of the data lifecycle:

- Model
- Extract
- Load
- Transform
- Analyze
- Notebook
- Orchestrate

To empower you and your team in this lifecycle, Meltano manifests as two tools:

1. command line interface (CLI)
1. web app (GUI)

These two tools enable you and your team to use Meltano in a few different ways:
1. Meltano as **Project** (CLI + GUI)
    - From data extraction to analysis and visualization with orchestration for automating the process
1. Meltano as **Framework** (CLI)
    - Helps you create and test extractors, loaders, and transforms
1. Meltano as **ELT** only (CLI)
    - Runtime for extracting, loading, and transforming of data
1. Meltano as **Analyze** only (GUI)
    - Interactively query, explore, visualize, and model the data (warehouse)

It leverages open source software and software development best practices including version control, CI, CD, and review apps for [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence and data science.

**Notes**

- _Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields._
- _The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription._

## Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the [Data Lifecycle].

Our CLI tool provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data lifecycle.

## Meltano Schema

Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

### Create Schema and Roles

Create and grant usage for a database schema.

## Meltano Model

Meltano Models allow you to define your data model and generate SQL so that you can easily analyze and visualize it in Meltano Analyze.

## Meltano Analyze

Meltano Analyze is a dashboard that allows you to run SQL queries and produce data visualizations, charts, and graphs based on your data.

## Meltano Transform

### dbt

Meltano uses [dbt](https://docs.getdbt.com/) to transform the source data into the `analytics` schema, ready to be consumed by models.

[Fishtown wrote a good article about what to model dynamically and what to do in dbt transformations](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304).

#### Python scripts

In certain circumstances transformations cannot be done in dbt (like API calls), so we use python scripts for these cases.

### Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.

#### Loading a CSV:

> Notes:
>
> - The naming format for the `FILES` must be `<schema>.<table>.csv`. This pattern is required and will be used to create/update the table in the DW.
> - Multiple `FILES` can be used, use spaces to separate.

- Start the cloud sql proxy
- Run the command:

```
python3 elt/util/spreadsheet_loader.py csv FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Loading a Google Sheet:

> Notes:
>
> - Each `FILES` will be located and loaded based on its name. The names of the sheets shared with the runner must be unique and in the `<schema>.<table>` format
> - Multiple `FILES` can be used, use spaces to separate.

- Share the sheet with the required service account (if being used in automated CI, use the runner service account)
- Run the command:

```
python3 elt/util/spreadsheet_loader.py sheet FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

#### Further Usage Help:

- Run the following command(s) for additional usage info `python3 elt/util/spreadsheet_loader.py <csv|sheet> -- --help`

### Docker images

Meltano provides the following docker images:

> Notes: All images are available in the GitLab's registry: `registry.gitlab.com`

- `meltano/meltano`: Contains the API, CLI, and Meltano Analyze. This image should be deployed as Meltano Analyze.
- `meltano/meltano/runner`: Contains the CLI and extra runner specific binaries. This image should be used on the CI runner.
- `meltano/meltano/singer_runner`: **DEPRECATED: Use `meltano/meltano/runner` instead** Contains the CLI, and all curated taps/targets pre-installed.

> Notes: These images are base images used as the basis of other images.

- `meltano/meltano/cli`: Contains the meltano cli
- `meltano/meltano/base`: Contains the requirements for `meltano/meltano`

## Meltano Ecosystem

| Stage       | Meltano selected                                                                     | OSS considered but not selected                                                                                                          | Proprietary alternatives                                                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model       | [Meltano Model](https://gitlab.com/meltano/meltano#meltano-model)                    | [Open ModelSphere](http://www.modelsphere.com/org/)                                                                                      | [LookML](https://looker.com/platform/data-modeling), [Matillion](http://www.stephenlevin.co/data-modeling-layer-startup-analytics-dbt-vs-matillion-vs-lookml/) |
| Extract     | [Singer Tap](https://gitlab.com/meltano/meltano#tap)                                 | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/)                                         | [Alooma](https://www.alooma.com/), [Fivetran](https://fivetran.com/)                                                                                           |
| Load        | [Singer Target](https://gitlab.com/meltano/meltano#target)                           | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/)                                         | [Alooma](https://www.alooma.com/), [Fivetran](https://fivetran.com/)                                                                                           |
| Transform   | [dbt](https://www.getdbt.com/)                                                       | [Stored procedures](https://gitlab.com/meltano/meltano#stored-procedures), [Pentaho DI](http://www.pentaho.com/product/data-integration) | [Alooma](https://www.alooma.com/)                                                                                                                              |
| Analyze     | [Meltano Analyze](https://gitlab.com/meltano/meltano/tree/master/src/analyze)        | [Metabase](https://www.metabase.com/)                                                                                                    | [Looker](https://looker.com/), [Periscope](https://www.periscopedata.com/)                                                                                     |
| Notebook    | [JupyterHub](https://github.com/jupyterhub/jupyterhub)                               | [GNU Octave](https://www.gnu.org/software/octave/)                                                                                       | [Nurtch](https://www.nurtch.com/), [Datadog notebooks](https://www.datadoghq.com/blog/data-driven-notebooks/)                                                  |
| Orchestrate | [GitLab CI](https://docs.gitlab.com/ee/ci/) / [Airflow](https://airflow.apache.org/) | [Luigi](https://github.com/spotify/luigi), [Nifi](https://nifi.apache.org/)                                                              | [Fivetran](https://fivetran.com/)                                                                                                                              |
