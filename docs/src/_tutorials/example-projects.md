---
title: Example Meltano Projects
description: Learn how others are using Meltano by viewing their production Meltano projects.
layout: doc
---
If you have a production project that you'd like to add please open a [Pull Request](https://github.com/meltano/meltano/edit/main/docs/src/_tutorials/example-projects.md).

We group example projects into three categories:
1. Running in production
2. Simpler examples usually solving one problem
3. Complete sandbox projects to play around with

### 1. Running in production

The following Meltano projects are real-world examples of Meltano in production use. If you're about to launch your pipelines
into your own production environment or want to take a look at how others organize their projects, these projects are a great place to start.

- **[Meltano Squared](https://github.com/meltano/squared)** - This is the project the Meltano team uses to manage their Meltano instance. Meltano Squared is quite comprehensive running on kubernetes, leveraging multiple yaml files, environments, plugin inheritance, Great Expectations, SQLFluff, dbt, Airflow and Superset.
- **[GitLab Data Meltano](https://gitlab.com/gitlab-data/gitlab-data-meltano)** - This is the project GitLab uses to manage Meltano.

### 2. Simple Meltano example projects

The following Meltano projects are designed to illustrate a solution to one problem, like how to add SQLFluff as dbt linter. If you're looking for hints on a specific problem, go through this list.

- **[Meltano & SQLFluff for dbt](https://gitlab.com/rabidaudio/meltano-sqlfluff-example)** - A simple project setting up SQLFluff via meltano as a linter for dbt (also via Meltano).
- **[Data Stack 4 Fun & Nonprofits](https://github.com/andrewcstewart/ds4fnp)** - A larger setup accompanied by a tutorial series setting up Meltano, Gitpod, dbt and superset.
- **[Meltano Getting Started Project](https://github.com/meltano/demo-project)** - If you follow the getting started doc part, this will be the resulting Meltano project.
- **[Meltano orchestrating dbt using Airflow](https://github.com/pnadolny13/meltano_example_implementations/tree/main/meltano_projects/dbt_orchestration)** - Meltano project orchestrating the loading of CSVs into a database with a dbt run afterwards. Also self-contained. There also is a [video demonstrating this dbt & Airflow project in action](https://www.youtube.com/watch?v=pNGJ96HOioM&t=919s).


### 3. Sandbox projects

The following projects are beginner projects with mocks, local CSVs, local databases to make them self-contained. A great place to peek into if you want to see Meltano projects in action for the first time and play around with basic functionality like extracting a CSV and loading it into a database.

- **[Meltano Dbt Jaffle shop](https://github.com/pnadolny13/meltano_example_implementations/tree/main/meltano_projects/singer_dbt_jaffle)** - The dbt jaffle shop project placed in a meltano context, with local postgres, completely self-contained.
- **[Meltano Extract Load Example](https://github.com/sbalnojan/meltano-example-el)** - A simple AWS S3 CSV extract and load into a PostgreSQL database. All mocked and completely self-contained.
- **[Meltano DB -> DB Example](https://github.com/sbalnojan/meltano-example-el-db)** - A simple extract from a Postgres database and load into a second Postgres database. All mocked and completely self-contained.
