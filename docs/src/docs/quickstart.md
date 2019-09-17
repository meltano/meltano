# Getting Started

Now that you have successfully [installed Meltano](/docs/installation.html) and its requirements, you can create your first project.

:::tip
Remember, all interactions with the `meltano` command must be run inside the virtual environment you created in the installation process.

If your prompt still starts with `(meltano)`, you're good. If not, please [re-activate your virtual environment](/docs/installation.html#activating-your-virtual-environment) before continuing.
:::

## Creating Your First Project

To initialize a new project, navigate to the directory that you'd like to contain your Meltano projects, and run this command, replacing `PROJECT_NAME` with whatever you would like your new project to be called:

```bash
meltano init PROJECT_NAME
```

This will create a new directory named `PROJECT_NAME` and initialize Meltano's basic directory structure inside it.

:::tip
For those new to the command line, your `PROJECT_NAME` should not have spaces in the name and should use dashes instead. For example, `my project` will not work; but `my-project` will.
:::

### Anonymous usage data

By default, Meltano shares anonymous usage data with the Meltano team using Google Analytics. We use this data to learn about the size of our user base and the specific Meltano features they are (not yet) using, which helps us determine the highest impact changes we can make in each weekly release to make Meltano even more useful for you and others like you.

If you'd prefer to use Meltano _without_ sending the team this kind of data, you can disable tracking entirely using one of these methods:

- When creating a new project, pass `--no_usage_stats` to `meltano init`: 

    ```bash
    meltano init PROJECT_NAME --no_usage_stats
    ```

- In an existing project, disable the `send_anonymous_usage_stats` setting in the `meltano.yml` file:

    ```bash
    send_anonymous_usage_stats: false
    ```

- To disable tracking in all projects in one go, set the `MELTANO_DISABLE_TRACKING` environment variable to `True`: 

    ```bash
    # Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
    export MELTANO_DISABLE_TRACKING=True
    ```

## Starting the Meltano UI

Now that you've created your first Meltano project, change to the new directory and start the Meltano UI:

```bash
cd PROJECT_NAME
meltano ui
```

Meltano is now running, so you can start adding data sources, configuring reporting databases, scheduling updates and building dashboards.

Open your web browser and visit  [http://localhost:5000](http://localhost:5000) to get started.

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

## Scheduling the ELT with Orchestration

If you're using SaaS tools to manage support, sales, marketing, revenue and other business functions you know your data is constantly changing. To keep your dashboards up to date, Meltano provides Orchestration using Apache Airflow, which is automatically installed when the Meltano UI is launched for the first time.

When a new pipeline schedule is created following the steps under [Running the ELT](#running-the-elt), a [DAG](https://airflow.apache.org/concepts.html#dags) is automatically created in Airflow as well, which represents "a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies".

Now click "Orchestration" in the navigation bar or visit [http://localhost:5000/orchestration](http://localhost:5000/orchestration) and you will see your schedule listed within the Airflow UI.

![Meltano UI first scheduled ELT in Airflow](/screenshots/meltano-ui-first-schedule.png)

For a deeper explanation of how to use Meltano Orchestration with Airflow, visit Meltano's [Orchestration documentation](/docs/meltano-cli.html#orchestration.html).

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


## Doing More With Meltano

Learn about more Meltano recipes and functionality with [Advanced Tutorials](/docs/tutorial.html).