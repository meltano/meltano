# Quick Start Guide

Now that you have successfully [installed Meltano]('/docs/installation.html) and its requirements, you can create your first project. 

:::tip
Before you begin, you must activate the virtual environment you created in the installation process on the command line. All the commands below should be run inside this virtual environment.
:::

Remember, to activate your virtual enviroment, you will need to run: 

```bash
# Linux, OSX
$ source ~/virtualenvs/meltano/bin/activate

# Windows
$ %ALLUSERSPROFILE%\\virtualenvs\\meltano\\Scripts\\activate.bat
```

## Creating Your First Project

Run this command in your terminal to initialize a new project:

```bash
$ meltano init PROJECT_NAME
```

:::tip
For those new to the command line, your PROJECT_NAME should not have spaces in the name and should use dashes instead. For example, "my project" will not work; but "my-project" will.
:::

Creating a project also creates a new directory with the name you gave it. Change to the new directory and then start Meltano with these commands:

```bash
$ cd PROJECT_NAME
$ meltano ui
```

Meltano is now running, so you can start adding data sources, configuring reporting databases, scheduling updates and building dashboards. 

Open your Internet browser and visit  [http://localhost:5000](http://localhost:5000) get started.

## Connecting Data Sources

When you visit the [http://localhost:5000](http://localhost:5000), you should see:

Do this in the Meltano UI under "Pipelines" in *Step 1, Extractors*. [http://localhost:5000/pipelines/extractors](http://localhost:5000/pipelines/extractors)

![Meltano UI with all extractors not installed initial loading screen](/screenshots/meltano-extractors-newinstall.png)

## Selecting Entities

Data sources can contain a LOT of different entities, and you might not want Meltano to pull every data source into your dashboard. In this step, you can choose which to include.

Do this in the Meltano UI under "Pipelines" in *Step 2, Entities*. [http://localhost:5000/pipelines/entities](http://localhost:5000/pipelines/entities)

![Meltano UI pipeline entities screen new install](/screenshots/meltano-pipeline-entities-quickstart.png)

## Selecting a Reporting Database

Now that Meltano is pulling data in from your data source(s), you need to choose where and in what format you would like that data stored. 

Do this in the Meltano UI under "Pipelines" in *Step 3, Loaders*. [http://localhost:5000/pipelines/loaders](http://localhost:5000/pipelines/loaders)

![Meltano UI pipeline targets new install](/screenshots/meltano-pipelines-targets-quickstart.png)

## Running the ELT

::: tip
Right now, this can't be done from the Meltano UI so you will have to return to your command line interface. 
:::

Run the following command

```bash
$ meltano elt [YOUR_TAP_NAME] [YOUR_TARGET_NAME]
#Extract & load complete!

#Example
$ meltano elt tap-carbon-intensity target-sqlite
```

### Using the Correct Syntax

To get a full list of all the availble taps and targets, run this command:

```bash
$ meltano discover all
```

## Scheduling the ELT with Orchestration

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using Apache Airflow.

::: tip
Right now, Airflow can not be installed from inside Meltano's UI so you need to return to your command line interface.
:::

Run the following command:

```bash
$ meltano add orchestrator airflow
#Added 'airflow' to your Meltano project.
#Activated 'airflow' virtual environment.
#Installed 'airflow'.
#Added and installed orchestrators 'airflow'.
```

One Airflow is installed, create your first test schedule using the ELT you ran in the previous step:

```bash

$ meltano schedule [NEW_SCHEDULE_NAME] [YOUR_TAP] [YOUR_TARGET] [INTERVAL]

#Example
$ meltano schedule carbon__sqlite tap-carbon-intensity target-sqlite @daily
```

To check that your scheduling was successful, and created a DAG in Airflow run the following command:

```bash
$ meltano invoke airflow list_dags

-------------------------------------------------------------------
DAGS
-------------------------------------------------------------------
meltano_carbon__sqlite
```

:::tip
To see a list of all your scheduled DAGs within the Meltano UI under "Orchestration" you will need to kill your terminal window running the `meltano ui` command and then restart it. You will only need to do this the first time you install Airflow.
:::

```bash
$ control+c
$ meltano ui
```

Now click "Orchestration" in the navigation bar or visit [http://localhost:5000/orchestration](http://localhost:5000/orchestration) and you will see your schedule listed within the Airflow UI.

![Meltano UI first scheduled ELT in Airflow](/screenshots/meltano-ui-first-schedule.png)

For a deeper explanation of how to use Meltano Orchestration with Airflow visit our [Orchestration documentation](/docs/meltano-cli.html#orchestration.html).

## Analyzing Your Data

Congratulations! Now that you've ingested data into Meltano, created a reporting database, and scheduled regular updates to your data set you're ready to go! 

Start exploring and analyzing your data and build dashboards with [Meltano Analyze](http://localhost:5000/analyze).

:::tip
Right now, models can not be added from inside Meltano's UI so you will need to return to your command line interface. This command line step is temporary, and the work to integrate it directly into Meltano's UI is being tracked in [Issue #651](https://gitlab.com/meltano/meltano/issues/651).
:::

To find a list of available models, run this command:

```bash
$ meltano discover models

models
model-carbon-intensity
model-carbon-intensity-sqlite
model-gitflix
model-gitlab
model-salesforce
model-stripe
model-zendesk
model-zuora
```

Choose the relevant model to the data source you've connected, and run the command:

```bash
$ meltano add model [MODEL_NAME]

#Example
$ meltano add model model-carbon-intensity
```

Now that you've added your model, you're Analyze page will contain a link to view that model as an interactive dashboard.


## Doing More With Meltano

Learn about more Meltano recipes and functionality with [Advanced Tutorials](/docs/tutorial.html).