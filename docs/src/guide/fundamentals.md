---
sidebar: auto
---

# Fundamentals

## Overview

The Meltano product consists of three key components:

1. A SQL based data store, for example [PostgreSQL](https://www.postgresql.org/) or [Cloud SQL](https://cloud.google.com/sql/). We recommend using Postgres for [review apps](https://about.gitlab.com/features/review-apps/) and a more durable and scalable service for production.
1. This project, [`meltano`](https://gitlab.com/meltano/meltano), which contains the ELT scripts and CI jobs to refresh the data warehouse from the [configured sources](https://gitlab.com/meltano/meltano/master/data_sources.md). Typically configured to run on a [scheduled CI job](https://docs.gitlab.com/ce/user/project/pipelines/schedules.html) to refresh the data warehouse from the configured sources.
1. The [`meltano-elt`](https://gitlab.com/meltano/meltano-elt) container, which includes the necessary dependencies for the ELT scripts. Used as the base image for the CI jobs.

As development progresses, additional documentation on getting started along with example configuration and CI scripts will become available.

It is expected that the Meltano project will have many applications managed in the top level of the project. Some or parts of these applications could be useful to many organizations, and some may only be useful within GitLab. We have no plans on weighing the popularity of an individual application at the top level of the Meltano project for inclusion/exclusion.

**Notes**

- _Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields._
- _The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription._

### Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the [Data Lifecycle].

Our CLI tool provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data lifecycle.

#### Meltano Schema

Helper functions to manage the data warehouse. At the moment, these are PGSQL specific.

#### Create Schema and Roles

Create and grant usage for a database schema.

### Meltano Model

Meltano Models allow you to model your data so you can easily analyze and visualize it in Meltano Analyze.

### Meltano Transform

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