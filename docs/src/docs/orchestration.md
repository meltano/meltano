---
sidebarDepth: 2
---

# Orchestration

## Airflow

Meltano supports [Airflow](https://apache.airflow.org) to manage the orchestration of the various components it provides.

### Getting started

First, add Airflow in your Meltano project.

```bash
$ meltano add orchestrator airflow
```

This will install airflow and make it available to use via `meltano invoke`. 

::: heads-up
Using `meltano invoke` gives you raw access to the underlying plugin after any configuration hooks.
:::

Meltano ships out-of-the-box with a sample DAG for your current project, which is located at `orchestrate/dags/meltano.py`; feel free to take a peek.

We are now ready to use Airflow, here's a little tour of what we can do.

::: tip
Airflow is a full-featured orchestrator that has a lot of features that are currently outside of Meltano's scope. As we are improving this integration, Meltano will facade more of these feature to create a seamless experience using this orchestrator.

Please refer to the [Airflow documentation](https://airflow.apache.org/) for more in-depth knowledge about Airflow.
:::

```bash
# notice the 'meltano' dag listed here
$ meltano invoke airflow list_dags

# manually trigger a task to run
$ meltano invoke airflow run --raw meltano extract_load $(date -I)

# start the airflow ui
$ meltano invoke airflow webserver -D

# start the airflow scheduler, enabling background job processing
$ meltano invoke airflow scheduler -D

# trigger a dag run
$ meltano invoke airflow trigger_dag meltano
```

### What's next?

  - Kubernetes executor support for Meltano
