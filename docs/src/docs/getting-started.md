---
description: If you're ready to get started with Meltano and run an EL(T) pipeline with a data source and destination of your choosing, you've come to the right place!
---

# Getting Started

Welcome! If you're ready to get started with Meltano and [run an EL(T) pipeline](#run-a-data-integration-el-pipeline)
with a [data source](#add-an-extractor-to-pull-data-from-a-source) and [destination](#add-a-loader-to-send-data-to-a-destination) of your choosing, you've come to the right place!

::: tip Short on time, or just curious what the fuss is about?

To get a sense of the Meltano experience in just a few minutes, follow the [examples on the homepage](/),
or watch the ["from 0 to ELT in 90 seconds" speedrun](https://meltano.com/blog/2021/04/28/speedrun-from-0-to-elt-in-90-seconds/).

They can be copy-pasted right into your terminal and will take you all the way through
[installation](/#installation), [data integration (EL)](/#integration), [data transformation (T)](/#transformation), [orchestration](/#orchestration), and [containerization](/#containerization)
with the [`tap-gitlab` extractor](https://hub.meltano.com/extractors/gitlab.html)
and the [`target-jsonl`](https://hub.meltano.com/loaders/jsonl.html) and [`target-postgres`](https://hub.meltano.com/loaders/postgres.html) loaders.

:::

## Install Meltano

Before you can get started with Meltano and the [`meltano` CLI](/docs/command-line-interface.html), you'll need to install it onto your system.

*To learn more about the different installation methods, refer to the [Installation guide](/docs/installation.html).*

### Local installation

If you're running Linux or macOS and have [Python](https://www.python.org/) 3.6, 3.7 or 3.8 installed,
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

    By default, this image comes with the oldest version of Python supported by Meltano, currently 3.6.
    If you'd like to use Python 3.7 or 3.8 instead, add a `-python<X.Y>` suffix to the image tag, e.g. `latest-python3.8`.

1. Optionally, verify that the [`meltano` CLI](/docs/command-line-interface.html) is now available through the Docker image by viewing the version:

    ```bash
    docker run meltano/meltano --version
    ```

Now, whenever this guide or the documentation asks you to run the `meltano` command, you'll need to run it using `docker run meltano/meltano <args>` as in the example above.

When running a `meltano` subcommand that requires access to your project (which you'll create in the next step), you'll also need to mount the project directory into the container and set it as the container's working directory:

```bash
docker run -v $(pwd):/project -w /project meltano/meltano <args>
```

If anything's not behaving as expected, refer to the ["Installing on Docker" section](/docs/installation.html#installing-on-docker) of the [Installation guide](/docs/installation.html) for more details.

## Create your Meltano project

Now that you have a way of running the [`meltano` CLI](/docs/command-line-interface.html),
it's time to create a new [Meltano project](/docs/project.html) that (among other things)
will hold the [plugins](/docs/plugins.html) that implement the various details of your ELT pipelines.

*To learn more about Meltano projects, refer to the [Projects concept doc](/docs/project.html).*

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

    This will create a new directory with, among other things, your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

    ```yml
    version: 1
    send_anonymous_usage_stats: true
    project_id: <random UUID>
    ```

    It doesn't define any [plugins](/docs/project.html#plugins) or [pipeline schedules](/docs/project.html#schedules) yet,
    but note that the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats) is enabled by default.
    To disable it, change the value to `false` and optionally remove the [`project_id` setting](/docs/settings.html#project-id).

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
    you'll run below on your project files, most notably your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

## Add an extractor to pull data from a source

Now that you have your very own Meltano project, it's time to add some [plugins](/docs/plugins.html) to it!

The first plugin you'll want to add is an [extractor](/docs/plugins.html#extractors),
which will be responsible for pulling data out of your data source.

*To learn more about adding plugins to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-a-plugin-to-your-project).*

1. Find out if an extractor for your data source is [supported out of the box](/docs/plugins.html#discoverable-plugins)
by checking the [Extractors list](https://hub.meltano.com/extractors/) or using [`meltano discover`](/docs/command-line-interface.html#discover):

    ```bash
    meltano discover extractors
    ```

1. Depending on the result, pick your next step:

    - If an extractor is **supported out of the box**, add it to your project using [`meltano add`](/docs/command-line-interface.html#add):

      ```bash
      meltano add extractor <plugin name>

      # For example:
      meltano add extractor tap-gitlab

      # If you have a preference for a non-default variant, select it using `--variant`:
      meltano add extractor tap-gitlab --variant=singer-io

      # If you're using Docker, don't forget to mount the project directory:
      docker run -v $(pwd):/project -w /project meltano/meltano add extractor tap-gitlab
      ```

      This will add the new plugin to your [`meltano.yml` project file](/docs/project.html#plugins):

      ```yml{3-5}
      plugins:
        extractors:
        - name: tap-gitlab
          variant: meltano
          pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
      ```

      You can now continue to step 4.

    - If an extractor is **not yet discoverable**, find out if a Singer tap for your data source already exists by checking [Singer's index of taps](https://www.singer.io/#taps) and/or doing a web search for `Singer tap <data source>`, e.g. `Singer tap COVID-19`.

1. Depending on the result, pick your next step:

    - If a Singer tap for your data source is **available**, add it to your project as a [custom plugin](/docs/plugins.html#custom-plugins) using [`meltano add --custom`](/docs/command-line-interface.html#add):

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

        This will add the new plugin to your [`meltano.yml` project file](/docs/project.html#plugins):

        ```yml{3-14}
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

        *To learn more about adding custom plugins, refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).*

        ::: tip
        Once you've got the extractor working in your project, please consider
        [contributing its description](/docs/contributor-guide.html#discoverable-plugins)
        to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
        so that it can be supported out of the box for new users!
        :::

    - If a Singer tap for your data source **doesn't exist yet**, learn how to build and use your own tap by following the ["Create and Use a Custom Extractor" tutorial](/tutorials/create-a-custom-extractor.html).

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

::: details What if I already have a config file for this extractor?

If you've used this Singer tap before without Meltano, you may have a [config file](/docs/singer-spec.html#config-files) already.

If you'd like to use the same configuration with Meltano, you can skip this section and copy and paste the JSON config object into your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) under the [plugin's `config` key](/docs/project.html#plugin-configuration):

```yaml{3-6}
extractors:
- name: tap-example
  config: {
    "setting": "value",
    "another_setting": true
  }
```

Since YAML is a [superset of JSON](https://yaml.org/spec/1.2/spec.html#id2759572), the object should be indented correctly, but formatting does not need to be changed.

:::

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
    meltano config tap-gitlab set projects "meltano/meltano meltano/tap-gitlab"
    meltano config tap-gitlab set start_date 2020-05-01T00:00:00Z
    meltano config tap-gitlab set private_token my_private_token
    ```

    This will add the non-sensitive configuration to your [`meltano.yml` project file](/docs/project.html#plugin-configuration):

    ```yml{5-7}
    plugins:
      extractors:
      - name: tap-gitlab
        variant: meltano
        config:
          projects: meltano/meltano meltano/tap-gitlab
          start_date: '2020-10-01T00:00:00Z'
    ```

    Sensitive configuration (like `private_token`) will instead be stored in your project's [`.env` file](/docs/project.html#env) so that it will not be checked into version control:

    ```bash
    export TAP_GITLAB_PRIVATE_TOKEN=my_private_token
    ```

1. Optionally, verify that the configuration looks like what the Singer tap expects according to its documentation using [`meltano config <plugin>`](/docs/command-line-interface.html#config):

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
      "start_date": "2020-10-01T00:00:00Z"
    }
    ```

### Select entities and attributes to extract

Now that the extractor has been configured, it'll know where and how to find your data,
but not yet which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes,
but it's recommended that you [specify the specific entities and attributes you'd like to extract](/docs/integration.html#selecting-entities-and-attributes-for-extraction),
to improve performance and save on bandwidth and storage.

*To learn more about selecting entities and attributes for extraction, refer to the [Data Integration (EL) guide](/docs/integration.html#selecting-entities-and-attributes-for-extraction).*

::: details What if I already have a catalog file for this extractor?

If you've used this Singer tap before without Meltano, you may have generated a [catalog file](/docs/singer-spec.html#catalog-files) already.

If you'd like Meltano to use it instead of [generating a catalog](/docs/integration.html#extractor-catalog-generation) based on the entity selection rules you'll be asked to specify below, you can skip this section and either set the [`catalog` extractor extra](/docs/plugins.html#catalog-extra) or use [`meltano elt`](/docs/command-line-interface.html#elt)'s `--catalog` option when [running the data integration (EL) pipeline](#run-a-data-integration-el-pipeline) later on in this guide.

:::

1. Find out whether the extractor supports entity selection, and if so, what entities and attributes are available, using [`meltano select --list --all`](/docs/command-line-interface.html#select):

    ```bash
    meltano select <plugin> --list --all

    # For example:
    meltano select tap-gitlab --list --all
    ```

    If this command fails with an error, this usually means that the Singer tap does not support [catalog discovery mode](/docs/singer-spec.html#discovery-mode), and will always extract all supported entities and attributes.

1. Assuming the previous command succeeded, select the desired entities and attributes for extraction using [`meltano select`](/docs/command-line-interface.html#select):

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

    This will add the [selection rules](/docs/plugins.html#select-extra) to your [`meltano.yml` project file](/docs/project.html#plugin-configuration):

    ```yml{4-10}
    plugins:
      extractors:
      - name: tap-gitlab
        select:
        - tags.*
        - commits.id
        - commits.project_id
        - commits.created_at
        - commits.author_name
        - commits.message
        - '!*.*_url'
    ```

    Note that exclusion takes precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern first. This is also detailed in the CLI documentation for the [`--exclude` parameter](/docs/command-line-interface.html#exclude-parameter).

1. Optionally, verify that only the intended entities and attributes are now selected using [`meltano select --list`](/docs/command-line-interface.html#select):

    ```bash
    meltano select <plugin> --list

    # For example:
    meltano select tap-gitlab --list
    ```

### Choose how to replicate each entity

If the data source you'll be pulling data from is a database, like [PostgreSQL](https://hub.meltano.com/extractors/postgres.html) or [MongoDB](https://hub.meltano.com/extractors/mongodb.html), your extractor likely requires one final setup step:
setting a [replication method](/docs/integration.html#replication-methods) for each [selected entity (table)](#select-entities-and-attributes-to-extract).

Extractors for SaaS APIs typically hard-code the appropriate replication method for each supported entity, so if you're using one, you can skip this section and [move on to setting up a loader](#add-a-loader-to-send-data-to-a-destination).

Most database extractors, on the other hand, support two or more of the following replication methods and require you to choose an appropriate option for each table through the `replication-method` [stream metadata](/docs/integration.html#setting-metadata) key:

- `LOG_BASED`: [Log-based Incremental Replication](/docs/integration.html#log-based-incremental-replication)

    The extractor uses the database's binary log files to identify what records were inserted, updated, and deleted from the table since the last run (if any), and extracts only these records.

    This option is not supported by all databases and database extractors.

- `INCREMENTAL`: [Key-based Incremental Replication](/docs/integration.html#key-based-incremental-replication)

    The extractor uses the value of a specific column on the table (the [Replication Key](/docs/integration.html#replication-key), e.g. an `updated_at` timestamp or incrementing `id` integer) to identify what records were inserted or updated (but not deleted) since the last run (if any), and extracts only those records.

- `FULL_TABLE`: [Full Table Replication](/docs/integration.html#full-table-replication)

    The extractor extracts all available records in the table on every run.

*To learn more about replication methods, refer to the [Data Integration (EL) guide](/docs/integration.html#replication-methods).*

1. Find out which replication methods (i.e. options for the `replication-method` [stream metadata](/docs/singer-spec.html#metadata) key) the extractor supports by checking its documentation or the README in its repository.

1. Set the desired `replication-method` metadata for each [selected entity](#select-entities-and-attributes-to-extract) using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) and the extractor's [`metadata` extra](/docs/plugins.html#metadata-extra):

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

    If you've set a table's `replication-method` to `INCREMENTAL`, also choose a [Replication Key](/docs/integration.html#replication-key) by setting the `replication-key` metadata:

    ```bash
    meltano config <plugin> set _metadata <entity> replication-key <column>

    # For example:
    meltano config tap-postgres set _metadata some_entity_id replication-key updated_at
    meltano config tap-postgres set _metadata some_entity_id replication-key id
    ```

    This will add the [metadata rules](/docs/plugins.html#metadata-extra) to your [`meltano.yml` project file](/docs/project.html#plugin-configuration):

    ```yml{4-13}
    plugins:
      extractors:
      - name: tap-gitlab
        metadata:
          some_entity_id:
            replication-method: INCREMENTAL
            replication-key: id
          other_entity:
            replication-method: FULL_TABLE
          '*':
            replication-method: INCREMENTAL
          '*_full':
            replication-method: FULL_TABLE
    ```

1. Optionally, verify that the [stream metadata](/docs/singer-spec.html#metadata) for each table was set correctly in the extractor's [generated catalog file](/docs/integration.html#extractor-catalog-generation) by dumping it using [`meltano invoke --dump=catalog <plugin>`](/docs/command-line-interface.html#select):

    ```bash
    meltano invoke --dump=catalog <plugin>

    # For example:
    meltano invoke --dump=catalog tap-postgres
    ```

## Add a loader to send data to a destination

Now that your Meltano project has everything it needs to pull data from your source,
it's time to tell it where that data should go!

This is where the [loader](/docs/plugins.html#loaders) comes in,
which will be responsible for loading [extracted](#add-an-extractor-to-pull-data-from-a-source) data into an arbitrary data destination.

*To learn more about adding plugins to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-a-plugin-to-your-project).*

1. Find out if a loader for your data destination is [supported out of the box](/docs/plugins.html#discoverable-plugins)
by checking the [Loaders list](https://hub.meltano.com/loaders/) or using [`meltano discover`](/docs/command-line-interface.html#discover):

    ```bash
    meltano discover loaders
    ```

1. Depending on the result, pick your next step:

    - If a loader is **supported out of the box**, add it to your project using [`meltano add`](/docs/command-line-interface.html#add):

      ```bash
      meltano add loader <plugin name>

      # For example:
      meltano add loader target-postgres

      # If you have a preference for a non-default variant, select it using `--variant`:
      meltano add loader target-postgres --variant=transferwise
      ```

      This will add the new plugin to your [`meltano.yml` project file](/docs/project.html#plugins):

      ```yml{3-5}
      plugins:
        loaders:
        - name: target-postgres
          variant: datamill-co
          pip_url: singer-target-postgres
      ```

      You can now continue to step 4.

    - If a loader is **not yet discoverable**, find out if a Singer target for your data source already exists by checking [Singer's index of targets](https://www.singer.io/#targets) and/or doing a web search for `Singer target <data destination>`, e.g. `Singer target BigQuery`.

1. Depending on the result, pick your next step:

    - If a Singer target for your data destination is **available**, add it to your project as a [custom plugin](/docs/plugins.html#custom-plugins) using [`meltano add --custom`](/docs/command-line-interface.html#add):

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

        This will add the new plugin to your [`meltano.yml` project file](/docs/project.html#plugins):

        ```yml{3-10}
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

        *To learn more about adding custom plugins, refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).*

        ::: tip
        Once you've got the loader working in your project, please consider
        [contributing its description](/docs/contributor-guide.html#discoverable-plugins)
        to the [index of discoverable plugins](/docs/plugins.html#discoverable-plugins)
        so that it can be supported out of the box for new users!
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

::: details What if I already have a config file for this loader?

If you've used this Singer target before without Meltano, you may have a [config file](/docs/singer-spec.html#config-files) already.

If you'd like to use the same configuration with Meltano, you can skip this section and copy and paste the JSON config object into your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) under the [plugin's `config` key](/docs/project.html#plugin-configuration):

```yaml{3-6}
loaders:
- name: target-example
  config: {
    "setting": "value",
    "another_setting": true
  }
```

Since YAML is a [superset of JSON](https://yaml.org/spec/1.2/spec.html#id2759572), the object should be indented correctly, but formatting does not need to be changed.

:::

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
    meltano config target-postgres set postgres_host localhost
    meltano config target-postgres set postgres_port 5432
    meltano config target-postgres set postgres_username meltano
    meltano config target-postgres set postgres_password meltano
    meltano config target-postgres set postgres_database warehouse
    meltano config target-postgres set postgres_schema public
    ```

    This will add the non-sensitive configuration to your [`meltano.yml` project file](/docs/project.html#plugin-configuration):

    ```yml{5-10}
    plugins:
      loaders:
      - name: target-bigquery
        variant: datamill-co
        config:
          postgres_host: localhost
          postgres_port: 5432
          postgres_username: meltano
          postgres_database: warehouse
          postgres_schema: public
    ```

    Sensitive configuration (like `postgres_password`) will instead be stored in your project's [`.env` file](/docs/project.html#env) so that it will not be checked into version control:

    ```bash
    export TARGET_POSTGRES_PASSWORD=meltano
    ```

1. Optionally, verify that the configuration looks like what the Singer target expects according to its documentation using [`meltano config <plugin>`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <plugin>

    # For example:
    meltano config target-postgres
    ```

    This will show the current configuration:

    ```json
    {
      "postgres_host": "localhost",
      "postgres_port": 5432,
      "postgres_username": "meltano",
      "postgres_password": "meltano",
      "postgres_database": "warehouse",
      "postgres_schema": "public"
    }
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

If you run `meltano elt` another time with the same Job ID, you'll see it automatically pick up where the previous run left off, assuming the extractor supports [incremental replication](/docs/integration.html#incremental-replication-state).

::: details What if I already have a state file for this extractor?

If you've used this Singer tap before without Meltano, you may have a [state file](/docs/singer-spec.html#state-files) already.

If you'd like Meltano to use it instead of [looking up state based on the Job ID](/docs/integration.html#incremental-replication-state), you can either use [`meltano elt`](/docs/command-line-interface.html#elt)'s `--state` option or set the [`state` extractor extra](/docs/plugins.html#state-extra).

If you'd like to dump the state generated by the most recent run into a file, so that you can explicitly pass it along to the next invocation, you can use [`meltano elt`](/docs/command-line-interface.html#elt)'s `--dump=state` option:

```bash
meltano elt <extractor> <loader> --job_id=<pipeline name> --dump=state > state.json

# For example:
meltano elt tap-gitlab target-postgres --job_id=gitlab-to-postgres --dump=state > state.json
```

:::

## Next steps

Now that you've successfully run your first data integration (EL) pipeline using Meltano,
you have a few possible next steps:

- [Schedule pipelines to run regularly](#schedule-pipelines-to-run-regularly)
- [Transform loaded data for analysis](#transform-loaded-data-for-analysis)
- [Containerize your project](#containerize-your-project)
- [Deploy your pipelines in production](#deploy-your-pipelines-in-production)

### Schedule pipelines to run regularly

Most pipelines aren't run just once, but over and over again, to make sure additions and changes in the source eventually make their way to the destination.

To help you realize this, Meltano supports scheduled pipelines that can be orchestrated using [Apache Airflow](https://airflow.apache.org/).

*To learn more about orchestration, refer to the [Orchestration guide](/docs/orchestration.html).*

1. Schedule a new [`meltano elt`](/docs/command-line-interface.html#elt) pipeline to be invoked on an interval using [`meltano schedule`](/docs/command-line-interface.html#schedule):

    ```bash
    meltano schedule <pipeline name> <extractor> <loader> <interval>

    # For example:
    meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily
    ```

    The `pipeline name` argument corresponds to the `--job_id` option on `meltano elt`, which identifies related EL(T) runs when storing and looking up [incremental replication state](/docs/integration.html#incremental-replication-state).
    To have scheduled runs pick up where your [earlier manual run](#run-a-data-integration-el-pipeline) left off, ensure you use the same pipeline name.

    This will add the new schedule to your [`meltano.yml` project file](/docs/project.html#schedules):

    ```yml{2-6}
    schedules:
    - name: gitlab-to-postgres
      extractor: tap-gitlab
      loader: target-postgres
      transform: skip
      interval: '@daily'
    ```

1. Optionally, verify that the schedule was created successfully using [`meltano schedule list`](/docs/command-line-interface.html#schedule):

    ```bash
    meltano schedule list
    ```

1. Add the [Apache Airflow](https://airflow.apache.org/) orchestrator to your project using [`meltano add`](/docs/command-line-interface.html#add), which will be responsible for managing the schedule and executing the appropriate `meltano elt` commands:

    ```bash
    meltano add orchestrator airflow
    ```

    This will add the new plugin to your [`meltano.yml` project file](/docs/project.html#plugins):

    ```yml{3-4}
    plugins:
      orchestrators:
      - name: airflow
        pip_url: apache-airflow==1.10.14
    ```

    It will also automatically add a
[`meltano elt` DAG generator](https://gitlab.com/meltano/files-airflow/-/blob/master/bundle/orchestrate/dags/meltano.py)
to your project's `orchestrate/dags` directory, where Airflow
will be configured to look for [DAGs](https://airflow.apache.org/docs/apache-airflow/1.10.14/concepts.html#dags) by default.

1. Start the [Airflow scheduler](https://airflow.apache.org/docs/apache-airflow/1.10.14/scheduler.html) using [`meltano invoke`](/docs/command-line-interface.html#invoke):

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

    The web interface and DAG overview will be available at <http://localhost:8080>.

### Transform loaded data for analysis

Once your raw data has arrived in your data warehouse, its schema will likely need to be transformed to be more appropriate for analysis.

To help you realize this, Meltano supports transformation using [`dbt`](https://www.getdbt.com/).

To learn about data transformation, refer to the [Data Transformation (T) guide](/docs/transforms.html).

### Containerize your project

To learn how to containerize your project, refer to the [Containerization guide](/docs/containerization.html).

### Deploy your pipelines in production

To learn how to deploy your pipelines in production, refer to the [Deployment in Production guide](/docs/production.html).
