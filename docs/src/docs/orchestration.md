---
sidebarDepth: 2
---

# Orchestration

## Airflow

Meltano uses [Airflow](https://apache.airflow.org) in order to schedule jobs. Please find below documentation on how it can be used.

### Getting started


```bash
# Add airflow in your Meltano project
$ meltano add orchestrator airflow
```

The above will install airflow and make it available to use via `meltano invoke`, which will give you raw access to the underlying plugin after any configuration hooks.

Meltano ships out-of-the-box with a sample DAG for your current project, which is located at `orchestrate/dags/meltano.py`.
Airflow is a full-featured orchestrator that has a lot of features that are currently outside of Meltano's scope. As we are improving this integration, Meltano will facade more of these feature to create a seamless experience using this orchestrator. Please refer to the [Airflow documentation](https://airflow.apache.org/) for more in-depth knowledge about Airflow.

```bash
# View 'meltano' dags
$ meltano invoke airflow list_dags

# Manually trigger a task to run
$ meltano invoke airflow run --raw meltano extract_load $(date -I)

# Start the airflow ui - currently starts in a separate browser
$ meltano invoke airflow webserver -D

# start the airflow scheduler, enabling background job processing
$ meltano invoke airflow scheduler -D

# trigger a dag run
$ meltano invoke airflow trigger_dag meltano
```

### What's next?

  - Kubernetes executor support for Meltano
