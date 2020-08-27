---
metaTitle: "Getting Started with Meltano: open source ELT"
description: If you're ready to get started with Meltano and run an EL(T) pipeline with a data source and destination of your choosing, you've come to the right place!
---

# Getting Started

Welcome! If you're ready to get started with Meltano and [run an EL(T) pipeline](#run-a-data-integration-el-pipeline)
with a [data source](#add-an-extractor-to-pull-data-from-a-source) and [destination](#add-a-loader-to-send-data-to-a-destination) of your choosing, you've come to the right place!

::: tip Short on time, or just curious what the fuss is about?

To get a sense of the Meltano experience in just a few minutes, follow the [examples on the homepage](/).

They can be copy-pasted right into your terminal and will take you all the way through
[installation](/#installation), [data integration (EL)](/#integration), [data transformation (T)](/#transformation), [orchestration](/#orchestration), and [containerization](/#containerization)
with the [`tap-gitlab` extractor](/plugins/extractors/gitlab.html)
and the [`target-jsonl`](/plugins/loaders/jsonl.html) and [`target-postgres`](/plugins/loaders/postgres.html) loaders.

:::

## Install Meltano

Before you can get started with Meltano and the [`meltano` CLI](/docs/command-line-interface.html), you'll need to install it onto your system.

*To learn more about the different installation methods, refer to the [Installation guide](/docs/installation.html).*

### Local installation

If you're running Linux or macOS and have [Python](https://www.python.org/) 3.6 or 3.7 installed (Python 3.8 is [not currently supported](https://gitlab.com/meltano/meltano/-/issues/1956)),
we recommend installing Meltano into a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment)
inside the directory that will hold your [Meltano projects](/docs/project.html).

1. Create and navigate to a directory to hold your Meltano projects:

    ```bash
    mkdir meltano-projects
    cd meltano-projects
    ```

1. Create and activate a virtual environment for Meltano inside the `.venv` directory:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

1. Install the [`meltano` package from PyPI](https://pypi.org/project/meltano/):

    ```bash
    pip3 install meltano
    ```

1. Optionally, verify that the [`meltano` CLI](/docs/command-line-interface.html) is now available by viewing the version:

    ```bash
    meltano --version
    ```

If anything's not behaving as expected, refer to the ["Local Installation" section](/docs/installation.html#local-installation) of the [Installation guide](/docs/installation.html) for more details.

### Docker installation

Alternatively, and assuming you already have [Docker](https://www.docker.com/) installed and running,
you can use the [`meltano/meltano` Docker image](https://hub.docker.com/r/meltano/meltano) which exposes the [`meltano` CLI command](/docs/command-line-interface.html) as its [entrypoint](https://docs.docker.com/engine/reference/builder/#entrypoint).

1. Pull or update the latest version of the Meltano Docker image:

    ```bash
    docker pull meltano/meltano:latest
    ```

1. Optionally, verify that the [`meltano` CLI](/docs/command-line-interface.html) is now available by viewing the version:

    ```bash
    docker run meltano/meltano --version
    ```

If anything's not behaving as expected, refer to the ["Installing on Docker" section](/docs/installation.html#installing-on-docker) of the [Installation guide](/docs/installation.html) for more details.

## Create your Meltano project

Now that you have a way of running the [`meltano` CLI](/docs/command-line-interface.html),
it's time to create a new [Meltano project](/docs/project.html) that (among other things)
will hold the [plugins](/docs/plugins.html) that implement the various details of your ELT pipelines.

*To learn more about Meltano projects, refer to the ["The Meltano Project" concept guide](/docs/project.html).*

1. Navigate to the directory that you'd like to hold your Meltano projects, if you didn't already do so earlier:

    ```bash
    mkdir meltano-projects
    cd meltano-projects
    ```

1. Initialize a new project in a directory of your choosing using [`meltano init`](/docs/command-line-interface.html#init):

    ```bash
    meltano init <project directory name>

    # For example:
    meltano init my-meltano-project

    # If you're using Docker, don't forget to mount the current working directory:
    docker run -v $(pwd):/projects -w /projects meltano/meltano init my-meltano-project
    ```

1. Navigate to the newly created project directory:

    ```bash
    cd <project directory>

    # For example:
    cd my-meltano-project
    ```

1. Optionally, if you'd like to version control your changes, initialize a [Git](https://git-scm.com/) repository and create an initial commit:

    ```bash
    git init
    git add --all
    git commit -m 'Initial Meltano project'
    ```

    This will allow you to use [`git diff`](https://git-scm.com/docs/git-diff)
    to easily check the impact of the [`meltano` commands](/docs/command-line-interface.html)
    you'll run below on your project files, most notably `meltano.yml`.

## Add an extractor to pull data from a source

Now that you have your very own Meltano project, it's time to add some [plugins](/docs/plugins.html) to it!

The first plugin you'll want to add is an [extractor](/docs/plugins.html#extractors),
which will be responsible for pulling data out of your data source.

*To learn more about adding plugins to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-extractors-and-loaders-to-your-project).*

1. Find out if an extractor for your data source is already [known to Meltano](/docs/contributor-guide.html#known-plugins)
by checking the [Extractors list](/plugins/extractors/) on this website, or using [`meltano discover`](/docs/command-line-interface.html#discover):

    ```bash
    meltano discover extractors
    ```

1. Depending on the result, pick your next step:

    - If a known extractor is **available**, add it to your project using [`meltano add`](/docs/command-line-interface.html#add):

      ```bash
      meltano add extractor <plugin name>

      # For example:
      meltano add extractor tap-gitlab

      # If you're using Docker, don't forget to mount the project directory:
      docker run -v $(pwd):/project -w /project meltano/meltano add extractor tap-gitlab
      ```

      You can now continue to step 4.

    - If an extractor is **not yet known** to Meltano, find out if a Singer tap for your data source already exists by checking [Singer's index of taps](https://www.singer.io/#taps) and/or doing a web search for `Singer tap <data source>`, e.g. `Singer tap COVID-19`.

1. Depending on the result, pick your next step:

    - If a Singer tap for your data source is **available**, add it to your project as a [custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins) using [`meltano add --custom`](/docs/command-line-interface.html#add):

        ```bash
        meltano add --custom extractor <tap name>

        # For example:
        meltano add --custom extractor tap-covid-19

        # If you're using Docker, don't forget to mount the project directory,
        # and ensure that interactive mode is enabled so that Meltano can ask you
        # additional questions about the plugin and get your answers over STDIN:
        docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom extractor tap-covid-19
        ```

        Meltano will now ask you some additional questions to learn more about the plugin.

        *To learn more about adding custom plugins, refer to the ["`meltano add`: How to use: Custom plugins" section](/docs/command-line-interface.html#how-to-use-custom-plugins) of the [CLI Reference](/docs/command-line-interface.html#add).*

        ::: tip
        Once you've successfully added your custom plugin to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!
        :::

    - If a Singer tap for your data source **doesn't exist yet**, learn how to build your own tap by following the ["Create a Custom Extractor" tutorial](/tutorials/create-a-custom-extractor.html) or [Singer's "Developing a Tap" guide](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-tap).

        Once you've got your new tap project set up, you can add it to your Meltano project
        as a custom plugin by following the `meltano add --custom` instructions above.
        When asked to provide a `pip install` argument, you can provide a local directory path or Git repository URL.

1. Optionally, verify that the extractor was installed successfully and that its executable can be invoked using [`meltano invoke`](/docs/command-line-interface.html#invoke):

    ```bash
    meltano invoke <plugin> --help

    # For example:
    meltano invoke tap-gitlab --help
    ```

    If you see the extractor's help message printed, the plugin was definitely installed successfully,
    but an error message related to missing configuration or an unimplemented `--help` flag
    would also confirm that Meltano can invoke the plugin's executable.

### Configure the extractor

Chances are that the extractor you just added to your project will require some amount of [configuration](/docs/configuration.html) before it can start extracting data.

*To learn more about managing the configuration of your plugins, refer to the [Configuration guide](/docs/configuration.html).*

1. Find out what settings your extractor supports using [`meltano config <plugin> list`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin> list

    # For example:
    meltano config tap-gitlab list
    ```

1. Assuming the previous command listed at least one setting, set appropriate values using [`meltano config <plugin> set`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin> set <setting> <value>

    # For example:
    meltano config tap-gitlab set projects meltano/meltano
    meltano config tap-gitlab set start_date 2020-05-01T00:00:00Z
    ```

1. Optionally, verify that the configuration looks like what the Singer tap expects according to its documentation using [`meltano config <plugin>`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin>

    # For example:
    meltano config tap-gitlab
    ```

### Select entities and attributes to extract

Now that the extractor has been configured, it'll know where and how to find your data,
but not yet which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes,
but it's recommended that you [specify the specific entities and attributes you'd like to extract](/docs/integration.html#selecting-entities-and-attributes-for-extraction),
to improve performance and save on bandwidth and storage.

*To learn more about selecting entities and attributes for extraction, refer to the [Data Integration (EL) guide](/docs/integration.html#selecting-entities-and-attributes-for-extraction).*

1. Find out whether the extractor supports entity selection, and if so, what entities and attributes are available, using [`meltano select --list --all`](/docs/command-line-interface.html#select):

    ```bash
    meltano select --list --all <plugin>

    # For example:
    meltano select --list --all tap-covid-19
    ```

    If this command fails with an error, this usually means that the Singer tap does not support [schema discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode), and will always extract all supported entities and attributes.

1. Assuming the previous command succeeded, select the desired entities and attributes for extraction using [`meltano select`](/docs/command-line-interface.html#select):

    ```bash
    meltano select <plugin> <entity> <attribute>
    meltano select <plugin> --exclude <entity> <attribute>

    # For example:
    meltano select tap-covid-19 eu_daily date
    meltano select tap-covid-19 eu_daily country
    meltano select tap-covid-19 eu_daily cases
    meltano select tap-covid-19 eu_daily deaths

    # Include all attributes of an entity
    meltano select tap-covid-19 eu_ecdc_daily "*"

    # Exclude matching attributes of all entities
    meltano select tap-covid-19 --exclude "*" "git_*"
    ```

    As you can see in the example, entity and attribute identifiers can contain wildcards (`*`) to match multiple entities or attributes at once.

1. Optionally, verify that only the intended entities and attributes are now selected using [`meltano select --list`](/docs/command-line-interface.html#select):

    ```bash
    meltano select --list <plugin>

    # For example:
    meltano select --list tap-covid-19
    ```

## Add a loader to send data to a destination

Now that your Meltano project has everything it needs to pull data from your source,
it's time to tell it where that data should go!

This is where the [loader](/docs/plugins.html#loaders) comes in,
which will be responsible for loading [extracted](#add-an-extractor-to-pull-data-from-a-source) data into an arbitrary data destination.

*To learn more about adding plugins to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-extractors-and-loaders-to-your-project).*

1. Find out if a loader for your data destination is already [known to Meltano](/docs/contributor-guide.html#known-plugins)
by checking the [Loaders list](/plugins/loaders/) on this website, or using [`meltano discover`](/docs/command-line-interface.html#discover):

    ```bash
    meltano discover loaders
    ```

1. Depending on the result, pick your next step:

    - If a known loader is **available**, add it to your project using [`meltano add`](/docs/command-line-interface.html#add):

      ```bash
      meltano add loader <plugin name>

      # For example:
      meltano add loader target-postgres
      ```

      You can now continue to step 4.

    - If a loader is **not yet known** to Meltano, find out if a Singer target for your data source already exists by checking [Singer's index of targets](https://www.singer.io/#targets) and/or doing a web search for `Singer target <data destination>`, e.g. `Singer target BigQuery`.

1. Depending on the result, pick your next step:

    - If a Singer target for your data destination is **available**, add it to your project as a [custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins) using [`meltano add --custom`](/docs/command-line-interface.html#add):

        ```bash
        meltano add --custom loader <target name>

        # For example:
        meltano add --custom loader target-bigquery

        # If you're using Docker, don't forget to mount the project directory,
        # and ensure that interactive mode is enabled so that Meltano can ask you
        # additional questions about the plugin and get your answers over STDIN:
        docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom loader target-bigquery
        ```

        Meltano will now ask you some additional questions to learn more about the plugin.

        *To learn more about adding custom plugins, refer to the ["`meltano add`: How to use: Custom plugins" section](/docs/command-line-interface.html#how-to-use-custom-plugins) of the [CLI Reference](/docs/command-line-interface.html#add).*

        ::: tip
        Once you've successfully added your custom plugin to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!
        :::

    - If a Singer target for your data source **doesn't exist yet**, learn how to build your own target by following [Singer's "Developing a Target" guide](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

        Once you've got your new target project set up, you can add it to your Meltano project
        as a custom plugin by following the `meltano add --custom` instructions above.
        When asked to provide a `pip install` argument, you can provide a local directory path or Git repository URL.

1. Optionally, verify that the loader was installed successfully and that its executable can be invoked using [`meltano invoke`](/docs/command-line-interface.html#invoke):

    ```bash
    meltano invoke <plugin> --help

    # For example:
    meltano invoke target-postgres --help
    ```

    If you see the loader's help message printed, the plugin was definitely installed successfully,
    but an error message related to missing configuration or an unimplemented `--help` flag
    would also confirm that Meltano can invoke the plugin's executable.

### Configure the loader

Chances are that the loader you just added to your project will require some amount of [configuration](/docs/configuration.html) before it can start loading data.

*To learn more about managing the configuration of your plugins, refer to the [Configuration guide](/docs/configuration.html).*

1. Find out what settings your loader supports using [`meltano config <plugin> list`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin> list

    # For example:
    meltano config target-postgres list
    ```

1. Assuming the previous command listed at least one setting, set appropriate values using [`meltano config <plugin> set`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin> set <setting> <value>

    # For example:
    meltano config target-postgres set user meltano
    meltano config target-postgres set password meltano
    meltano config target-postgres set host localhost
    meltano config target-postgres set port 5432
    meltano config target-postgres set dbname warehouse
    ```

1. Optionally, verify that the configuration looks like what the Singer target expects according to its documentation using [`meltano config <plugin>`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin>

    # For example:
    meltano config target-postgres
    ```

## Run a data integration (EL) pipeline

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [loader](#add-a-loader-to-send-data-to-a-destination) are all set up, we've reached the final chapter of this adventure, and it's time to run your first data integration (EL) pipeline!

*To learn more about data integration, refer to the [Data Integration (EL) guide](/docs/integration.html).*

There's just one step here: run your newly added extractor and loader in a pipeline using [`meltano elt`](/docs/command-line-interface.html#elt):

```bash
meltano elt <extractor> <loader> --job_id=<pipeline name>

# For example:
meltano elt tap-gitlab target-postgres --job_id=gitlab-to-postgres
```

If everything was configured correctly, you should now see your data flow from your source into your destination!

If the command failed, but it's not obvious how to resolve the issue, consider enabling [debug mode](/docs/command-line-interface.html#debugging) to get some more insight into what's going on behind the scenes.
If that doesn't get you closer to a solution, learn how to [get help with your issue](/docs/getting-help.md).

## Next steps

Now that you've successfully run your first data integration (EL) pipeline using Meltano,
you have a few possible next steps:

- [Schedule pipelines to run regularly](#schedule-pipelines-to-run-regularly)
- [Transform loaded data for analysis](#transform-data-for-analysis)
- [Containerize your project](#containerize-your-project)
- [Deploy your pipelines in production](#deploy-your-pipelines-in-production)

### Schedule pipelines to run regularly

Most pipelines aren't run just once, but over and over again, to make sure additions and changes in the source eventually make their way to the destination.

To help you realize this, Meltano supports scheduled pipelines that can be orchestrated using [Apache Airflow](https://apache.airflow.org/).

*To learn more about orchestration, refer to the [Orchestration guide](/docs/orchestration.html).*

1. Schedule a new [`meltano elt`](/docs/command-line-interface.html#elt) pipeline to be invoked on an interval using [`meltano schedule`](/docs/command-line-interface.html#schedule):

    ```bash
    meltano schedule <pipeline name> <extractor> <loader> <interval>

    # For example:
    meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily
    ```

    The `pipeline name` argument corresponds to the `--job_id` flag on `meltano elt`, which identifies related EL(T) runs when storing and looking up [pipeline state](/docs/integration.html#pipeline-state).
    To have scheduled runs pick up where your [earlier manual run](#run-a-data-integration-el-pipeline) left off, ensure you use the same pipeline name.

1. Optionally, verify that the schedule was created successfully using [`meltano schedule list`](/docs/command-line-interface.html#schedule):

    ```bash
    meltano schedule list
    ```

1. Add the [Apache Airflow](https://apache.airflow.org/) orchestrator to your project using [`meltano add`](/docs/command-line-interface.html#add), which will be responsible for managing the schedule and executing the appropriate `meltano elt` commands:

    ```bash
    meltano add orchestrator airflow
    ```

    This will automatically add a
[`meltano elt` DAG generator](https://gitlab.com/meltano/files-airflow/-/blob/master/bundle/orchestrate/dags/meltano.py)
to your project's `orchestrate/dags` directory, where Airflow
will be configured to look for [DAGs](https://airflow.apache.org/docs/stable/concepts.html#dags) by default.

1. Start the [Airflow scheduler](https://airflow.apache.org/docs/stable/cli-ref.html#scheduler) using [`meltano invoke`](/docs/command-line-interface.html#invoke):

    ```bash
    meltano invoke airflow scheduler

    # Add `-D` to run the scheduler in the background:
    meltano invoke airflow scheduler -D
    ```

1. Optionally, verify that a [DAG](https://airflow.apache.org/docs/stable/concepts.html#dags) was automatically created for each scheduled pipeline by starting the [Airflow web interface](https://airflow.apache.org/docs/stable/cli-ref.html#webserver):

    ```bash
    meltano invoke airflow webserver

    # Add `-D` to run the scheduler in the background:
    meltano invoke airflow webserver -D
    ```

    The web interface and DAG overview will be available at <http://localhost:8080>.

### Transform loaded data for analysis

Once your raw data has arrived in your data warehouse, its schema will likely need to be transformed to be more appropriate for analysis.

To help you realize this, Meltano supports transformation using [`dbt`](https://www.getdbt.com/).

To learn about data transformation, refer to the [Data Transformation (T) guide](/docs/transforms.html).

### Containerize your project

To learn how to containerize your project, refer to the [Containerization guide](/docs/containerization.html).

### Deploy your pipelines in production

To learn how to deploy your pipelines in production, refer to the [Deployment in Production guide](/docs/production.html).
