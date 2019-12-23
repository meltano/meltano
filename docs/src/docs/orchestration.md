## Orchestration

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using [Apache Airflow](https://apache.airflow.org).

When a new pipeline schedule is created using the [UI](/docs/getting-started.html#create-a-pipeline-schedule) or [CLI](/docs/command-line-interface.html#schedule), a [DAG](https://airflow.apache.org/concepts.html#dags) is automatically created in Airflow as well, which represents "a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies".

Airflow is automatically installed when the Meltano UI is launched for the first time, and the scheduler automatically runs in the background while Meltano UI is running.

### Installing Airflow

If you're not using Meltano UI, you'll need to install Airflow manually:

Change directories so that you are inside your Meltano project, and then run the following command to make Airflow available to use via `meltano invoke`

```bash
meltano add orchestrator airflow
```

Now you have Airflow installed, let's create a simple example schedule to confirm everything is working correctly.

### Create a Schedule

To regularly schedule your ELT to run, use the ["Pipeline" interface in the UI](/docs/getting-started.html#create-a-pipeline-schedule), or the following command:

```bash
meltano schedule [SCHEDULE_NAME] [EXTRACTOR_NAME] [TARGET_NAME] [INTERVAL]
```

Example:

```bash
meltano schedule carbon__sqlite tap-carbon-intensity target-sqlite @daily
```

Now that you've scheduled your first DAG, you can load the "Pipeline" page in the UI and see it show up.

### Using Airflow directly

You are free to interact with Airflow directly through its own UI. You can start the web like this:

```bash
meltano invoke airflow webserver -D
```

By default, you'll only see Meltano's pipeline DAGs here, which are created automatically using the dynamic DAG generator included with every Meltano project, located at `orchestrate/dags/meltano.py`.

You can use the bundled Airflow with custom DAGs by putting them inside the `orchestrate/dags` directory, where they'll be picked up by Airflow automatically. To learn more, check out the [Apache Airflow documentation](https://apache.airflow.org). 

Meltano's use of Airflow will be unaffected by other usage of Airflow as long as `orchestrate/dags/meltano.py` remains untouched and pipelines are managed through the dedicated interface.

#### Other things you can do with Airflow

Currently, `meltano invoke` gives you raw access to the underlying plugin after any configuration hooks.

View 'meltano' dags:

```bash
meltano invoke airflow list_dags
```

Manually trigger a task to run:

```bash
meltano invoke airflow run --raw meltano extract_load $(date -I)
```

Start the Airflow UI: (will start in a separate browser)

```bash
meltano invoke airflow webserver -D
```

Start the Airflow scheduler, enabling background job processing if you're not already running Meltano UI:

```bash
meltano invoke airflow scheduler -D
```

Trigger a dag run:

```bash
meltano invoke airflow trigger_dag meltano
```

Airflow is a full-featured orchestrator that has a lot of features that are currently outside of Meltano's scope. As we are improving this integration, Meltano will facade more of these feature to create a seamless experience using this orchestrator. Please refer to the [Airflow documentation](https://airflow.apache.org/) for more in-depth knowledge about Airflow.
