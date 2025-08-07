---
title: Orchestrate Data
description: Learn how to schedule and orchestrate your pipelines using Meltano and Airflow.
layout: doc
sidebar_position: 6
---

Most data pipelines aren't run just once, but over and over again, to make sure additions and changes in the source eventually make their way to the destination.

To help you realize this, Meltano supports scheduled pipelines that can be orchestrated using [Apache Airflow](https://airflow.apache.org/).

When a new pipeline schedule is created using the [CLI](/reference/command-line-interface#schedule), a [DAG](https://airflow.apache.org/concepts.html#dags) is automatically created in Airflow as well, which represents "a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies".

## Create a Schedule

### Scheduling predefined jobs

To regularly schedule your pipeline to run first define it as a [job](/reference/command-line-interface#job) within your project.
Then you can schedule it using the [`meltano schedule add`](/reference/command-line-interface#schedule) command:

```bash
# Define a job
meltano job add tap-gitlab-to-target-postgres-with-dbt --tasks "tap-gitlab target-postgres dbt-postgres:run"

# Schedule the job
meltano schedule add daily-gitlab-load --job tap-gitlab-to-target-postgres-with-dbt --interval '@daily'
```

This would add the following schedule to your `meltano.yml`:

```yaml
schedules:
- name: daily-gitlab-load
  interval: '@daily'
  job: tap-gitlab-to-target-postgres-with-dbt
```

If you have schedule-specific environment variables that you would like to pass to the invocation environments of the plugins run by the schedule, you can supply those via the `env` key like so:

```yaml
schedules:
- name: daily-gitlab-load
  interval: '@daily'
  job: tap-gitlab-to-target-postgres-with-dbt
  env:
    SCHEDULE_SPECIFIC_ENV_VAR: schedule_specific_value
```

## Run a schedule manually

You can run a schedule manually using the `meltano schedule run` command:

```bash
meltano schedule run daily-gitlab-load
```

## Installing Airflow

While you can use Meltano's CLI define pipeline schedules,
actually executing them is the orchestrator's responsibility, so let's install Airflow:

Change directories so that you are inside your Meltano project,
and then run the following command to add the
[default DAG generator](https://github.com/meltano/files-airflow/blob/main/bundle/orchestrate/dags/meltano.py)
to your project and make Airflow available to use via `meltano invoke`:

```bash
# Simplified syntax - plugin type is automatically detected
meltano add airflow  # Automatically detected as utility

# Explicit plugin type for disambiguation:
# meltano add --plugin-type utility airflow

# Deprecated positional syntax:
# meltano add utility airflow

meltano invoke airflow:initialize
meltano invoke airflow users create -u admin@localhost -p password --role Admin -e admin@localhost -f admin -l admin
```

See the Airflow docs page on [MeltanoHub](https://hub.meltano.com/utilities/airflow) for more details.

### Using an existing Airflow installation

You can also use the [Meltano DAG generator](https://github.com/meltano/files-airflow/blob/main/bundle/orchestrate/dags/meltano.py)
with an existing Airflow installation, as long as the `MELTANO_PROJECT_ROOT` environment variable is set to point at your Meltano project.

In fact, all `meltano invoke airflow ...` does is [populate `MELTANO_PROJECT_ROOT`](/guide/configuration#accessing-from-plugins),
set Airflow's `core.dags_folder` setting to `$MELTANO_PROJECT_ROOT/orchestrate/dags` (where the DAG generator lives by default),
and invoke the `airflow` executable with the provided arguments.

You can add the Meltano DAG generator to your project without also installing the Airflow orchestrator plugin by adding the [`airflow` file bundle](https://github.com/meltano/files-airflow/):

```bash
meltano add files files-airflow
```

Now, you'll want to copy the DAG generator in to your Airflow installation's `dags_folder`,
or reconfigure it to look in your project's `orchestrate/dags` directory instead.

This setup assumes you'll use `meltano schedule` to schedule your `meltano el`
pipelines, as described above, since the DAG generator iterates over the result of
`meltano schedule list --format=json` and creates DAGs for each.
However, you can also create your own Airflow DAGs for any pipeline you fancy
by using [`BashOperator`](https://airflow.apache.org/docs/apache-airflow/2.10.5/howto/operator/bash.html)
with the [`meltano el` command](/reference/command-line-interface#el), or
[`DockerOperator`](https://airflow.apache.org/docs/apache-airflow-providers-docker/4.3.0/_api/airflow/providers/docker/operators/docker/index.html#module-airflow.providers.docker.operators.docker)
with a [project-specific Docker image](/guide/production#containerized-meltano-project).

## Starting the Airflow scheduler

Now that Airflow is installed and (automatically) configured to look at your project's Meltano DAG generator, let's start the scheduler:

```bash
meltano invoke airflow scheduler
```

Airflow will now run your pipelines on a schedule as long as the scheduler is running!

## Using Airflow directly

You are free to interact with Airflow directly through its own UI. You can start the web like this:

```bash
meltano invoke airflow webserver
```

By default, you'll only see Meltano's pipeline DAGs here, which are created automatically using the dynamic DAG generator included with every Meltano project, located at `orchestrate/dags/meltano.py`.

You can use the bundled Airflow with custom DAGs by putting them inside the `orchestrate/dags` directory, where they'll be picked up by Airflow automatically. To learn more, check out the [Apache Airflow documentation](https://airflow.apache.org).

Meltano's use of Airflow will be unaffected by other usage of Airflow as long as `orchestrate/dags/meltano.py` remains untouched and pipelines are managed through the dedicated interface.

### Other things you can do with Airflow

Currently, `meltano invoke` gives you raw access to the underlying plugin after any configuration hooks.

View 'meltano' dags:

```bash
meltano invoke airflow dags list
```

Manually trigger a task to run:

```bash
meltano invoke airflow tasks run --raw meltano extract_load $(date -I)
```

Start the Airflow UI: (will start in a separate browser)

```bash
meltano invoke airflow webserver
```

Start the Airflow scheduler, enabling job processing:

```bash
meltano invoke airflow scheduler
```

Trigger a dag run:

```bash
meltano invoke airflow dags trigger meltano
```

Airflow is a full-featured orchestrator that has a lot of features that are currently outside of Meltano's scope. As we are improving this integration, Meltano will facade more of these feature to create a seamless experience using this orchestrator. Please refer to the [Airflow documentation](https://airflow.apache.org/) for more in-depth knowledge about Airflow.
