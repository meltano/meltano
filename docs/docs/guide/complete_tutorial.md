---
title: Complete ELT Walkthrough
description: If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: getting_started
sidebar_position: 5
---

Welcome! If you're ready to get started with Meltano and [run an EL[T] pipeline](#run-a-data-integration-el-pipeline)
with a [data source](#add-an-extractor-to-pull-data-from-a-source) and [destination](#add-a-loader-to-send-data-to-a-destination) of your choosing, you've come to the right place!

:::tip

<strong>Short on time, or just curious what the fuss is about?</strong> Watch the <a href="https://www.youtube.com/watch?v=sL3RvXZOTvE">"0 to DataOps" speedrun</a> to get a sense of the Meltano experience in just a few minutes!

:::

## Install Meltano

Before you can get started with Meltano and the [`meltano` command line interface (CLI)](/reference/command-line-interface), you'll need to install it onto your system.

_To learn more about the different installation methods, refer to the [Installation guide](/guide/installation-guide)._

### Local Installation

You will need to be running Linux, macOS, or Windows, and have [Python](https://www.python.org/) 3.8, 3.9, 3.10, 3.11, 3.12 installed. We recommend installing Meltano into a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) inside the directory that will hold your [Meltano projects](/concepts/project).

1.  Create and navigate to a directory to hold your Meltano projects:

    ```bash
    mkdir meltano-projects
    cd meltano-projects
    ```

1.  Install the [pipx](https://pypa.github.io/pipx/) package manager:

    ```bash
    #For Windows (PowerShell): New-Alias Python3 Python
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    #For Windows (PowerShell): Open up a new powershell instance to load your new path variables
    source ~/.bashrc
    ```

:::info

<p>For Windows, instead of source ~/.bashrc, you'll want to open a new PowerShell instance.</p>
:::

1.  Install the [`meltano` package from the Python Package Index (PyPI)](https://pypi.org/project/meltano/):

    ```bash
    pipx install meltano
    ```

    If you have multiple versions of Python installed, you can use a specific one with the `--python` arugment:

    ```bash
    pipx install meltano --python <path to desired Python executable>
    ```

1.  Optionally, verify that the [`meltano` CLI](/reference/command-line-interface) is now available by viewing the version:

    ```bash
    meltano --version
    ```

If anything's not performing as expected, refer to the ["Local Installation" section](/guide/installation-guide#local-installation) of the [Installation guide](/guide/installation-guide) for more details.

## Create Your Meltano Project

Now that you have a way of running the [`meltano` CLI](/reference/command-line-interface),
it's time to create a new [Meltano project](/concepts/project) that (among other things)
will hold the [plugins](/concepts/plugins) that implement the details of your ELT pipelines.

_To learn more about Meltano projects, refer to the [Projects concept doc](/concepts/project)._

1. Navigate to the directory that you'd like to hold your Meltano projects if you haven't already done so:

   ```bash
   mkdir meltano-projects
   cd meltano-projects
   ```

1. Initialize a new project in a directory of your choosing using [`meltano init`](/reference/command-line-interface#init):

   ```bash
   meltano init <project directory path>

   # For example:
   meltano init my-meltano-project

   # If you're using Docker, don't forget to mount the current working directory:
   docker run -v $(pwd):/projects -w /projects meltano/meltano init my-meltano-project
   ```

   This action will create a new directory with, among other things, your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file):

   ```yml
   version: 1
   default_environment: dev
   project_id: <random UUID>
   environments:
   - name: dev
   - name: staging
   - name: prod
   ```

   The `meltano.yml` file does not define any [plugins](/concepts/project#plugins), or [pipeline schedules](/concepts/project#schedules) yet, but does include 3 [environments](/concepts/environments) that you can use if you wish.

   Note that anonymous usage stats are enabled by default; if you want to learn more about how the product benefits from them or how to change the default settings, see the [settings reference](/reference/settings#send-anonymous-usage-stats) page for more details.

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

This will allow you to use [`git diff`](https://git-scm.com/docs/git-diff) to easily check the impact of the [`meltano` commands](/reference/command-line-interface) you'll run below on your project files, most notably your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file).

## View and Activate Your Environments

As part of creating your Meltano project, we automatically added your first [environments](/concepts/environments) called `dev`, `staging` and `prod`. This allows you to define configurations specific to the environment in which you're running your project. There's also a [`default_environment`](https://docs.meltano.com/concepts/environments#default-environments) setting in the `meltano.yml` that get automatically set to `dev`, you can list and change the active environment using:

1. List your available environments:

   ```bash
   meltano environment list
   ```

1. Activate your environment for your shell session:

   ```bash
   export MELTANO_ENVIRONMENT=dev
   ```

   or for Windows PowerShell:

   ```powershell
   $env:MELTANO_ENVIRONMENT="dev"
   ```

   Alternatively you can include the `--environment=dev` argument to each `meltano` command. You should now see a log message that says `Environment 'dev' is active` each time you run a `meltano` command.

1. [optional] Add a new environment:

   ```bash
   meltano environment add <environment name>
   ```

## Add an Extractor to Pull Data from a Source

Now that you have your very own Meltano project, it's time to add some [plugins](/concepts/plugins) to it!

The first plugin you'll want to add is an [extractor](/concepts/plugins#extractors),
which will be responsible for pulling data out of your data source.

_To learn more about adding plugins to your project, refer to the [Plugin Management guide](/guide/plugin-management#adding-a-plugin-to-your-project)._

1.  Find out if an extractor for your data source is [supported out of the box](/concepts/plugins#discoverable-plugins)
    by checking the [Extractors list](https://hub.meltano.com/extractors/):

2.  Depending on the result, pick your next step:

    - If an extractor is **supported out of the box**, add it to your project using [`meltano add`](/reference/command-line-interface#add):

    ```bash
    meltano add extractor <plugin name>

    # For example:
    meltano add extractor tap-gitlab

    # If you have a preference for a non-default variant, select it using `--variant`:
    meltano add extractor tap-gitlab --variant=singer-io

    # If you're using Docker, don't forget to mount the project directory:
    docker run -v $(pwd):/project -w /project meltano/meltano add extractor tap-gitlab
    ```

    This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

    ```yml
    plugins:
      extractors:
      - name: tap-gitlab
        variant: meltanolabs
        pip_url: git+https://github.com/MeltanoLabs/tap-gitlab.git
    ```

    Also note that if you're using Meltano version >=2.0 you will see a `plugins/extractors/tap-gitlab--meltanolabs.lock` file added to your project.
    This pins your settings definitions for stability, they should be checked into your git repository.
    For additional stability you can consider pinning your `pip_url` to a specific release version (e.g. tap-gitlab==1.0.0) or commit hash (e.g. git+https://github.com/MeltanoLabs/tap-gitlab.git@v1.0.0).

    You can now continue to step 4.

    - If an extractor is **not yet discoverable**, find out if a Singer tap for your data source already exists by checking out [MeltanoHub for Singer](https://hub.meltano.com/singer/), which is the best place to find and explore existing Singer taps and targets.

3.  Depending on the result, pick your next step:

            - If a Singer tap for your data source is **available**, add it to your project as a [custom plugin](/concepts/plugins#custom-plugins) using [`meltano add --custom`](/reference/command-line-interface#add):

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

                  This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

                  ```yml
                  plugins:
                    extractors:
                      - name: tap-covid-19
                        namespace: tap_covid_19
                        pip_url: tap-covid-19
                        executable: tap-covid-19
                        capabilities:
                          - catalog
                          - discover
                          - state
                        settings:
                          - name: api_token
                          - name: user_agent
                          - name: start_date
                  ```

                  _To learn more about adding custom plugins, refer to the [Plugin Management guide](/guide/plugin-management#custom-plugins)._

:::info

Once you've got the extractor working in your project, please consider <a href="/contribute/plugins#discoverable-plugins">contributing its description</a> to the <a href="/concepts/plugins#discoverable-plugins">index of discoverable plugins</a> so that it can be supported out of the box for new users!

:::

    - If a Singer tap for your data source **doesn't exist yet**, learn how to build and use your own tap by following the ["Create and Use a Custom Extractor" tutorial](/tutorials/custom-extractor).

    Once you've got your new tap project set up, you can add it to your Meltano project
    as a custom plugin by following the `meltano add --custom` instructions above.
    When asked to provide a `pip install` argument, you can provide a local directory path or Git repository URL.

1.  Optionally, verify that the extractor was installed successfully and that its executable can be invoked using [`meltano invoke`](/reference/command-line-interface#invoke):

    ```bash
    meltano invoke <plugin> --help

    # For example:
    meltano invoke tap-gitlab --help
    ```

    If you see the extractor's help message printed, the plugin was definitely installed successfully,
    but an error message related to missing configuration or an unimplemented `--help` flag
    would also confirm that Meltano can invoke the plugin's executable.

### Configure the Extractor

Chances are that the extractor you just added to your project will require some amount of [configuration](/guide/configuration) before it can start extracting data.

_To learn more about managing the configuration of your plugins, refer to the [Configuration guide](/guide/configuration)._

:::caution

  <p><strong>What if I already have a config file for this extractor?</strong></p>
  <p>If you've used this Singer tap before without Meltano, you may have a <a href="https://hub.meltano.com/singer/spec#config-files">config file</a>.</p>
  <p>If you'd like to use the same configuration with Meltano, you can skip this section and copy and paste the JSON config object into your <a href="/concepts/project#meltano-yml-project-file">`meltano.yml` project file</a> under the <a href="/concepts/project#plugin-configuration">plugin's `config` key</a>:</p>

  ```yaml title="meltano.yml"
    extractors:
    - name: tap-example
      config: {
        "setting": "value",
        "another_setting": true
      }

  <p>Since YAML is a <a href="https://yaml.org/spec/1.2/spec.html#id2759572">superset of JSON</a>, the object should be indented correctly, but formatting does not need to be changed.</p>
:::

1. The simplest way to configure a new plugin in Meltano is using `interactive`:

   ```bash
   meltano config <plugin> set --interactive

   # For example:
   meltano config tap-gitlab set --interactive
   ```

Follow the prompts to step through all available settings, or select an individual setting to configure.

You can also optionally use the `list`, `set` and `unset` commands directly to view and change plugin configuration:

- Find out what settings your extractor supports using [`meltano config <plugin> list`](/reference/command-line-interface#config):

  ```bash
  meltano config <plugin> list

  # For example:
  meltano config tap-gitlab list
  ```

- Assuming the previous command listed at least one setting, set appropriate values using [`meltano config <plugin> set`](/reference/command-line-interface#config):

:::info

<strong>See <a href="https://hub.meltano.com/extractors/gitlab#private-token">MeltanoHub for details</a> on how to get a GitLab `private_token` for tap-gitlab.</strong>

:::

```bash
meltano config <plugin> set <setting> <value>

# For example:
meltano config tap-gitlab set projects "meltano/meltano meltano/tap-gitlab"
meltano config tap-gitlab set start_date 2024-03-01T00:00:00Z
meltano config tap-gitlab set private_token my_private_token
```

This will add the non-sensitive configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

```yml
environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-gitlab
            config:
              projects: meltano/meltano meltano/tap-gitlab
              start_date: "2024-10-01T00:00:00Z"
```

Sensitive configuration (like `private_token`) will instead be stored in your project's [`.env` file](/concepts/project#env) so that it will not be checked into version control:

```bash
export TAP_GITLAB_PRIVATE_TOKEN=my_private_token
```

1. Optionally, verify that the configuration looks like what the Singer tap expects according to its documentation using [`meltano config <plugin>`](/reference/command-line-interface#config):

   ```bash
   meltano config <plugin>

   # For example:
   meltano config tap-gitlab
   ```

   This will show the current configuration:

   ```json
   {
     "api_url": "https://gitlab.com",
     "private_token": "my_private_token",
     "groups": "",
     "projects": "meltano/meltano meltano/tap-gitlab",
     "ultimate_license": false,
     "fetch_merge_request_commits": false,
     "fetch_pipelines_extended": false,
     "start_date": "2024-03-01T00:00:00Z"
   }
   ```

### Select Entities and Attributes to Extract

Now that the extractor has been configured, it'll know where and how to find your data, but won't yet know which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes, but it's recommended that you [specify the specific entities and attributes you'd like to extract](/guide/integration#selecting-entities-and-attributes-for-extraction) to improve performance and save on bandwidth and storage.

_To learn more about selecting entities and attributes for extraction, refer to the [Data Integration (EL) guide](/guide/integration#selecting-entities-and-attributes-for-extraction)._

:::info

  <p><strong>What if I already have a catalog file for this extractor?</strong></p>
  <p>If you've used this Singer tap before without Meltano, you may have already generated a <a href="https://hub.meltano.com/singer/spec#catalog-files">catalog file</a>.</p>
  <p>If you'd like for Meltano to use it instead of <a href="/guide/integration#extractor-catalog-generation">generating a catalog</a> based on the entity selection rules you'll be asked to specify below, you can skip this section and either set the <a href="/concepts/plugins#catalog-extra">`catalog` extractor extra</a> or use <a href="/reference/command-line-interface#elt">`meltano elt`</a>'s`--catalog` option when <a href="#run-a-data-integration-el-pipeline">running the data integration (EL) pipeline</a> later on in this guide.</p>
:::

1. Find out whether the extractor supports entity selection, and if so, what entities and attributes are available, using [`meltano select --list --all`](/reference/command-line-interface#select):

   ```bash
   meltano select <plugin> --list --all

   # For example:
   meltano select tap-gitlab --list --all
   ```

   If this command fails with an error message, it usually means that the Singer tap does not support [catalog discovery mode](https://hub.meltano.com/singer/spec#discovery-mode) and will always extract all supported entities and attributes.

1. Assuming the previous command succeeded, select the desired entities and attributes for extraction using [`meltano select`](/reference/command-line-interface#select):

   ```bash
   meltano select <plugin> <entity> <attribute>
   meltano select <plugin> --exclude <entity> <attribute>

   # For example:
   meltano select tap-gitlab commits id
   meltano select tap-gitlab commits project_id
   meltano select tap-gitlab commits created_at
   meltano select tap-gitlab commits author_name
   meltano select tap-gitlab commits message

   # Include all attributes of an entity
   meltano select tap-gitlab tags "*"

   # Exclude matching attributes of all entities
   meltano select tap-gitlab --exclude "*" "*_url"
   ```

   As you can see in the example, entity and attribute identifiers can contain wildcards (`*`) to match multiple entities or attributes at once.

   This will add the [selection rules](/concepts/plugins#select-extra) to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

   ```yml
   plugins:
     extractors:
       - name: tap-gitlab
         variant: meltanolabs
         pip_url: git+https://github.com/MeltanoLabs/tap-gitlab.git
   environments:
     - name: dev
       config:
         plugins:
           extractors:
             - name: tap-gitlab
               config:
                 projects: meltano/meltano meltano/tap-gitlab
                 start_date: "2024-03-01T00:00:00Z"
               select:
                 - commits.id
                 - commits.project_id
                 - commits.created_at
                 - commits.author_name
                 - commits.message
                 - tags.*
                 - "!*.*_url"
   ```

   Note that exclusion takes precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern. This information is also detailed in the CLI documentation for the [`--exclude` parameter](/reference/command-line-interface#exclude-parameter).

1. Optionally, verify that only the intended entities and attributes are now selected using [`meltano select --list`](/reference/command-line-interface#select):

   ```bash
   meltano select <plugin> --list

   # For example:
   meltano select tap-gitlab --list
   ```

### Choose How to Replicate Each Entity

If the data source you'll be pulling data from is a database, such as [PostgreSQL](https://hub.meltano.com/extractors/postgres.html) or [MongoDB](https://hub.meltano.com/extractors/mongodb.html), your extractor will likely require one final setup step: setting a [replication method](/guide/integration#replication-methods) for each [selected entity (table)](#select-entities-and-attributes-to-extract).

:::info

  <p>
    Extractors for Software as a Service (SaaS) APIs typically hard-code the appropriate replication method for each supported entity, so if you're using one, you can skip this section and <a href="#add-a-loader-to-send-data-to-a-destination">move on to setting up a loader</a>.
  </p>
:::

Most database extractors, on the other hand, support two or more of the following replication methods and require you to choose an appropriate option for each table through the `replication-method` [stream metadata](/guide/integration#setting-metadata) key:

- `LOG_BASED`: [Log-based Incremental Replication](/guide/integration#log-based-incremental-replication)

  The extractor uses the database's binary log files to identify what records were inserted, updated, and deleted from the table since the last run (if any), and extracts only these records.

  This option is not supported by all databases and database extractors.

- `INCREMENTAL`: [Key-based Incremental Replication](/guide/integration#key-based-incremental-replication)

  The extractor uses the value of a specific column on the table (the [Replication Key](/guide/integration#replication-key), such as an `updated_at` timestamp or incrementing `id` integer) to identify what records were inserted or updated (but not deleted) since the last run (if any), and extracts only those records.

- `FULL_TABLE`: [Full Table Replication](/guide/integration#full-table-replication)

  The extractor extracts all available records in the table on every run.

  _To learn more about replication methods, refer to the [Data Integration (EL) guide](/guide/integration#replication-methods)._

  1. Find out which replication methods (i.e. options for the `replication-method` [stream metadata](https://hub.meltano.com/singer/spec#metadata) key) the extractor supports by checking its documentation or the README in its repository.

  1. Set the desired `replication-method` metadata for each [selected entity](#select-entities-and-attributes-to-extract) using [`meltano config <plugin> set`](/reference/command-line-interface#config) and the extractor's [`metadata` extra](/concepts/plugins#metadata-extra):

     ```bash
     meltano config <plugin> set _metadata <entity> replication-method <LOG_BASED|INCREMENTAL|FULL_TABLE>

     # For example:
     meltano config tap-postgres set _metadata some_entity_id replication-method INCREMENTAL
     meltano config tap-postgres set _metadata other_entity replication-method FULL_TABLE

     # Set replication-method metadata for all entities
     meltano config tap-postgres set _metadata '*' replication-method INCREMENTAL

     # Set replication-method metadata for matching entities
     meltano config tap-postgres set _metadata '*_full' replication-method FULL_TABLE
     ```

     As you can see in the example, entity identifiers can contain wildcards (`*`) to match multiple entities at once.

     If you've set a table's `replication-method` to `INCREMENTAL`, also choose a [Replication Key](/guide/integration#replication-key) by setting the `replication-key` metadata:

     ```bash
     meltano config <plugin> set _metadata <entity> replication-key <column>

     # For example:
     meltano config tap-postgres set _metadata some_entity_id replication-key updated_at
     meltano config tap-postgres set _metadata some_entity_id replication-key id
     ```

     This will add the [metadata rules](/concepts/plugins#metadata-extra) to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

     ```yml
     environments:
       - name: dev
         config:
           plugins:
             extractors:
               - name: tap-postgres
                 metadata:
                   some_entity_id:
                     replication-method: INCREMENTAL
                     replication-key: id
                   other_entity:
                     replication-method: FULL_TABLE
                   "*":
                     replication-method: INCREMENTAL
                   "*_full":
                     replication-method: FULL_TABLE
     ```

  1. Optionally, verify that the [stream metadata](https://hub.meltano.com/singer/spec#metadata) for each table was set correctly in the extractor's [generated catalog file](/guide/integration#extractor-catalog-generation) by dumping it using [`meltano invoke --dump=catalog <plugin>`](/reference/command-line-interface#select):

     ```bash
     meltano invoke --dump=catalog <plugin>

     # For example:
     meltano invoke --dump=catalog tap-postgres
     ```

## Add a Loader to Send Data to a Destination

Now that your Meltano project has everything it needs to pull data from your source,
it's time to tell it where that data should go!

This is where the [loader](/concepts/plugins#loaders) comes in,
which will be responsible for loading [extracted](#add-an-extractor-to-pull-data-from-a-source) data into an arbitrary data destination.

_To learn more about adding plugins to your project, refer to the [Plugin Management guide](/guide/plugin-management#adding-a-plugin-to-your-project)._

1.  Find out if a loader for your data destination is [supported out of the box](/concepts/plugins#discoverable-plugins)
    by checking the [Loaders list](https://hub.meltano.com/loaders/):

2.  Depending on the result, pick your next step:

            - If a loader is **supported out of the box**, add it to your project using [`meltano add`](/reference/command-line-interface#add):

                  ```bash
                  meltano add loader <plugin name>

                  # For this example, we'll use the default variant:
                  meltano add loader target-postgres

                  # Or if you just want to use a non-default variant you can use this,
                  # selected using `--variant`:
                  meltano add loader target-postgres --variant=datamill-co
                  ```

:::info

<p>Sometimes extractors and loaders expect that certain dependencies are already installed. If you run into any issues while installing, refer to <a href="https://hub.meltano.com/">MeltanoHub</a> for more help troubleshooting or join the <a href="https://meltano.com/slack">Meltano Slack workspace</a> to ask questions.</p>

:::

                  This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

                  ```yml
                  plugins:
                  loaders:
                    - name: target-postgres
                      variant: transferwise
                      pip_url: pipelinewise-target-postgres
                  ```

                  You can now continue to step 4.

            - If a loader is **not yet discoverable**, find out if a Singer target for your data source already exists by checking [Singer's index of targets](https://www.singer.io/#targets) and/or doing a web search for `Singer target <data destination>`, for example, `Singer target BigQuery`.

1.  Depending on the result, pick your next step:

        - If a Singer target for your data destination is **available**, add it to your project as a [custom plugin](/concepts/plugins#custom-plugins) using [`meltano add --custom`](/reference/command-line-interface#add):

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

              This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

              ```yml
              plugins:
                loaders:
                  - name: target-bigquery
                    namespace: target_bigquery
                    pip_url: target-bigquery
                    executable: target-bigquery
                    settings:
                      - name: project_id
                      - name: dataset_id
                      - name: table_id
              ```

              _To learn more about adding custom plugins, refer to the [Plugin Management guide](/guide/plugin-management#custom-plugins)._

:::info

            <p>Once you've got the loader working in your project, please consider <a href="/contribute/plugins#discoverable-plugins">contributing its description</a> to the <a href="/concepts/plugins#discoverable-plugins">index of discoverable plugins</a> so that it can be supported out of the box for new users!</p>

:::

        - If a Singer target for your data source **doesn't yet exist**, learn how to build your own target by following [Singer's "Developing a Target" guide](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#developing-a-target).

        Once you've got your new target project set up, you can add it to your Meltano project
        as a custom plugin by following the `meltano add --custom` instructions above.
        When asked to provide a `pip install` argument, you can provide a local directory path or Git repository URL.

1.  Optionally, verify that the loader was installed successfully and that its executable can be invoked using [`meltano invoke`](/reference/command-line-interface#invoke):

    ```bash
    meltano invoke <plugin> --help

    # For example:
    meltano invoke target-postgres --help
    ```

    If you see the loader's help message printed, the plugin was definitely installed successfully,
    but an error message related to missing configuration or an unimplemented `--help` flag
    would also confirm that Meltano can invoke the plugin's executable.

### Configure the Loader

Chances are that the loader you just added to your project will require some [configuration](/guide/configuration) before it can start loading data.

_To learn more about managing the configuration of your plugins, refer to the [Configuration guide](/guide/configuration)._

:::caution

  <p><strong>What if I already have a config file for this loader?</strong></p>
  <p>If you've used this Singer target before without Meltano, you may already have a <a href="https://hub.meltano.com/singer/spec#config-files">config file</a>.</p>
  <p>If you'd like to use the same configuration with Meltano, you can skip this section and copy and paste the JSON config object into your <a href="/concepts/project#meltano-yml-project-file"><code>meltano.yml</code> project file</a> under the <a href="/concepts/project#plugin-configuration">plugin's <code>config</code> key</a>:</p>

  ```yaml title="meltano.yml"
    loaders:
    - name: target-example
      config: {
        "setting": "value",
        "another_setting": true
      }
  ```

  <p>Since YAML is a <a href="https://yaml.org/spec/1.2/spec.html#id2759572">superset of JSON</a>, the object should be indented correctly, but formatting does not need to be changed.</p>
:::

1. The simplest way to configure a new plugin in Meltano is using `interactive`:

   ```bash
   meltano config <plugin> set --interactive

   # For example:
   meltano config target-postgres set --interactive
   ```

Follow the prompts to step through all available settings, or select an individual setting to configure.

You can also optionally use the `list`, `set` and `unset` commands directly to view and change plugin configuration:

- Find out what settings your loader supports using [`meltano config <plugin> list`](/reference/command-line-interface#config):

  ```bash
  meltano config <plugin> list

  # For example:
  meltano config target-postgres list
  ```

- Assuming the previous command listed at least one setting, set appropriate values using [`meltano config <plugin> set`](/reference/command-line-interface#config):

  ```bash
  meltano config <plugin> set <setting> <value>

  # For example:
  meltano config target-postgres set user meltano
  meltano config target-postgres set password meltano
  meltano config target-postgres set dbname warehouse
  meltano config target-postgres set default_target_schema public
  ```

:::info

  <p>You can turn on a local postgres docker instance with these configs using <code>docker run --name postgres -e POSTGRES_PASSWORD=meltano -e POSTGRES_USER=meltano -e POSTGRES_DB=warehouse -d -p 5432:5432 postgres</code>.</p>

:::

This will add the non-sensitive configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

```yml
plugins:
  loaders:
    - name: target-postgres
      variant: transferwise
      pip_url: pipelinewise-target-postgres
      config:
        user: meltano
        dbname: warehouse
        default_target_schema: public
```

Sensitive configuration information (such as `password`) will instead be stored in your project's [`.env` file](/concepts/project#env) so that it will not be checked into version control:

```bash
export TARGET_POSTGRES_PASSWORD=meltano
```

1. Optionally, verify that the configuration looks like what the Singer target expects according to its documentation using [`meltano config <plugin>`](/reference/command-line-interface#config):

   ```bash
   meltano config <plugin>

   # For example:
   meltano config target-postgres
   ```

   This will show the current configuration:

   ```json
   {
     "host": "localhost",
     "port": 5432,
     "user": "meltano",
     "password": "meltano",
     "dbname": "warehouse",
     "ssl": "false",
     "default_target_schema": "public",
     "batch_size_rows": 100000,
     "flush_all_streams": false,
     "parallelism": 0,
     "parallelism_max": 16,
     "add_metadata_columns": false,
     "hard_delete": false,
     "data_flattening_max_level": 0,
     "primary_key_required": true,
     "validate_records": false
   }
   ```

## Run a Data Integration (EL) Pipeline

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [loader](#add-a-loader-to-send-data-to-a-destination) are all set up, we've reached the final chapter of this adventure, and it's time to run your first data integration (EL) pipeline!

_To learn more about data integration, refer to the [Data Integration (EL) guide](/guide/integration)._

There's just one step here: run your newly added extractor and loader in a pipeline using [`meltano run`](/reference/command-line-interface#run):

```bash
meltano run <extractor> <loader>

# For example:
meltano run tap-gitlab target-postgres
```

If everything was configured correctly, you should now see your data flow from your source into your destination! Check your postgres instance for the tables `warehouse.schema.commits` and `warehouse.schema.tags`.

If the command failed, but it's not obvious how to resolve the issue, consider enabling [debug mode](/reference/command-line-interface#debugging) to get some more insight into what's going on behind the scenes.
If that doesn't get you closer to a solution, [feel free to ask for assistance from our friendly Slack community](https://meltano.com/slack).

If you run `meltano run` at another time, it will automatically pick up where the previous run left off, assuming the extractor supports [incremental replication](/guide/integration#incremental-replication-state) and you have an active environment.
Behind the scenes Meltano is tracking state using a State ID that's auto-generated based on the extractor name, loader name, and active environment name.
To override the state and extract all data from the beginning again you can use the `--full-refresh` argument.

:::info

  <p><strong>What if I already have a state file for this extractor?</strong></p>
  <p>If you've used this Singer tap before without Meltano, you may already have a <a href="https://hub.meltano.com/singer/spec#state-files">state file</a>.</p>
  <p>If you'd like Meltano to use it instead of <a href="/guide/integration#incremental-replication-state">looking up state based on the State ID</a>, you can either use <a href="/reference/command-line-interface#state"><code>meltano state</code></a> to view and edit the state directly or set the <a href="/concepts/plugins#state-extra"><code>state</code> extractor extra</a>.</p>
  <p>If you'd like to view the state generated by the most recent run, you can use <a href="/reference/command-line-interface#get"><code>meltano state get</code></a></p>

<pre>
# Example
meltano state get dev:tap-gitlab-to-target-postgres
</pre>

:::

There is also the [`meltano elt`](/reference/command-line-interface#elt) command which is a more rigid command for running only EL pipelines.

Or directly using the `meltano invoke`, which only executes a single plugin at a time.
This can be useful for debugging a failing extractor or loader.

## Next Steps

Now that you've successfully run your first data integration (EL) pipeline using Meltano,
you have a few possible next steps:

- [Schedule Pipelines to Run Regularly](#schedule-pipelines-to-run-regularly)
- [Transform Loaded Data for Analysis](#transform-loaded-data-for-analysis)
- [Analyze Your Data with Superset](#analyze-your-data-with-superset)
- [Containerize Your Project](#containerize-your-project)
- [Deploy Your Pipelines in Production](#deploy-your-pipelines-in-production)

### Schedule Pipelines to Run Regularly

Most pipelines aren't run just once, but over and over again, to make sure additions and changes in the source eventually make their way to the destination.

To help you achieve this, Meltano supports scheduled pipelines that can be orchestrated using [Apache Airflow](https://airflow.apache.org/).

_To learn more about orchestration, refer to the [Orchestration guide](/guide/orchestration)._

1. Schedule a new pipeline to be invoked on an interval using [`meltano schedule`](/reference/command-line-interface#schedule):

```bash
meltano schedule add <pipeline name> --extractor <extractor> --loader <loader> --interval <interval>

# For example:
meltano schedule add gitlab-to-postgres --extractor tap-gitlab --loader target-postgres --interval @daily
```

The `pipeline name` argument corresponds to the `--state-id` option on `meltano el`, which identifies related EL runs when storing and looking up [incremental replication state](/guide/integration#incremental-replication-state).

To have scheduled runs pick up where your [earlier manual run](#run-a-data-integration-el-pipeline) left off, ensure you use the same pipeline name.

This will add the new schedule to your [`meltano.yml` project file](/concepts/project#schedules):

```yml
schedules:
  - name: gitlab-to-postgres
    extractor: tap-gitlab
    loader: target-postgres
    transform: skip
    interval: "@daily"
```

:::info

  <p>The <code>name</code> setting in schedules acts as the <code>state_id</code> so that state is preserved across scheduled executions. This should generally be a globally unique string based on the job being run (i.e. <code>gitlab-to-postgres</code> or <code>gitlab-to-postgres-prod</code> if you have multiple environemnts).</p>
:::

1. Optionally, verify that the schedule was created successfully using [`meltano schedule list`](/reference/command-line-interface#schedule):

   ```bash
   meltano schedule list
   ```

1. Add the [Apache Airflow](https://airflow.apache.org/) utility to your project using [`meltano add`](/reference/command-line-interface#add), which will be responsible for managing the schedule and executing the appropriate `meltano run` commands:

   ```bash
   meltano add utility airflow
   ```

   This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

   ```yml
   plugins:
     utilities:
       - name: airflow
         pip_url: git+https://github.com/meltano/airflow-ext.git@main apache-airflow==2.8.1 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-no-providers-${MELTANO__PYTHON_VERSION}.txt
   ```

   It will also automatically add a
   [`meltano run` DAG generator](https://github.com/meltano/files-airflow/blob/main/bundle/orchestrate/dags/meltano.py)
   to your project's `orchestrate/dags` directory, where Airflow
   will be configured to look for [DAGs](https://airflow.apache.org/docs/apache-airflow/1.10.14/concepts.html#dags) by default.

1. Start the [Airflow scheduler](https://airflow.apache.org/docs/apache-airflow/1.10.14/scheduler.html) using [`meltano invoke`](/reference/command-line-interface#invoke):

   ```bash
   meltano invoke airflow scheduler

   # Add `-D` to run the scheduler in the background:
   meltano invoke airflow scheduler -D
   ```

   As long as the scheduler is running, your scheduled pipelines will run at the appropriate times.

1. Optionally, verify that a [DAG](https://airflow.apache.org/docs/apache-airflow/1.10.14/concepts.html#dags) was automatically created for each scheduled pipeline by starting the [Airflow web interface](https://airflow.apache.org/docs/apache-airflow/1.10.14/cli-ref.html#webserver):

   ```bash
   meltano invoke airflow webserver

   # Add `-D` to run the scheduler in the background:
   meltano invoke airflow webserver -D
   ```

1. Create an Admin user called `melty` for logging in.

   ```bash
   meltano invoke airflow users create --username melty \
   --firstname melty \
   --lastname meltano \
   --role Admin \
   --password melty \
   --email melty@meltano.com
   ```

   The web interface and DAG overview will be available at http://localhost:8080.

### Transform Loaded Data for Analysis

Once your raw data has arrived in your data warehouse, its schema will likely need to be transformed to be more appropriate for analysis.

To help you achieve this, Meltano supports transformation using [`dbt`](https://www.getdbt.com/).
If you already have an existing dbt project that you'd like to migrate to Meltano, check out the [existing dbt project guide](https://docs.meltano.com/guide/existing-dbt-project) for more details.

To learn about data transformation, refer to the [Data Transformation (T) guide](/guide/transformation).
`dbt` plugins are adapter specific so you should install the plugin that matches your warehouse (i.e. Postgres = `dbt-postgres`, Snowflow = `dbt-snowflake`, etc.).
Refer to the [transformers page](https://hub.meltano.com/transformers/) on MeltanoHub to see all available plugins.

1. Install the dbt transformer to your project:

   ```bash
   meltano add transformer dbt-postgres
   ```

1. Configure dbt-postgres

   ```bash
   meltano config dbt-postgres list

   # For example:
   meltano config dbt-postgres set host localhost
   meltano config dbt-postgres set user meltano
   meltano config dbt-postgres set password meltano
   meltano config dbt-postgres set port 5432
   meltano config dbt-postgres set dbname warehouse
   meltano config dbt-postgres set schema analytics
   ```

1. Once dbt has been installed and configured in your Meltano project, you will see the `/transform` directory populated with dbt artifacts.

   These artifacts are installed via the [dbt file bundle](https://gitlab.com/meltano/files-dbt-postgres/).
   For more about file bundles, refer to the [Plugin File bundles](/concepts/plugins#file-bundles).

   Now all you need to do is start writing your dbt models in the `/transform/models` directory.
   This usually consists of a `source.yml` file defining the source tables you will be referencing inside your dbt models.

   For example, the `/transform/models/tap_gitlab/source.yml` below configures dbt sources from the postgres tables where our tap-gitlab EL job output to.

   Create and navigate to the `/transform/models/tap_gitlab` directory to hold your dbt models:

   ```bash
   mkdir ./transform/models/tap_gitlab
   touch  ./transform/models/tap_gitlab/source.yml
   ```

   Add the following content to your new `source.yml` file:

   ```yaml
   config-version: 2
   version: 2
   sources:
     - name: tap_gitlab
       schema: public
       tables:
         - name: commits
         - name: tags
   ```

   The organization of your dbt project is up to you, but the Meltano convention is to name the model directory after the extractor using snake_case (i.e. tap_gitlab).

   See more in the [Data Transformation (T) guide - transform in your ELT pipeline](/guide/transformation#transform-in-your-elt-pipeline).

1. Then add a model file with your SQL transformation logic.
   For example the dbt model SQL below generates a table with new commits in the last 7 days `/transform/models/tap_gitlab/commits_last_7d.sql`.

   Create your model file:

   ```bash
   touch  ./transform/models/tap_gitlab/commits_last_7d.sql
   ```

   Add the following content to your new `commits_last_7d.sql` file:

   ```sql
   {% raw %}
   {{
     config(
       materialized='table'
     )
   }}

   select *
   from {{ source('tap_gitlab', 'commits') }}
   where created_at::date >= current_date - interval '7 days'
   {% endraw %}
   ```

1. Run your dbt models either using [`meltano run`](/reference/command-line-interface#run) or [`meltano invoke`](/reference/command-line-interface#invoke):

   ```bash
   meltano invoke dbt-postgres:<command>

   # For example:
   meltano invoke dbt-postgres:run
   ```

   The [`meltano run`](/reference/command-line-interface#run) command allows you to execute dbt in the same way as `invoke` but in a much more flexible fashion. This allows for inline dbt execution and more advanced reverse ETL use cases:

   ```bash
   meltano run <extractor> <loader> <other_plugins>

   # For example:
   meltano run tap-gitlab target-postgres dbt-postgres:test dbt-postgres:run tap-postgres target-gsheet
   ```

   After your transform run is complete, you should see a new table named after your model `warehouse.analytics.commits_last_7d` in your target.

   See the [transformer docs](https://hub.meltano.com/transformers/dbt#commands) from other supported dbt commands like `dbt-postgres:test`, `dbt-postgres:seed`, `dbt-postgres:snapshot` and selection criteria like `dbt-postgres:run --models tap_gitlab.*`.

### Analyze Your Data with Superset

To learn how to install and use [Superset](https://superset.apache.org/) in your project, refer to the [Analyze data](/guide/analysis) docs.

### Containerize Your Project

To learn how to containerize your project, refer to the [Containerization guide](/guide/containerization).

### Deploy Your Pipelines in Production

To learn how to deploy your pipelines in production, refer to the [Deployment in Production guide](/guide/production).
