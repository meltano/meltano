# Getting Started

Now that you have successfully [installed Meltano](/docs/installation.html) and its requirements, you can create your first project.

## Creating Your First Project

:::tip
Before you begin, you must activate the virtual environment you created in the installation process on the command line. All the commands below should be run inside this virtual environment.
:::

Remember, to activate your virtual enviroment, you will need to run:

```bash
# Linux, OSX
source ~/virtualenvs/meltano/bin/activate

# Windows
%ALLUSERSPROFILE%\\virtualenvs\\meltano\\Scripts\\activate.bat
```

Run this command in your terminal to initialize a new project:

```bash
meltano init PROJECT_NAME
```

:::tip
For those new to the command line, your PROJECT_NAME should not have spaces in the name and should use dashes instead. For example, "my project" will not work; but "my-project" will.
:::

Creating a project also creates a new directory with the name you gave it. Change to the new directory and then start Meltano with these commands:

```bash
cd PROJECT_NAME
meltano ui
```

Meltano is now running, so you can start adding data sources, configuring reporting databases, scheduling updates and building dashboards.

Open your Internet browser and visit  [http://localhost:5000](http://localhost:5000) to get started.

## Connecting Data Sources

When you visit [http://localhost:5000](http://localhost:5000), you should see:

Do this in the Meltano UI under "Pipelines" in *Step 1, Extractors*. [http://localhost:5000/pipelines/extractors](http://localhost:5000/pipelines/extractors)

![Meltano UI with all extractors not installed initial loading screen](/screenshots/meltano-extractors-newinstall.png)

## Selecting Entities

Data sources can contain a LOT of different entities, and you might not want Meltano to pull every data source into your dashboard. In this step, you can choose which to include by clicking the "Edit Selections" button of an installed extractor.

Do this in the Meltano UI under "Pipelines" in *Step 2, Entities*. [http://localhost:5000/pipelines/entities](http://localhost:5000/pipelines/entities)

![Meltano UI pipeline entities screen new install](/screenshots/meltano-pipeline-entities-quickstart.png)

## Selecting a Reporting Database

Now that Meltano is pulling data in from your data source(s), you need to choose where and in what format you would like that data stored.

Do this in the Meltano UI under "Pipelines" in *Step 3, Loaders*. [http://localhost:5000/pipelines/loaders](http://localhost:5000/pipelines/loaders)

![Meltano UI pipeline targets new install](/screenshots/meltano-pipelines-targets-quickstart.png)

## Running the ELT

Now that you've selected your reporting database, you can schedule and run your ELT pipeline.

Do this in the Meltano UI under "Pipelines" in *Step 4, Schedules*. [http://localhost:5000/pipelines/schedules](http://localhost:5000/pipelines/schedules)

![Meltano UI pipeline schedules screen create schedule](/screenshots/meltano-ui-create-schedule.png)

Once you've created your first schedule, you will see it here:

![Meltano UI list of schedules](/screenshots/meltano-pipeline-schedule.png)

From here, you can schedule "Run" to initiate the ELT ad hoc. This will run the process that pulls data from the target you selected into your reporting database, so you can Analyze it.

## Analyzing Your Data

Congratulations! Now that you've ingested data into Meltano, created a reporting database, and scheduled regular updates to your dataset you're ready to analyze!

There are just three steps to take:
1. Go to [http://localhost:5000/analyze](http://localhost:5000/analyze)
2. Click the Install button of your desired analysis model
3. Once installed, click the corresponding analysis model's Analyze button

  ![Meltano UI - Models Analyze](/screenshots/meltano-ui-analyze-models.png)

You're Analyze page contains links for viewing corresponding analyses. Each manifests as an interactive query builder and data visualizer. Start exploring and analyzing your data and then build savable and shareable dashboards.

Begin exploring, querying, and visualizing your data using Meltano Analyze.

![Meltano UI analyze example carbon emissions data explorer](/screenshots/meltano-ui-analyze-example.png)

After you "Run Query" you can view charts and graphs, and save interesting query results to your dashboards.

## Scheduling the ELT with Orchestration

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using Apache Airflow.

To install airflow, navigate to the "Orchestrate" page and click "Install Airflow".

![Meltano UI to install Airflow](/screenshots/meltano-install-airflow-from-ui.png)

Once Airflow is installed, you can view the ELT pipeline schedule(s) created in the previous [Running the ELT](#running-the-elt) step via Meltano UI where a DAG gets created for each pipeline schedule.

A [DAG](https://airflow.apache.org/concepts.html#dags) is automatically created in Airflow and "is a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies".

:::tip
To see a list of all your scheduled DAGs within the Meltano UI under "Orchestration" you will need to kill your terminal window running the `meltano ui` command and then restart it. You will only need to do this the first time you install Airflow.
:::


```bash
# After installing Airflow, you will need to shut down your current instance of Meltano and restart
meltano ui
```

Now click "Orchestration" in the navigation bar or visit [http://localhost:5000/orchestration](http://localhost:5000/orchestration) and you will see your schedule listed within the Airflow UI.

![Meltano UI first scheduled ELT in Airflow](/screenshots/meltano-ui-first-schedule.png)

For a deeper explanation of how to use Meltano Orchestration with Airflow, visit Meltano's [Orchestration documentation](/docs/meltano-cli.html#orchestration.html).

### Troubleshooting Airflow ###

If you run into issues, it is possible that you could end up with multiple instances of Airflow running at the same time. This is a known issue ([#821](https://gitlab.com/meltano/meltano/issues/812)) common if you have been working with multiple Meltano projects, or have killed Meltano UI from the command line.

To troubleshoot, run `sudo lsof -i -P | grep -i "listen"` from your command line. If you see multiple instances of Python running on Port 5010, kill the first instance with `kill 12345` (using the number for your instance). Then run `meltano ui` and try again.


## Doing More With Meltano

Learn about more Meltano recipes and functionality with [Advanced Tutorials](/docs/tutorial.html).