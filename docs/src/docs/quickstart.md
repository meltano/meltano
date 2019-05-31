# Quick Start

Now that you have successfully [installed Meltano]('/docs/installation.html) and its requirements, you can create your first project. Once we initialize a new project on the command line, the rest of your work will take place in our web-based user interface.

## Launch Your Virtual Environment

Navigate to the directory in your terminal where you want your Meltano project to be installed. Then run the following commands:

```bash
# Create virtual environment
virtualenv venv

# Activate virtual environment
source venv/bin/activate
```

## Create Your First Project

Run this command in your terminal to initialize a new project:

```bash
meltano init PROJECT_NAME
```

:::tip
For those new to the command line, your PROJECT_NAME should not have spaces in the name and should use dashes instead. For example, "my project" will not work; but "my-project" will.
:::

Creating a project also created a new directory with the name you gave it. Change to the new directory with this command:

```bash
cd PROJECT_NAME
```

Now that you are inside your project directory, start Meltano with this command:

```bash
meltano ui
```

Meltano is now running, so you can start adding data sources and building dashboards. Open your Internet browser and visit  [http://localhost:5000](http://localhost:5000)

## Connect Data Sources

When you visit the [http://localhost:5000](http://localhost:5000), you should see:

![Meltano UI with Carbon API initial loading screen](/screenshots/meltano-ui-carbon-tutorial-output.png)

From this screen, you can select data source(s) Meltano should ingest into your project using [Plugins](/docs/plugins.html)

## Select Entities

Many data sources contain a LOT of different entities, and you might not want Meltano to pull all of them into your dashboard. In this step, you can choose which data points you want to include.

## Select Data Targets

Now that Meltano is pulling data in from your data source(s), it needs to know where and in what format you would like that data stored.

## Run the ELT

::: tip
Right now, this can't be done from the Meltano UI so you will have to return to your command line interface. 
:::

Run the following command

```bash
meltano elt [YOUR_TAP_NAME] [YOUR_TARGET_NAME]

#Example
meltano elt tap-carbon-intensity target-sqlite
```

### Using the Correct Syntax

To get a full list of all the availble taps and targets, run this command:

```bash
meltano discover all
```

## Schedule ELT Jobs

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using Apache Airflow.

::: tip
Right now, Airflow can not be installed from inside Meltano's UI so you will ahve to return to your command line interface.
:::

Run the following command:

```bash
meltano add orchestrator airflow
```

One Airflow is installed, create your first test schedule using the ELT you ran in the previous step:

```bash

meltano schedule [YOUR_TAP] [YOUR_TARGET] [INTERVAL]

#Example
meltano schedule carbon__sqlite tap-carbon-intensity target-sqlite @daily
```

To check that your scheduling was successful, and created a DAG in Airflow run the following command:

```bash
meltano invoke airflow list_dags

-------------------------------------------------------------------
DAGS
-------------------------------------------------------------------
meltano_carbon__sqlite
```

:::tip
To see a list of all your scheduled DAGs within the Meltano UI under "Orchestration" you will need to kill your terminal window running the `meltano ui` command and then restart it. You will only need to do this the first time you install Airflow.
:::

## Doing More With Meltano

Congratulations! You connected your first data source, configured your ELT to run, and scheduled it to regularly update. Now you're ready to learn about more advanced functionality with [Advanced Tutorials](/docs/tutorial.html).