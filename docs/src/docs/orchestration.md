## Orchestration

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using Apache Airflow, which is automatically installed when the Meltano UI is launched for the first time.

When a new pipeline schedule is created following the steps under [Running the ELT](#running-the-elt), a [DAG](https://airflow.apache.org/concepts.html#dags) is automatically created in Airflow as well, which represents "a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies".

Meltano uses [Airflow](https://apache.airflow.org) to schedule jobs.

### Installing Airflow

Change directories so that you are inside your Meltano project, and then run the following command to make Airflow available to use via `meltano invoke`

```bash
meltano add orchestrator airflow
```

If you are already in the Meltano UI, you will need to kill it, and re-start it with `meltano ui` to activate the Orchestration tab.

Now you have Airflow installed, let's create a simple example schedule to confirm everything is working correctly.

Meltano ships out-of-the-box with a dynamic DAG, which is a DAG generator for your current project located at `orchestrate/dags/meltano.py` .

### Create a Schedule

To regularly schedule your ELT to run, do the following

```bash
meltano schedule [SCHEDULE_NAME] [EXTRACTOR_NAME] [TARGET_NAME] [INTERVAL]
```

Example:

```bash
meltano schedule carbon__sqlite tap-carbon-intensity target-sqlite @daily
```

Now that you've scheduled your first DAG, you can refresh the "Orchestration" page and you will see your DAG.

::: tip
IMPORTANT: Your schedule is now created, but it will not be enabled until you toggle the "ON" button. Refresh the page and click the "Refresh" icon under "Links" to see that your DAG is fully running.
:::

To learn more about orchestration functionality, check out the [Apache Airflow documentation](https://apache.airflow.org).

#### Other Things You Can Do With Airflow

Currently, `meltano invoke` gives you raw access to the underlying plugin after any configuration hooks.

View 'meltano' dags:

```bash
meltano invoke airflow list_dags
```

Manually trigger a task to run:

```bash
meltano invoke airflow run --raw meltano extract_load $(date -I)
```

Start the airflow ui - currently starts in a separate browser:

```bash
meltano invoke airflow webserver -D
```

Start the airflow scheduler, enabling background job processing:

```bash
meltano invoke airflow scheduler -D
```

Trigger a dag run:

```bash
meltano invoke airflow trigger_dag meltano
```

Airflow is a full-featured orchestrator that has a lot of features that are currently outside of Meltano's scope. As we are improving this integration, Meltano will facade more of these feature to create a seamless experience using this orchestrator. Please refer to the [Airflow documentation](https://airflow.apache.org/) for more in-depth knowledge about Airflow.
