# Developer Tools

Meltano is primarily offered to end-users as a hosted software-as-a-service (SaaS) solution for busy non-technical business owners looking to gain insights into their business data. However, we are also [an open source project](https://gitlab.com/meltano/meltano), and you have the option to [self-host Meltano](http://localhost:8080/docs/developer-tools.html#self-hosted-installation).

- [Self-Hosted Installation Guide](/docs/developer-tools.html#self-hosted-installation)
- [Upgrading Meltano Version](/docs/developer-tools.html#upgrading-meltano-version)
- [Command Line Interface](/docs/developer-tools.html#command-line-interface)
- [Environment Variables](/docs/developer-tools.html#environment-variables)
- [Reporting Database Options](/docs/developer-tools.html#reporting-database-options)
- [Role-Based Access Control](/docs/developer-tools.html#role-based-access-control-alpha)
- [Open Source Contributor Guide](/docs/developer-tools.html#contributor-guide)
- [Overview of Meltano Architecture](/docs/developer-tools.html#architecture)

## Self-Hosted Installation

This section provides guides for getting set up with a self-hosted instance of Meltano's open source data analytics software on your local computer or using popular hosting solutions:

- [Local Installation](/docs/developer-tools.html#local-installation)
- [Docker](/docs/developer-tools.html#installing-on-docker)
- [Amazon Web Services (AWS)](/docs/developer-tools.html#amazon-web-services-aws)

::: tip
Are you trying Meltano for the first time? You can skip the installation process and we'll set you up with a free 30-day trial of Meltano as a hosted service. If you decide you want to switch to self-hosted later we can clone your instance so you can take it with you. [Sign up here.](https://meltano.typeform.com/to/NJPwxv)
:::

### Local Installation

In this section, we will install Meltano as a local application on your computer that you can access from your browser and on the command line.

::: tip
We do not have a double click installer at this time, but [it is on our roadmap](https://gitlab.com/meltano/meltano/issues/1107) and we will be sure to update this page when we do!
:::

#### Requirements

Before you install Meltano, make sure you have the following requirements installed and up to date.

##### Unix-like environment

::: warning
There is currently a known issue with macOS 10.15 and Python 3. For more information, visit [issue #1468](https://gitlab.com/meltano/meltano/issues/1468).
:::

Recent versions of Linux and macOS are both fully supported, but Windows is not.

If you'd like to run Meltano on Windows, you can install it inside the [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about). You may also try [installing Meltano on Docker](#installing-on-docker), although Docker on Windows is known to have [some idiosyncrasies](https://gitlab.com/meltano/meltano/issues/1261#note_240256080) that might hinder Meltano's ability to function.

##### Python 3+

- [Python 3.6.1+](https://realpython.com/installing-python/)

::: tip
You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.
:::

To check if you have the correct Python version, open your terminal and use the following commands to check the version:

```bash
python --version
```

If you've installed Python 3, but are not getting the result you expect, you may have installed Python 3 alongside an existing Python 2 installation. In this case, please use `python3` and `pip3` wherever this guide refers to the `python` and `pip` commands.

##### pip

`pip` is a package installer that comes automatically with Python 3+. This is also what we will be using to install Meltano. Here are some commands related to `pip` that may be of interest:

```bash
# Check for current version of pip
# to ensure that it is using the Python3 pip
pip --version

# Update pip
pip install --upgrade pip
```

##### Virtual Environment

::: danger IMPORTANT
Unless you are building a Docker image, it is **strongly recommended** that Meltano be installed inside a virtual environment in order to avoid potential system conflicts that may be difficult to debug.
:::

**Why use a virtual environment?**

Your local environment may use a different version of Python or other dependencies that are difficult to manage. The virtual environment provides a "clean" space to work without these issues.

##### Recommended Virtual Environment Setup

We suggest you create a directory where you want your virtual environments to be saved (e.g. `.venv/`). This can be any directory in your environment, but we recommend saving it in your Meltano project to make it easier to keep track of.

Then create a new virtual environment inside that directory:

```bash
mkdir .venv
python -m venv .venv/meltano
```

##### Activating Your Virtual Environment

Activate the virtual environment using:

```bash
source .venv/meltano/bin/activate
```

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to your prompt.

::: tip
Once a virtual environment is activated, it stays active until the current shell is closed. In a new shell, you must re-activate the virtual environment before interacting with the `meltano` command that will be installed in the next step.

To streamline this process, you can define a [shell alias](https://shapeshed.com/unix-alias/) that'll be easier to remember than the entire activation invocation:

```bash
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
alias meltano!="source $MELTANO_PROJECT_PATH/.venv/meltano/bin/activate"

# Use as follows, after creating a new shell:
meltano!
```

You can deactivate a virtual environment by typing `deactivate` in your shell.

:::

#### Install Meltano

Now that you have your virtual environment set up and running, run the following command to install the Meltano package:

```bash
pip install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```

That's it! Meltano is now be available for you to use.

Now that you have successfully installed Meltano and its requirements, you can [create your first project](http://localhost:8080/docs/developer-tools.html#create-your-first-project).

### Installing on Docker

[Docker](https://www.docker.com/) is an alternative installation option to [using a virtual environment to run Meltano](/docs/installation.html#virtual-environment). To use these instructions you will need to [install Docker](https://docs.docker.com/install/) onto your computer and have it running when you execute the commands below.

##### Using Pre-built Docker Images

We provide the [meltano/meltano](https://hub.docker.com/r/meltano/meltano) docker image with Meltano pre-installed and ready to use.

> Note: The **meltano/meltano** docker image is also available in GitLab's registry: `registry.gitlab.com`

This image contains everything you need to get started with Meltano.

```bash
# download or update to the latest version
docker pull meltano/meltano

# look the currently installed version
docker run meltano/meltano --version
```

##### Initialize Your Project

Once you have Docker installed, running, and have pulled the pre-built image you can use Meltano just as you would in our [Getting Started Guide](/docs/getting-started.html). However, the command line syntax is slightly different. For example, let's create a new Meltano project:

```
docker run -v $(pwd):/projects \
             -w /projects \
             meltano/meltano init yourprojectname
```

Then you can `cd` into your new project:

```
cd yourprojectname
```

We can then start the Meltano UI. Since `ui` is the default command, we can omit it.

```
docker run -v $(pwd):/project \
             -w /project \
             -p 5000:5000 \
             meltano/meltano
```

You can now visit [http://localhost:5000](http://localhost:5000) to access the Meltano UI.

If you are a Meltano end-user who is not going to be contributing code to our open source repository, you should be able to use Meltano entirely from the UI at this point.

Follow the steps in our [Getting Started Guide](/docs/getting-started.html) to get started.

## Amazon Web Services (AWS)

::: warning Prerequisites
This guide assumes that you have a functioning Docker image where your Meltano project is already bundled with the Meltano installation. To track this issue, follow [meltano#624](https://gitlab.com/meltano/meltano/issues/624).
:::

In this section, we will be going over how you can deploy a Meltano Docker image to AWS.

### Setting Up Elastic Container Service (ECS)

1. Login to [AWS Console](https://console.aws.amazon.com)
1. Search for [ECS](https://console.aws.amazon.com/ecs) and click on the link

![](/screenshots/aws-ecs.png)

![](/screenshots/aws-ecs-getting-started.png)

1. We will create a new _Container definition_ by clicking on the `Configure` button in the **custom** card
1. Fill out the form with the following data:

- **Container name**: Meltano
- **Image**: YOUR_DOCKER_IMAGE_URL
  - Examples:
    - docker.io/namespace/image-name:tag
    - registry.gitlab.com/namespace/project/image-name:tag
- **Memory Limits (MiB)**: Soft limit 1024
- **Port mappings**:
  - 5000/tcp (meltano)

1. Click `Update` button to finish setting up your container defintion
1. Click `Edit` next to the _Task defintion_ heading
1. Update the form with the following:

- **Task definition name**: meltano-run
- **Network mode**: awsvpc
- **Task execution role**: ecsTaskExecutionRole
- **Compatibilities**: FARGATE
- **Task memory**: 1GB (1024)
- **Task CPU**: 0.25 vCPU (256)

1. Click `Next` to move to the next step

### Review service properties

![](/screenshots/aws-ecs-review-service.png)

1. Verify that the properties are as follows:

- **Service name**: meltano-service
- **Number of desired tasks**: 1
- **Security group**: Automatically create new
- **Load balancer type**: None

1. Click `Next` to move on to the next step

### Configure Your Cluster

The main configuration here is the **Cluster name**. We provide a suggestion below, but feel free to name it as you wish.

- **Cluster name**: meltano-cluster
- **VPC ID**: Automatically create new
- **Subnets**: Automatically create new

### Review Cluster Configuration

After you click `Next`, you will have the opportunity to review all of the properties that you set. Once you confirm that the settings are correct, click `Create` to setup your ECS.

You should now see a page where Amazon prepares the services we configured. There will be spinning icons on the right of each service that will live update as it finished. Once you see everything has setup properly, you're cluster has been successfully deployed!

### Final steps

![](/screenshots/aws-ecs-final-steps.png)

1. Open the page with your cluster
1. Click on the _Tasks_ tab
1. You should see a task that has a status of `RUNNING` for _Last Status_
1. Click on the _Task ID_ link (e.g., 0b35dea-3ca..)
1. Under _Network_, you can find the URL for your instance under _Public IP_ (e.g., 18.18.134.18)
1. Open a new tab in your browser and visit this new URL on port 5000 (e.g., http://18.18.134.18:5000)

::: tip
The IP address can be mapped to a domain using Route53. We will be writing up a guide on how to do this. You can follow along at [meltano#625](https://gitlab.com/meltano/meltano/issues/625).
:::

#### Next Steps

Once you have successfully installed Meltano from the command line, you will need to [create your first project from the command line](/docs/developer-tools.html#create-your-first-project).

## Troubleshooting Installation

::: tip
Are you having installation or deployment problems? We are here to help you. Check out [Getting Help](/docs/getting-help.html) on the different ways to get in touch with us.
:::

### Configure network access

::: tip
This section is only necessary if you do not have a Security Group that allows for port 5000,5010 inbound.
:::

Once you complete the cluster setup, you should be brought to the detail page for the service. You should be default on a tab called _Details_ with a _Network Access_ section.

1. Navigate to the _Details_ tab
1. Under _Network Access_, click on the link next to _Security Groups_ (e.g., sg-f0dj093dkjf10)
1. This should open a new tab with your security group
1. Navigate to the _Inbound Rules_ tab on the bottom of the page
1. Click `Edit Rules`
1. Delete any existing rules
1. Click `Add Rule` with the following properties:

- **Type**: Custom TCP Rule
- **Protocol**: TCP
- **Port Range**: 5000
- **Source**: Custom 0.0.0.0/0

1. Click "Add Rule" with the following properties:

- **Type**: Custom TCP Rule
- **Protocol**: TCP
- **Port Range**: 5010
- **Source**: Custom 0.0.0.0/0

1. Click `Save rules`

## Upgrading Meltano Version

We release a new version of Meltano every week. To keep tabs on the latest releases, follow along on the [Meltano blog](https://meltano.com/blog/), or have a look at our [CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md).

### Using Meltano UI

When an update is available, you will be informed of this automatically through a shiny blue button in the top right corner of Meltano UI:

![](/screenshots/update-available.png)

Clicking this button will show more information and give you the option to install the update right away:

![](/screenshots/update-available-popup.png)

The Meltano UI will refresh automatically once installation is complete.

### Using the command line

If you're not using Meltano UI, you can update Meltano to the latest version by running the following command in your terminal:

```
meltano upgrade
```

## Command Line Interface

Meltano provides a command line interface (CLI) that allows you to manage the configuration and orchestration of Meltano instances. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

- [Getting Started Guide for the Command Line](/docs/developer-tools.html#gettting-started-with-meltano-on-the-command-line)
- [Glossary of Command Line Concepts]()

### Getting Started with Meltano on the Command Line

Once you have successfully installed Meltano from the command line, you will need to create a project before you launch the Meltano UI.

### Create your first project

To initialize a new project, open your terminal and navigate to the directory that you'd like to store your Meltano projects in.

Use the `meltano init` command, which takes a `PROJECT_NAME` that is of your own choosing. For this guide, let's create a project called "myprojectname".

```bash
meltano init myprojectname
```

This will create a new directory named `myprojectname` in the current directory and initialize Meltano's basic directory structure inside it.

Inside the Meltano project directory, all plugin configuration (which may include tokens and passwords) is stored inside the `.meltano` directory, which is automatically added to the project's `.gitignore` file to prevent this potentially sensitive information from accidentally being pushed up to a hosted Git repository.

### Setup your loader

Self-hosted Meltano instances require you to configure your reporting database, which we call the Meltano **Loader**, from the command line. To do this, you will supply your database configuration through a `.env` file.

Once you create the file, you will need to paste in the configuration for your database. For example, PostgreSQL configurations can [be found here](/plugins/loaders/postgres.html#intermediate-connecting-meltano-to-an-existing-postgresql-database).

After saving your configurations, you can load your configurations by running:

```bash
source .env
```

And just like that, your loader is configured!

### Start the application

Now that you've created your first Meltano project, let's change directory to our new project and start Meltano UI:

```bash
cd myprojectname
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

Now that you have access to the Meltano UI, [use our Getting Started guide](http://localhost:8080/docs/getting-started.html#create-your-meltano-account) to learn more about how to use the software.


### Glossary of Command Line Concepts

### `add`

The `add` command allows you to add an extractor, loader, or transform to your Meltano instance.

#### Extractor / Loader

When you add a extractor or loader to a Meltano instance, Meltano will:

1. Add it to the `meltano.yml` file
1. Installs it in the `.meltano` directory with `venv` and `pip`

You can run `meltano add` with `--include-related` to automatically install all transform, model, and dashboard plugins related to an extractor.

##### Examples

```bash
# Extractor / Loader Template
meltano add [extractor | loader] [name_of_plugin]

# Extractor Example
meltano add extractor tap-gitlab

# Extractor Example including related plugins
meltano add --include-related extractor tap-google-analytics

# Loader Example
meltano add loader target-postgres
```

#### Transform

When you add a transform to a Meltano instance, Meltano will:

1. Installs dbt transformer to enable transformations (if needed)
1. Add transform to `meltano.yml file`
1. Updates the dbt packages and project configuration

##### Example

```bash
# Transform Template
meltano add [transform] [name_of_transform]
```

#### Model

When you add a model to a Meltano instance, Meltano will:

1. Add a model bundle to your `meltano.yml` file to help you interactively generate SQL
1. Install the model inside the `.meltano` directory which are then available to use in the Meltano webapp

##### Example

```bash
meltano add model [name_of_model]
```

#### Dashboard

When you add a dashboard to a Meltano instance, Meltano will:

1. Add a dashboard bundle to your `meltano.yml` file
1. Install the dashboard and reports inside the `analyze` directory which are then available to use in the Meltano webapp

##### Example

```bash
meltano add dashboard [name_of_dashboard]
```

#### Orchestration

When you add an orchestrator to a Meltano instance, Meltano will:

1. Adds an orchestrator plugin to your **meltano.yml**
1. Installs it

##### Example

```bash
meltano add orchestrator [name_of_orchestrator]
```

### `config`

Enables you to change a plugin's configuration.

Meltano uses configuration layers to resolve a plugin's configuration:

1. Environment variables
1. Plugin definition's `config:` attribute in **meltano.yml**
1. Settings set via `meltano config` or in the UI (stored in the system database)
1. Default values set in the setting definition in **discovery.yml**

::: info
Sensitive settings such as _passwords_ or _keys_ should not be configured using `meltano.yml`, 
since the entire contents of this file are available to the Meltano UI and its users.

Instead, these sensitive values should be stored in environment variables, or the system database (using `meltano config` or the UI).

You can use `meltano config <plugin_name> list` to find the environment variable associated with a setting.

Note that in each of these cases, Meltano stores the configuration as-is, without encryption.
:::

#### How to use

```bash
# Displays the plugin's configuration.
meltano config <plugin_name>

# List the available settings for the plugin.
meltano config <plugin_name> list

# Sets the configuration's setting `<name>` to `<value>`.
meltano config <plugin_name> set <name> <value>

# Remove the configuration's setting `<name>`.
meltano config <plugin_name> unset <name>

# Clear the configuration (back to defaults).
meltano config <plugin_name> reset
```

### `discover`

Lists the available plugins you are interested in.

#### How to Use

```bash
# List all available plugins
meltano discover all

# Only list available extractors
meltano discover extractors

# Only list available loaders
meltano discover loaders

# Only list available models
meltano discover models
```

### `elt`

This allows you to run your ELT pipeline to Extract, Load, and Transform the data with configurations of your choosing:

1. The `job_id` is autogenerated using the current date and time if it is not provided (via `--job_id` or `$MELTANO_JOB_ID`)
1. The `run_id` is a UUID autogenerated at each run
1. All the output generated by this command is also logged in `.meltano/run/elt/{job_id}/{run_id}/elt.log`

#### How to use

```bash
meltano elt <extractor> <loader> [--job_id TEXT] [--transform run] [--dry]
```

#### Parameters

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

#### Examples

```bash
meltano select --exclude tap-carbon-intensity '*' 'longitude'
```

```bash
meltano select --exclude tap-carbon-intensity '*' 'latitude'
```

This will exclude all `longitude` and `latitude` attributes.

### `extract`

Extract data to a loader and optionally transform the data

#### How to Use

```bash
meltano extract [name of extractor] --to [name of loader]`
```

### `init`

Used to create a new meltano project with a basic infrastructure in place in the current directory that the user is in.

#### How to use

```bash
# Format
meltano init [project_name] [--no_usage_stats]
```

#### Parameters

- **project_name** - This determines the folder name for the project

#### Options

- **no_usage_stats** - This flag disables sending anonymous usage data when creating a new project.

### `install`

Installs all the dependencies of your project based on the **meltano.yml** file.

Use `--include-related` to automatically install transform, model, and dashboard plugins related to installed extractor plugins.

#### How to Use

```bash
meltano install

meltano install --include-related
```

### `invoke`

- `meltano invoke <plugin_name> PLUGIN_ARGS...`: Invoke the plugin manually.

### `list`

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

### `permissions`

::: info
This is an optional tool for users who want to configure permissions if they're using Snowflake as the data warehouse and want to granularly set who has access to which data at the warehouse level.

Alpha-quality [Role Based Access Control (RBAC)](/docs/security-and-privacy.html#role-based-access-control-rbac-alpha) is also available.
:::

Use this command to check and manage the permissions of a Snowflake account.

```bash
meltano permissions grant <spec_file> --db snowflake [--dry] [--diff]
```

Given the parameters to connect to a Snowflake account and a YAML file (a "spec") representing the desired database configuration, this command makes sure that the configuration of that database matches the spec. If there are differences, it will return the sql grant and revoke commands required to make it match the spec. If there are additional permissions set in the database this command will create the necessary revoke commands with the exception of:

* Object Ownership
* Warehouse Privileges

We currently support only Snowflake, as [pgbedrock](https://github.com/Squarespace/pgbedrock) can be used for managing the permissions in a Postgres database.

##### spec_file

The YAML specification file is used to define in a declarative way the databases, roles, users and warehouses in a Snowflake account, together with the permissions for databases, schemas and tables for the same account.

Its syntax is inspired by [pgbedrock](https://github.com/Squarespace/pgbedrock), with additional options for Snowflake.

All permissions are abbreviated as `read` or `write` permissions, with Meltano generating the proper grants for each type of object. This includes shared databases which have simpler and more limited permissions than non-shared databases.

Tables and views are listed under `tables` and handled properly behind the scenes.

If `*` is provided as the parameter for tables the grant statement will use the `ALL <object_type>s in SCHEMA` syntax. It will also grant to future tables and views. See Snowflake documenation for [`ON FUTURE`](https://docs.snowflake.net/manuals/sql-reference/sql/grant-privilege.html#optional-parameters)

If a schema name includes an asterisk, such as `snowplow_*`, then all schemas that match this pattern will be included in grant statement. This can be coupled with the asterisk for table grants to grant permissions on all tables in all schemas that match the given pattern. This is useful for date-partitioned schemas.

All entities must be explicitly referenced. For example, if a permission is granted to a schema or table then the database must be explicitly referenced for permissioning as well.

A specification file has the following structure:

```bash
# Databases
databases:
    - db_name:
        shared: boolean
    - db_name:
        shared: boolean
    ... ... ...

# Roles
roles:
    - role_name:
        warehouses:
            - warehouse_name
            - warehouse_name
            ...

        member_of:
            - role_name
            - role_name
            ...

        privileges:
            databases:
                read:
                    - database_name
                    - database_name
                    ...
                write:
                    - database_name
                    - database_name
                    ...
            schemas:
                read:
                    - database_name.*
                    - database_name.schema_name
                    - database_name.schema_partial_*
                    ...
                write:
                    - database_name.*
                    - database_name.schema_name
                    - database_name.schema_partial_*
                    ...
            tables:
                read:
                    - database_name.*.*
                    - database_name.schema_name.*
                    - database_name.schema_partial_*.*
                    - database_name.schema_name.table_name
                    ...
                write:
                    - database_name.*.*
                    - database_name.schema_name.*
                    - database_name.schema_partial_*.*
                    - database_name.schema_name.table_name
                    ...

        owns:
            databases:
                - database_name
                ...
            schemas:
                - database_name.*
                - database_name.schema_name
                - database_name.schema_partial_*
                ...
            tables:
                - database_name.*.*
                - database_name.schema_name.*
                - database_name.schema_partial_*.*
                - database_name.schema_name.table_name
                ...

    - role_name:
    ... ... ...

# Users
users:
    - user_name:
        can_login: boolean
        member_of:
            - role_name
            ...
    - user_name:
    ... ... ...

# Warehouses
warehouses:
    - warehouse_name:
        size: x-small
    ... ... ...
```

For a working example, you can check [the Snowflake specification file](https://gitlab.com/meltano/meltano/blob/master/tests/meltano/core/permissions/specs/snowflake_spec.yml) that we are using for testing `meltano permissions`.

##### --db

The database to be used, either `postgres` or `snowflake`. Postgres is still experimental and may be fully supported in the future.

##### --diff

When this flag is set, a full diff with both new and already granted commands is returned. Otherwise, only required commands for matching the definitions on the spec are returned.

##### --dry

When this flag is set, the permission queries generated are not actually sent to the server and run; They are just returned to the user for examining them and running them manually.

When this flag is not set, the commands will be executed on Snowflake and their status will be returned and shown on the command line.


##### Connection Parameters

The following environmental variables must be available to connect to Snowflake:

```bash
$PERMISSION_BOT_USER
$PERMISSION_BOT_PASSWORD
$PERMISSION_BOT_ACCOUNT
$PERMISSION_BOT_DATABASE
$PERMISSION_BOT_ROLE
$PERMISSION_BOT_WAREHOUSE
```

### `schedule`

::: tip
An `orchestrator` plugin is required to use `meltano schedule`: refer to the [Orchestration](/docs/orchestration.html) documentation to get started with Meltano orchestration.
:::

Meltano provides a `schedule` method to run specified ELT pipelines at regular intervals. Schedules are defined inside the `meltano.yml` project as such:

- `meltano schedule <schedule_name> <extractor> <loader> <interval> [--transform]`: Schedule an ELT pipeline to run using an orchestrator.
  - `meltano schedule list`: List the project's schedules.

```yaml
schedules:
  - name: test
    interval: '@daily'
    extractor: tap-mock
    loader: target-mock
    transform: skip
    env: {}
```

### `select`

Use the `select` command to add select patterns to a specific extractor in your Meltano project.

- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attributes for a specific tap.

::: warning
Not all taps support this feature. In addition, taps needs to support the `--discover` switch. You can use `meltano invoke tap-... --discover` to see if the tap supports it.
:::

#### How to use

Meltano select patterns are inspired by the [glob](<https://en.wikipedia.org/wiki/Glob_(programming)>) syntax you might find in your operating system.

- `*`: matches any sequence of characters
- `?`: matches one character
- `[abc]`: matches either `a`, `b`, or `c`
- `[!abc]`: matches any character **but** `a`, `b`, or `c`

##### Examples

```bash
$ meltano select tap-carbon-intensity '*' 'name*'
```

This will select all attributes starting with `name`.

```bash
$ meltano select tap-carbon-intensity 'region'
```

This will select all attributes of the `region` entity.

::: tip
Most shells parse glob syntax: you must escape the special characters in the select pattern by quoting the pattern.
:::

#### Exclude Parameter

Use `--exclude` to exclude all attributes that match the filter.

::: info
Exclusion has precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern first.
:::

### `ui`

- `meltano ui`: Start the Meltano UI.

#### `start` (default)

Start the Meltano UI.

#### `setup`

::: tip
This command is only relevant for production-grade setup.
:::

Generate secure secrets in the `ui.cfg` so that the application is secure.

::: warning
Regenerating secrets will cause the following:

  - All passwords will be invalid
  - All sessions will be expired
  
Use with caution!
:::

##### --bits

Specify the size of the secrets, default to 256.

### `user`

::: tip
This command is only relevant when Meltano is run with authentication enabled.
:::

#### `add` 

Create a Meltano user account, active and ready to be used.

##### --overwrite, -f

Update the user instead of creating a new one.

##### --role, -G

Add the user to the role. Meltano ships with two built-in roles: `admin` and `regular`.

##### How to use

```bash
meltano user add admin securepassword --role admin
```

### `upgrade`

Upgrade Meltano to the latest version.

This function will following process to upgrade Meltano:

- Run `pip3 install --upgrade meltano`
- Run the database migrations
- Send a [SIGHUP](http://docs.gunicorn.org/en/stable/signals.html#reload-the-configuration) to the process running under the `.meltano/run/gunicorn.pid`, thus restarting the workers

### `version`

It is used to check which version of Meltano currently installed.

#### How to use

```bash
meltano --version
```

## Environment Variables

For each Meltano installation, if you need to customize environment variables, this is done with the `.env` file that is created with each new installation.

### Anonymous Usage Data

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

When anonymous usage tracking is enabled, Meltano tracks the following events:

- `meltano init {project name}`
- `meltano ui`
- `meltano elt {extractor} {loader} --transform {skip, only, run}`
- `meltano add {extractor, loader, transform, model, transformer, orchestrator}`
- `meltano discover {all, extractors, loaders, transforms, models, transformers, orchestrators}`
- `meltano install`
- `meltano invoke {plugin_name} {plugin_args}`
- `meltano select {extractor} {entities_filter} {attributes_filter}`
- `meltano schedule add {name} {extractor} {loader} {interval}`
- `meltano permissions grant --db {postgres, snowflake} --dry`

Beyond the invocation of these commands and the identified command line arguments, Meltano does not track any other event metadata, plugin configuration, or processed data.

Finally, Meltano also tracks anonymous web metrics when browsing the Meltano UI pages.

If you want to evaluate Meltano's anonymous usage tracking strategy for yourself, you can check [meltano.core.tracking.GoogleAnalyticsTracker](https://gitlab.com/meltano/meltano/blob/master/src/meltano/core/tracking/ga_tracker.py) and all the places that it is used.


### Connector Settings Configuration

Until role-based access control is implemented in Meltano, we need to prevent user editing of certain settings from the UI. View this [`tap-gitlab` environment variable setup example](/tutorials/gitlab-and-postgres.html#add-extractor) to learn how to work with this current limitation.

### Meltano UI

#### System Database

By default, Meltano uses a SQLite database named `./meltano/meltano.db` as its system database.

You can choose to use a different system database backend or configuration using the `--database-uri`
option of the `meltano` command, or the `MELTANO_DATABASE_URI` environment variable:

```bash
# SQLite (absolute path required, notice the `3` slashes before the path)
export MELTANO_DATABASE_URI=sqlite:////path/to/system_database.db
# PostgreSQL:
export MELTANO_DATABASE_URI=postgresql://username:password@host:port/database
```

#### Flask

The following are the environment variables currently available for customization for Flask.

Update your `.env` file in your project directory with the desired customizations.

```bash
export FLASK_PROFILE = ""
export FLASK_ENV = ""
```

##### Service Listen Configuration

By default, the API service listens with following host/port combination.

API: `http://0.0.0.0:5000`

To change the host/port configuration on which the API server listens, update your `.env` in your project directory with the following configuration:

```bash
# Meltano API configuration
export MELTANO_API_HOSTNAME="0.0.0.0"
export MELTANO_API_PORT="5000"
```

##### Single Sign On

These variables are specific to [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/#) and work with [OAuth authentication with GitLab](https://docs.gitlab.com/ee/integration/oauth_provider.html).

::: tip
These settings are used for single-sign-on using an external OAuth provider.
:::

Update your `.env` file in your project directory with the desired customizations.

```bash
# GitLab Client ID
export OAUTH_GITLAB_APPLICATION_ID = ""
# GitLab Client Secret
export OAUTH_GITLAB_SECRET = ""
```

For more information on how to get these from your GitLab application, check out the [integration docs from GitLab](https://docs.gitlab.com/ee/integration/gitlab.html).

#### Read-Only mode

The disable all modifications to the Meltano UI, you can run Meltano using the *read-only* mode.

```bash
# Meltano read-only mode
export MELTANO_READONLY=1
```

#### OAuth Service

::: tip
Meltano provides a public hosted solution at <https://oauth.svc.meltanodata.com>.
:::

```bash
# use the public OAuth Service
MELTANO_OAUTH_SERVICE_URL=https://oauth.svc.meltanodata.com

# use the local OAuth Service
MELTANO_OAUTH_SERVICE_URL=http://localhost:5000/-/oauth
```

### Meltano OAuth Service

Meltano ships with an OAuth Service to handle the OAuth flow in the Extractors' configuration.

::: warning
To run this service, you **must** have a registered OAuth application on the [Authorization server](https://www.oauth.com/oauth2-servers/definitions/#the-authorization-server).

Most importantly, the Redirect URI must be set properly so that the OAuth flow can be completed.

This process is specific to each Provider.
:::

#### Starting the service

The OAuth Service is bundled within Meltano, and is automatically started with `meltano ui` and mounted at `/-/oauth` for development purposes.

As it is a Flask application, it can also be run as a standalone using:

```bash
FLASK_ENV=production FLASK_APP=meltano.oauth python -m flask run --port 9999
```

#### Providers configuration

##### Facebook

```bash
OAUTH_FACEBOOK_CLIENT_ID=<application_id>
OAUTH_FACEBOOK_CLIENT_SECRET=<application_secret>
```

## Reporting Database Options

Users who chose to self-host Meltano need to create, configure and connect a **Loader** database to Meltano. Meltano Loaders _load data in bulk_ after it has been imported from source(s) using Extractors. Meltano currently supports loading data in the follow formats:

- [Comma Separated Values (CSV)](/plugins/loaders/csv.html)
- [Snowflake Data Warehouse](/plugins/loaders/snowflake.html)
- [PostgresQL Database](/plugins/loaders/postgres.html)
- [SQLite Database](/plugins/loaders/sqlite.html)

::: tip
Hosted instances of Meltano come with a pre-configured PostgresQL database where Meltano loads extracted data so that it can be analyzed. If you are not sure how to set up your Loader, you can [sign up for a free hosted instance](https://meltano.typeform.com/to/NJPwxv) and we'll take care of that for you.
:::

## Role Based Access Control <sup>ALPHA</sup>

::: danger IMPORTANT
This feature is experimental and subject to change.
:::

In the current architecture of Meltano, authorization is technically always enabled because every installation of Meltano comes with a single user that has administrative rights to everything. In other words, there are no restrictions as far as what the user can do and there is no difference between users who are logged in to Meltano.

While this functionality is still in alpha, you can enable RBAC by setting the environment variable `MELTANO_AUTHENTICATION` to `true`.

```bash
# Set in your .env file
export MELTANO_AUTHENTICATION=true
```

Now you can start your Meltano installation with:

```bash
meltano ui
```

### User Authentication

You should see the following login page whenever you open Meltano.

![](/screenshots/meltano-login.png)

There are two primary ways to authenticate:

1. Local user registration through the Register link
1. Authentication through a GitLab account

### Managing Roles

Meltano uses a RBAC (role-based access control) to expose resources to the current authenticated user.

- User: associated to an email, serves as the primary identity
- Role: associated to users, serves as the authorization source
- Permission: associated to roles, express the authorization scope
- Resource: Any `Design`, `Report`, `Dashboard`

In this system, any permission is assigned a "Context" which represent a pattern upon which resources will be tested for. Currently, the context tests for the `name` attribute of resources.

Here's an example, let's say we have a `Design` named `finance.month_over_month` and a `Permission` with a context `finance.*`, then this `Design` would be available to all users that have any role having this `Permission`.

This system allows you to create any kind of hierarchical system:

- _department.resource-name_
- _topic.resource-name_
- _access-level.resource-name_

## Contributor Guide

### Prerequisites

In order to contribute to Meltano, you will need the following:

1. [Python 3.6.1+](https://www.python.org/downloads/)
2. [Node 8.11.0+](https://nodejs.org/)
3. [Yarn](https://yarnpkg.com/)

### Where to start?

We welcome contributions, idea submissions, and improvements. In fact we may already have open issues labeled [Accepting Merge Requests] if you don't know where to start. Please see the contribution guidelines below for source code related contributions.

#### Metrics (anonymous usage data) tracking

As you contribute to Meltano, you may want to disable [metrics tracking](/docs/environment-variables.html#anonymous-usage-data) globally rather than by project. You can do this by setting the environment variable `MELTANO_DISABLE_TRACKING` to `True`:

```bash
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
export MELTANO_DISABLE_TRACKING=True
```

### Setting Up Your Environment

```bash
# Clone the Meltano repo
git clone git@gitlab.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Optional, but it's best to have the latest pip
pip install --upgrade pip

# Optional, but it's best to have the latest setuptools
pip install --upgrade setuptools

# Optional, but it's recommended to create a virtual environment
# in order to minimize side effects from unknown environment variable
python -m venv ~/.venv/meltano-development

# Activate your virtual environment
source ~/.venv/meltano-development/bin/activate

# Install all the dependencies
pip install -r requirements.txt

# Install dev dependencies with the edit flag on to detect changes
# Note: you may have to escape the .`[dev]` argument on some shells, like zsh
pip install -e .[dev]

# Bundle the Meltano UI into the `meltano` package
make bundle
```

Meltano is now installed and available at `meltano`, as long as you remain in your `meltano-development` virtual environment!

This means that you're ready to start Meltano CLI development. For API and UI development, read on.

### API Development

This section of the guide provides guidance on how to work with the Meltano API, which serves as the backend of Meltano and is built with the [Python framework: Flask](https://github.com/pallets/flask).

#### Getting Setup

After all of your dependencies installed, we recommend opening a new window/tab in your terminal so you can run the following commands:

```bash
# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start a development build of the Meltano API and a production build of Meltano UI
FLASK_ENV=development meltano ui
```

The development build of the Meltano API and a production build of the UI will now be available at <http://localhost:5000/>.

::: tip

To debug your Python code, here is the recommended way to validate / debug your code:

```python
# Purpose: Start a debugger
# Usage: Use as a one-line import / invocation for easier cleanup
import pdb; pdb.set_trace()
```

:::

### UI Development

In the event you are contributing to Meltano UI and want to work with all of the frontend tooling (i.e., hot module reloading, etc.), you will need to run the following commands:

```bash
# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start the Meltano API and a production build of Meltano UI that you can ignore
meltano ui

# Open a new terminal tab and go to your meltano directory
cd $PROJECT_NAME

# Install frontend infrastructure at the root directory
yarn setup

# Start local development environment
yarn serve
```

The development build of the Meltano UI will now be available at <http://localhost:8080/>. 

A production build of the API will be available at <http://localhost:5000/> to support the UI, but you will not need to interact with this directly.

::: tip

If you're developing for the _Embed_ app (embeddable `iframe` for reports) you can toggle `MELTANO_EMBED`:

```bash
# Develop for the embed app
export MELTANO_EMBED=1

# Develop for the main app (this is the default)
export MELTANO_EMBED=0

# Start local development environment
yarn serve
```

:::

If you need to change the URL of your development environment, you can do this by updating your `.env` in your project directory with the following configuration:

```bash
# The URL where the web app will be located when working locally in development
# since it provides the redirect after authentication.
# Not require for production
export MELTANO_UI_URL = ""
```

### Taps & Targets Development

Watch ["How taps are built"](https://www.youtube.com/watch?v=aImidnW8nsU) for an explanation of how Singer taps (which form the basis for Meltano extractors) work, and what goes into building new ones or verifying and modifying existing ones for various types of APIs.

Then watch ["How transforms are built"](https://www.youtube.com/watch?v=QRaCSKQC_74) for an explanation of how DBT transforms work, and what goes into building new ones for new data sources.

#### Changing discovery.yml

##### `discovery.yml` version

Whenever new functionality is introduced that changes the schema of `discovery.yml` (the exact properties it supports and their types), the `version` in `src/meltano/core/bundle/discovery.yml` and the `VERSION` constant in `src/meltano/core/plugin_discovery_service.py` must be incremented, so that older instances of Meltano don't attempt to download and parse a `discovery.yml` its parser is not compatible with.

Changes to `discovery.yml` that only use existing properties do not constitute schema changes and do not require `version` to be incremented.

##### Local changes to `discovery.yml`

When you need to make changes to `discovery.yml`, these changes are not automatically detected inside of the `meltano` repo during development. While there are a few ways to solve this problem, it is recommended to create a symbolic link in order ensure that changes made inside of the `meltano` repo appear inside the Meltano project you initialized and are testing on.

1. Get path for `discovery.yml` in the repo

- Example: `/Users/bencodezen/Projects/meltano/src/meltano/core/bundle/discovery.yml`

2. Open your Meltano project in your terminal

3. Create a symbolic link by running the following command:

```
ln -s $YOUR_DISCOVERY_YML_PATH
```

Now, when you run the `ls -l` command, you should see something like:

```
bencodezen  staff   72 Nov 19 09:19 discovery.yml -> /Users/bencodezen/Projects/meltano/src/meltano/core/bundle/discovery.yml
```

Now, you can see your changes in `discovery.yml` live in your project during development! 🎉

##### Connector settings

Each extractor (tap) and loader (target) in the `discovery.yml` has a `settings` property. Nested under this property are a variable amount of individual settings. In the Meltano UI these settings are parsed to generate a configuration form. To improve the UX of this form, each setting has a number of optional properties:

```yaml
- settings:
    - name: setting_name # Required (must match the connector setting name)
      label: Setting Name # Optional (human friendly text display of the setting name)
      value: '' # Optional (Use to set a default value)
      placeholder: Ex. format_like_this # Optional (Use to set the input's placeholder default)
      kind: string # Optional (Use for a first-class input control. Default is `string`, others are `hidden`, `boolean`, `date_iso8601`, `password`, `options`, & `file`)
      description: Setting description # Optional (Use to provide inline context)
      tooltip: Here is some more info... # Optional (use to provide additional inline context)
      documentation: https://meltano.com/ # Optional (use to link to specific supplemental documentation)
      protected: true # Optional (use in combination with `value` to provide an uneditable default)
      env: SOME_API_KEY # Optional (use to delegate to an environment variable for overriding this setting's value)
```

#### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

##### How to test a tap?

We qualify taps with the capabilities it supports:

  - properties: the tap uses the old `--properties` format for the catalog
  - catalog: the tap uses the new `--catalog` format for the catalog
  - discover: the tap supports catalog extraction
  - state: the tap supports incremental extraction

###### Properties/Catalog

You should look at the tap's documentation to see which one is supported.

###### Discover

Try to run the tap with the `--discover` switch, which should output a catalog on STDOUT.

###### State

  1. Try to run the tap connect and extract data first, watching for `STATE` messages.
  1. Do two ELT run with `target-postgres`, then validate that:
    1. All the tables in the schema created have a PRIMARY KEY constraint. (this is important for incremental updates)
    1. There is no duplicates after multiple extractions

##### Troubleshooting

###### Tables are lacking primary keys

This might be a configuration issue with the catalog file that is sent to the tap. Take a look at the tap's documentation and look for custom metadata on the catalog. 

#### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target development please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitLab
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

### Dashboard Development

To create a dashboard plugin like https://gitlab.com/meltano/dashboard-google-analytics, follow these steps:

1. Set up the extractor and model you are creating dashboard(s) and reports for in your local Meltano instance.
1. Start Meltano UI.
1. Use the UI to create the desired reports based on the model's designs. Name the reports appropriately, but don't include the extractor name or label.
1. Create one or more new dashboard and add the reports to it. If you're creating just one dashboard, name it after the extractor label (e.g. "Google Analytics", not `tap-google-analytics`). If you're creating multiple dashboards, add an appropriate subtitle after a colon (e.g. "Google Analytics: My Dashboard").
1. Create a new plugin repository named `dashboard-<data source>` (e.g. `dashboard-google-analytics`).
1. Copy over `setup.py`, `README.md`, and `LICENSE` from https://gitlab.com/meltano/dashboard-google-analytics and edit these files as appropriate.
1. Move your newly created dashboards and reports from your local Meltano project's `analyze/dashboards` and `analyze/reports` to `dashboards` and `reports` inside the new plugin repository.
1. Push your new plugin repository to GitLab.com. Official dashboard plugins live at `https://gitlab.com/meltano/dashboard-...`.
1. Add an entry to `src/meltano/core/bundle/discovery.yml`  under `dashboards`. Set `namespace` to the `namespace` of the extractor and model plugins the dashboard(s) and reports are related to (e.g. `tap_google_analytics`), and set `name` and `pip_url` set as appropriate.
1. Delete the dashboard(s) and reports from your local Meltano project's `analyze` directory.
1. Ensure that your local Meltano instance uses the recently modified `discovery.yml` by following the steps under ["Local changes to discovery.yml](#local-changes-to-discovery-yml).
1. Run `meltano add --include-related extractor <extractor name>` to automatically install all plugins related to the extractor, including our new dashboard plugin. Related plugins are also installed automatically when installing an extractor using the UI, but we can't use that flow here because the extractor has already been installed.
1. Verify that the dashboard(s) and reports have automatically been added to your local Meltano project's `analyze` directory and show up under "Dashboards" in the UI.
1. Success! You can now submit a merge request to Meltano containing the changes to `discovery.yml` (and an appropriate `CHANGELOG` item, of course).

### System Database

Meltano API and CLI are both supported by a database that is managed using Alembic migrations.

:::tip Note
[Alembic](https://alembic.sqlalchemy.org/en/latest/) is a full featured database migration working on top of SQLAlchemy.
:::

Migrations for the system database are located inside the `meltano.migrations` module.

To create a new migration, use the `alembic revision -m "message"` command, then edit the created file with the necessary database changes. Make sure to implement both `upgrade` and `downgrade`, so the migration is reversible, as this will be used in migration tests in the future.

Each migration should be isolated from the `meltano` module, so **don't import any model definition inside a migration**.

:::warning
Meltano doesn't currently support auto-generating migration from the models definition.
:::

To run the migrations, use `meltano upgrade` inside a Meltano project.

### Documentation

Meltano uses [VuePress](https://vuepress.vuejs.org/) to manage its documentation site. Some of the benefits it provides us includes:

- Enhanced Markdown authoring experience
- Automatic check for broken relative links

#### Text

Follow the [Merge Requests](#merge-requests) and [Changelog](#changelog) portions of this contribution section for text-based documentation contributions.

#### Images

When adding supporting visuals to documentation, adhere to:

- Use Chrome in "incognito mode" (we do this to have the same browser bar for consistency across screenshots)
- Screenshot the image at 16:9 aspect ratio with minimum 1280x720px
- Place `.png` screenshot in `src/docs/.vuepress/public/screenshots/` with a descriptive name

### Testing

#### End-to-End Testing with Cypress

Our end-to-end tests are currently being built with [Cypress](https://www.cypress.io/).

##### How to Run Tests

1. Initialize a new meltano project with `meltano init $PROJECT_NAME`
1. Change directory into `$PROJECT_NAME`
1. Start up project with `meltano ui`
1. Clone Meltano repo
1. Open Meltano repo in Terminal
1. Run `yarn setup`
1. Run `yarn test:e2e`

This will kick off a Cypress application that will allow you to run tests as desired by clicking each test suite (which can be found in `/src/tests/e2e/specs/*.spec.js`)

![Preview of Cypres app running](/images/cypress-tests/cypTest-01.png)

::: info
In the near future, all tests can flow automatically; but there are some complications that require manual triggering due to an inability to read pipeline completion.
:::

### Code style

#### Tools

Meltano uses the below tools to enforce consistent code style. Explore the [repo](https://gitlab.com/meltano/meltano/tree/master) to learn of the specific rules and settings of each.

- [Black](https://github.com/ambv/black)
- [ESLint](https://eslint.org/docs/rules/)
- [ESLint Vue Plugin](https://github.com/vuejs/eslint-plugin-vue)
- [Prettier](https://prettier.io/)

You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

#### Mantra

> A contributor should know the exact line-of-code to make a change based on convention

In the spirit of GitLab's "boring solutions" with the above tools and mantra, the codebase is additionally sorted as follows:

##### Imports

`import`s are sorted using the following pattern:

  1. Code source location: third-party → local (separate each group with a single blank line)
  1. Import scheme: Default imports → Partial imports
  1. Name of the module, alphabetically: 'lodash' → 'vue'

::: tip
There should be only 2 blocks of imports with a single blank line between both blocks.
The first rule is used to separate both blocks.
:::

```js
import lodash from 'lodash'                  // 1: third-party, 2: default, 3: [l]odash
import Vue from 'vue'                        // 1: third-party, 2: default, 3: [v]ue
import { bar, foo } from 'alib'              // 1: third-party, 2: partial, 3: [a]lib
import { mapAction, mapState } from 'vuex'   // 1: third-party, 2: partial, 3: [v]uex
¶  // 1 blank line to split import groups
import Widget from '@/component/Widget'      // 1: local, 2: default, 3: @/[c]omponent/Widget
import poller from '@/utils/poller'          // 1: local, 2: default, 3: @/[u]tils/poller
import { Medal } from '@/component/globals'  // 1: local, 2: partial, 3: @/[c]omponent/globals
import { bar, thing } from '@/utils/utils'   // 1: local, 2: partial, 3: @/[u]tils/utils
¶
¶  // 2 blank lines to split the imports from the code 
```

```python
import flask                                        # 1: third-party, 2: default, 3: [f]lask
import os                                           # 1: third-party, 2: default, 3: [o]s
from datetime import datetime                       # 1: third-party, 2: partial, 3: [d]atetime
from functools import wraps                         # 1: third-party, 2: partial, 3: [f]unctools
¶  # 1 blank line to split import groups
import meltano                                      # 1: local, 2: default, 3: [meltano]
import meltano.migrations                           # 1: local, 2: default, 3: [meltano.m]igrations
from meltano.core.plugin import Plugin, PluginType  # 1: local, 2: partial, 3: [meltano.core.pl]ugin
from meltano.core.project import Project            # 1: local, 2: partial, 3: [meltano.core.pr]oject
¶ 
¶  # 2 blank lines to split the imports from the code 
```

##### Definitions

Object properties and methods are alphabetical where `Vuex` stores are the exception (`defaultState` -> `getters` -> `actions` -> `mutations`)

::: warning
We are looking to automate these rules in https://gitlab.com/meltano/meltano/issues/1609.
:::

:::warning Troubleshooting
When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.
:::

### UI/UX

#### Visual Hierarchy

##### Depth

The below level hierarchy defines the back to front depth sorting of UI elements. Use it as a mental model to inform your UI decisions.

- Level 1 - Primary navigation, sub-navigation, and signage - _Grey_
- Level 2 - Primary task container(s) - _White w/Shadow_
- Level 3 - Dropdowns, dialogs, pop-overs, etc. - _White w/Shadow_
- Level 4 - Modals - _White w/Lightbox_
- Level 5 - Toasts - _White w/Shadow + Message Color_

##### Interactivity

Within each aforementioned depth level is an interactive color hierarchy that further organizes content while communicating an order of importance for interactive elements. This interactive color hierarchy subtly influences the user's attention and nudges their focus.

1. Primary - _`$interactive-primary`_
   - Core interactive elements (typically buttons) for achieving the primary task(s) in the UI
   - Fill - Most important
   - Stroke - Important
1. Secondary - _`$interactive-secondary`_
   - Supporting interactive elements (various controls) that assist the primary task(s) in the UI
   - Fill - Most important
     - Can be used for selected state (typically delegated to stroke) for grouped buttons (examples usage seen in Transform defaults)
   - Stroke - Important
     - Denotes the states of selected, active, and/or valid where grey represents the opposites unselected, inactive, and/or invalid
1. Tertiary - _Greyscale_
   - Typically white buttons and other useful controls that aren't core or are in support of the primary task(s) in the UI
1. Navigation - _`$interactive-navigation`_
   - Denotes navigation and sub-navigation interactive elements as distinct from primary and secondary task colors

After the primary, secondary, tertiary, or navigation decision is made, the button size decision is informed by:

1. Use the default button size
1. Use the `is-small` modifier if it is within a component that can have multiple instances

#### Markup Hierarchy

There are three fundamental markup groups in the codebase. All three are technically VueJS single-file components but each have an intended use:

1. Views (top-level "pages" and "page containers" that map to parent routes)
2. Sub-views (nested "pages" of "page containers" that map to child routes)
3. Components (widgets that are potentially reusable across parent and child routes)

Here is a technical breakdown:

1. Views - navigation, signage, and sub-navigation
   - Navigation and breadcrumbs are adjacent to the main view
   - Use `<router-view-layout>` as root with only one child for the main view:
     1. `<div class="container view-body">`
        - Can expand based on task real-estate requirements via `is-fluid` class addition
   - Reside in the `src/views` directory
2. Sub-views - tasks
   - Use `<section>` as root (naturally assumes a parent of `<div class="container view-body">`) with one type of child:
     - One or more `<div class="columns">` each with their needed `<div class="column">` variations
   - Reside in feature directory (ex. `src/components/analyze/AnalyzeModels`)
3. Components - task helpers
   - Use Vue component best practices
   - Reside in feature or generic directory (ex. `src/components/analyze/ResultTable` and `src/components/generic/Dropdown`)

### Merge Requests

:::tip Searching for something to work on?
Start off by looking at our [~"Accepting Merge Requests"][accepting merge requests] label.

Keep in mind that this is only a suggestion: all improvements are welcome.
:::

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer may approve the merge request or send it back for further iteration
1. Once approved, the merge request can be merged by any Meltano maintainer

#### Reviews

A contributor can ask for a review on any merge request, without this merge request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the merge request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a merge request without feedback, unless specified by the reviewer.

### Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

#### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.

### Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

#### Why Tmuxinator?

In order to run applications, you need to run multiple sessions and have to do a lot of repetitive tasks (like sourcing your virtual environments). So we have created a way for you to start and track everything in its appropriate panes with a single command.

1. Start up Docker
1. Start Meltano API
1. Start the web app

It's a game changer for development and it's worth the effort!

#### Requirements

1. [tmux](https://github.com/tmux/tmux) - Recommended to install with brew
1. [tmuxinator](https://github.com/tmuxinator/tmuxinator)

This config uses `$MELTANO_VENV` to source the virtual environment from. Set it to the correct directory before running tmuxinator.

#### Instructions

1. Make sure you know what directory your virtual environment is. It is normally `.venv` by default.
1. Run the following commands. Keep in mind that the `.venv` in line 2 refers to your virtual environment directory in Step #1.

```bash
cd path/to/meltano
MELTANO_VENV=.venv tmuxinator local
```

#### Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)

[Accepting Merge Requests]: https://gitlab.com/groups/meltano/-/issues?label_name[]=Accepting%20Merge%20Requests

## Architecture

### Meltano Model

Meltano Models allow you to define your data model and interactively generate SQL so that you can easily analyze and visualize it in Meltano UI.

An _analysis model_ is an interchangeable term for _meltano model_.

#### Concepts

Below are definition for each concept used within a Meltano Model.

##### Topic

A `Topic` is a group of one or many `Designs` that determines how they will be mapped together.

A `Topic` can be identified by the naming schema: `<name>.topic.m5o` and should be stored in the `/model` directory.

##### Design

A `Design` maps multiple `Tables` together via `Joins` and represent the query context required for the actual analysis.

Each `Design` is also a `Source`, and thus can be refered to by the `Joins` it defines.

```
# defines a Design named `sample`
sample {
  from: table_name
  joins {
    # defines a Join named `join_a`
    join_a {
      from: table_a
      # we refer to the `Source's name` here
      sql_on: "sample.a_id = join_a.a_id"
    },
    …
  }
}
```

Designs are defined inside their corresponding `Topic` file.

##### Join

A `Join` represent the relationship between two `Sources`.

Each `Join` is also a `Source` so it can be refered to in by another `Join` defined in the same `Design`.

```
sample {
  from: table_name
  joins {
    join_a {
      from: table_a
      sql_on: "sample.a_id = join_a.a_id"
    },
    join_b {
      from: table_b
      # we can refer to `join_a` as it is defined in the same `Design`
      sql_on: "join_a.b_id = join_b.b_id"
    }
  }
}
```

##### Source

A `Source` is defined as something that refers to a `Table` in a `Design` context. It is crucial for `Designs` that refers to the same `Table` multiple times, because it serves as unique identifier for the scope of the query.

##### Table

A `Table` relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains `columns` and `aggregates` so you can select which you want to show.

A `Table` can be identified by the file naming schema: `<name>.table.m5o` and should be stored in the `/model` directory.

##### Aggregate

An `Aggregate` relates to a calculable column, via `count`, `sum`, `avg`, `min` or `max` (i.e., aggregate function definitions). These are limited to predefined methods with no custom SQL as well since custom SQL will be handled through transforms with dbt.

An `Aggregate` can be referred as an `Attribute` in a `Design` context.

##### Column

A `Column` relates directly to a column in a table of a database. Some limitations of this are that it will be limited to column only and no custom SQL.

A `Column` can be referred as an `Attribute` in a `Design` context.

#### Discover Available Models

To see what models are currently available in the Meltano ecosystem, run the following command:

```
meltano discover models
```

#### Add a Model

To add an existing model to your Meltano project, run the following command:

```
meltano add model [name_of_model]
```

#### Create a New Model

##### Setup

There are two foundational steps required for Meltano to extract, load, and transform your data for analysis in Meltano UI:

- Define each `Table` for a data source (as `<name>.table.m5o`)
- Define `Topics` for each analysis you want to run (as `<topic>.topic.m5o`)

##### Model Authoring (`.m5o` files)

The `.m5o` file extension is unique to Meltano but adheres to the [HOCON (Human-Optimized Config Object Notation) format](https://github.com/lightbend/config/blob/master/HOCON.md#hocon-human-optimized-config-object-notation). Below are example model files with comments to aid the authoring of your `*.topic.m5o` and `*.table.m5o` files mentioned above.

###### Example `carbon.topic.m5o` file

```bash
# Define a database, connection settings, and the table relationships (further defined in each `my-table.table.m5o` file) to inform Meltano how to connect for ELT, orchestration, and interactive SQL generation using the Meltano UI
{
  # Define version metadata
  version = 1
  # Define the name of the database used to denote automatically generated .m5oc for use by Meltano
  name = carbon
  # Define the extractor's namespace from which the data should be loaded
  plugin_namespace = tap_carbon
  # Define GUI label
  label = carbon intensity
  # Define base tables and their respective join relationships
  designs {
    # Define the base table(s) of interest (further defined in each my-table.table.m5o file) that will be GUI joinable and subsequently used for generating SQL queries
    region {
      # Define GUI label
      label = Region
      # Define from table name
      from = region
      # Define GUI description
      description = Region Carbon Intensity Data
      # Define joinable table(s) of this base table
      joins {
        # Define name of join table
        entry {
          # Define GUI label
          label = Entry
          # Define table columns of interest that will be GUI selectable and subsequently used for generating SQL queries
          fields = [entry.from, entry.to]
          # Define the SQL join condition
          sql_on = "region.id = entry.region_id"
          # Define join relationship
          relationship = one_to_one
        }
      }
    }
  }
}
```

###### Example `entry.table.m5o` file

```bash
# Define a database table for connecting to using Meltano's CLI and/or UI
{
  # Define the schema.table-name pattern used for connecting to a specific table in a database
  sql_table_name = gitlab.entry
  # Define the table name
  name = entry
  # Define the column(s) of interest that will be GUI selectable and subsequently used for generating SQL queries
  columns {
    # Define column name
    id {
      # Define GUI label
      label = ID
      # Define the primary key (only one per colums definition)
      primary_key = yes
      # Define GUI visibility
      hidden = yes
      # Define data type so ELT process properly updates the data warehouse
      type = string
      # Define the SQL that selects this column
      sql = "{{table}}.id"
    }
  }
  # Define time-based column(s) of interest that will be GUI selectable and subsequently used for generating SQL queries
  timeframes {
    from {
      label = From
      description = Selected from range in carbon data
      type = time
      # `part` refers to the DATE_PART SQL function:
      # https://www.postgresql.org/docs/8.1/functions-datetime.html#FUNCTIONS-DATETIME-EXTRACT
      periods = [{ name = week, label = Week, part = WEEK },
                 { name = month, label = Month, part = MONTH },
                 { name = year, label = Year, part = YEAR }]
      convert_tz = no
      sql = "{{TABLE}}.from"
    }
    to {
      label = To
      description = Selected to range in carbon data
      type = time
      # `part` refers to the DATE_PART SQL function:
      # https://www.postgresql.org/docs/8.1/functions-datetime.html#FUNCTIONS-DATETIME-EXTRACT
      periods = [{ name = week, label = Week, part = WEEK },
                 { name = month, label = Month, part = MONTH },
                 { name = year, label = Year, part = YEAR }]
      convert_tz = no
      sql = "{{TABLE}}.to"
    }
  }
}
```

With these files the Meltano CLI (or in conjunction with the Meltano UI) can properly extract, load, and transform your data for analysis using Meltano UI.

#### M5O Files

There are two types of `.m5o` files:

1. `.m5o` are user defined files that model the data in your database
2. `.m5oc` are compiled files generated from multiple `m5o` files

The `.m5o` files are based on the JSON-like HOCON syntax and serve as input for the compiled `.m5oc` files that Meltano then leverages.

#### Report

A `Report` is a saved state of selecting and analyzing a `Design`. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

A `Report` can be identified by the file naming schema: `<name>.report.m5o` and should be stored in the `/model` directory.

#### Dashboard

A `Dashboard` is a group of many `Reports`.

A `Dashboard` is identified by the file naming schema: `<name>.dashboard.m5o` and should be stored in the `/model` directory.

### Meltano UI

Meltano UI is a dashboard that allows you to interactively generate and run SQL queries to produce data visualizations, charts, and graphs based on your data.

### Meltano ELT

Meltano uses Singer Taps and Targets to Extract the data from various data sources and load them in raw format, i.e. as close as possible to their original format, to the Data Warehouse. Subsequently, the raw data is transformed to generate the dataset used for analysis and dashboard generation.

#### Taps

A `Tap` is an application that pulls data out of a data source by using the best integration for extracting bulk data.

For example, it takes data from sources like databases or web service APIs and converts them in a format that can be used for data integration or an ETL (Extract Transform Load) pipeline.

Meltano's `taps` is part of the Extractor portion of the data workflow and are based on the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

#### Targets

A `Target` is an application that has the responsibility of consuming data from `taps` and perform a task with it. Examples include loading it into a file (i.e., CSV), API, or database.

Meltano `targets` is part of the Loader portion of the data workflow.

#### Pipelines

Meltano can be used in any ELT architecture by using the right taps and targets for the job. The strategies supported can range from dumping the source data in a data lake to keeping all historical versions for each record to storing well formatted, clean data in the target data store.

When considering which taps and targets Meltano will maintain, some assumptions are followed concerning how source data is stored in the target data store:

- All extracted data is stored in the same Target Database, e.g., we use a Database named `RAW` for storing all extracted data to Snowflake.

- For each tap's data source, a schema is created for storing all the data that is extracted through a tap. E.g., The `RAW.SALESFORCE` schema is used for data extracted from Salesforce, and the `RAW.ZENDESK` schema is used for data extracted from Zendesk.

- Every stream generated from a tap will result in a table with the same name. That table will be created in the schema from that tap based on the information sent in the `SCHEMA` message.

- Meltano supports schema updates for when a schema of an entity changes during an extraction. This is enacted when Meltano receives more than one `SCHEMA` message for a specific stream in the same extract load run.

  When a SCHEMA message for a stream is received, our Targets check whether there is already a table for the entity defined by the stream.

  - If the schema for the tap does not exist, it is created.
  - If the table for the stream does not exist, it is created.
  - If a table does exist, our Targets create a diff to check if new attributes must be added to the table or already defined attributes should have their data type updated. Based on that diff, the Targets make the appropriate schema changes.

  Rules followed:

  1. Only support type upgrades (e.g., STRING -> VARCHAR) for existing columns.
  2. If an unsupported type update is requested (e.g., float --> int), then an exception is raised.
  3. Columns are never dropped. Only UPDATE existing columns or ADD new columns.

- Data is upserted when an entity has at least one primary key (key_properties not empty). If there is already a row with the same composite key (combination of key_properties) then the new record updates the existing one.

  No key_properties must be defined for a target to work on append-only mode. In that case, the target tables will store historical information with entries for the same key differentiated by their `__loaded_at` timestamp.

- If a timestamp_column attribute is not defined in the SCHEMA sent to the target for a specific stream, it is added explicitly. Each RECORD has the timestamp of when the target receives it as a value. As an example, `target-snowflake` sets the name of that attribute to `__loaded_at` when an explicit name is not provided in the target's configuration file.

  When a target is set to work on append-only mode (i.e. no primary keys defined for the streams), the timestamp_column's value can be used to get the most recent information for each record.

- For targets loading data to Relational Data Stores (e.g., Postgres, Snowflake, etc.), we unnest nested JSON data structures and follow a `[object_name]__[property_name]` approach similar to [what Stitch platform also does](https://www.stitchdata.com/docs/data-structure/nested-data-structures-row-count-impact).

- At the moment we do not deconstruct nested arrays. Arrays are stored as JSON or STRING data types (depending on the support provided by the target Data Store) with the relevant JSON representation stored as is. e.g. "['banana','apple']". It can then be extracted and used in the Transform Step.

#### Concurrency

The Singer spec doesn't define how to handle concurrency at the ELT level.

Making the streams concurrent themselves is pretty straightforward, but making sure the state handles concurrent updates is the real challenge, and also source specific.
Some sources supports pagination endpoints or a cursor-like API, but not all APIs are made equal.

Also depending on the data source, you might have some limit on how concurrent you can be, for example Salesforce limits to 25 concurrent request, but Netsuite allows only one query at a time per account.

For now, Meltano will try to implement concurrent taps when possible.

#### Job logging

Every time `meltano elt ...` runs, Meltano will keep track of the job and its success state in a log.

In Meltano UI, you can visit the Pipelines page and check the log of any past pipeline by clicking the `Log` button next to it. You can check the logs generated for running pipelines by clicking the `Running...` button:

![Screenshot of pipelines in the Schedules page](/images/getting-started-guide/gsg-05.png)

For example, the following screenshot shows the log of a completed pipeline:

![Screenshot of run log of a completed pipeline](/images/getting-started-guide/gsg-07.png)

All the output generated by `meltano elt ...` is logged in `.meltano/run/elt/{job_id}/{run_id}/elt.log`

Where `run_id` is a UUID autogenerated at each run and the `job_id` can be one of the following:

- The name of the pipeline created by Meltano UI; e.g. `pipeline-1571745262740`.
- The `job_id` provided to the `meltano elt ... [--job_id TEXT]` CLI command.
- It is autogenerated using the current date and time if it is not provided when the `meltano elt` CLI command runs.

#### How ELT Commands Fetch Dependencies

When you run ELT commands on a tap or target, this is the general process for fetching dependencies:

- First, the CLI looks in the project directory that you initialized
- Then it looks in the global file (`discovery.yml`) for urls of a package or repo
  - Note: This will eventually be moved into its own repository to prevent confusion since you cannot have local references for dependencies
- If this is the first time that the dependencies are requested, it will download to a local directory (if it is a package) or cloned (if it is a repo)
- By doing this, you ensure that packages are version controlled via `discovery.yml` and that it will live in two places:
  - in the project itself for the user to edit
  - in a global repo for meltano employees to edit

### Meltano Transformations

In order for data to be in a state where it can be used for generating reports and analyses, it is critical that they are standardized in order for calculations to be run on them. As a result, the data world has a concept of **transformations** which allow us to take a set of data and ensure that they are ready for analysis.

For example, if we have a simple CSV with a column of data for the sale amount for the day.

```
sales
-----
$21.00
$42.48
$100
$96.28
```

It may not be immediately obvious, but when this data is migrated to a database, it is typically converted as a string in order to include the dollar symbol. However, while the formatting is useful for knowing that field represents a currency, this prevents us from performing calculations like average, median, or mean.

As a result, we need to run transformations on our data to the proper data type while also ensuring the data is clean. In other words, we'd like our data to look like this:

```
sales
-----
21
42.48
100
96.28
```

#### Transformation Methodology: dbt

Meltano uses [dbt](https://docs.getdbt.com/) to transform the source data into the `analytics` schema, ready to be consumed by models.

To get started using [dbt](https://docs.getdbt.com/docs/introduction), you need to have some knowledge of [SQL](https://en.m.wikipedia.org/wiki/SQL) since this is how you will write your transformations to take raw data into data that's ready for analytics.

For more information on how to use dbt, check out the [official dbt documentation site for how it works](https://docs.getdbt.com/docs/introduction).

And for a guided tutorial on how to create custom transforms, check out our [Create Custom Transforms and Models tutorial](https://www.meltano.com/tutorials/create-custom-transforms-and-models.html)!

##### Python scripts

In certain circumstances transformations cannot be done in dbt (like API calls), so we use python scripts for these cases.

#### Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.

##### Loading a CSV:

> Notes:
>
> - The naming format for the `FILES` must be `<schema>.<table>.csv`. This pattern is required and will be used to create/update the table in the DW.
> - Multiple `FILES` can be used, use spaces to separate.

- Start the cloud sql proxy
- Run the command:

```
python3 elt/util/spreadsheet_loader.py csv FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

##### Loading a Google Sheet:

> Notes:
>
> - Each `FILES` will be located and loaded based on its name. The names of the sheets shared with the runner must be unique and in the `<schema>.<table>` format
> - Multiple `FILES` can be used, use spaces to separate.

- Share the sheet with the required service account (if being used in automated CI, use the runner service account)
- Run the command:

```
python3 elt/util/spreadsheet_loader.py sheet FILES...
```

- Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

##### Further Usage Help:

- Run the following command(s) for additional usage info `python3 elt/util/spreadsheet_loader.py <csv|sheet> -- --help`

#### Access Control

Meltano manages authorization using a role based access control scheme.

- Users have multiple roles;
- Roles have multiple permissions;

A Permission has a context for with it is valid: anything that matches the context is permitted.

### Meltano UI in Production

Meltano UI consist of a Flask API and a Vue.js front-end application, which are both included in the `meltano` package. In other words, the Flask API is not exposed at a project level and any customizations needed must be done at the package level.

To run Meltano in production, we recommend using [gunicorn](http://docs.gunicorn.org/en/stable/install.html) for setting up your HTTP Server.

First, install gunicorn:

```bash
pip3 install gunicorn
```

You can then start Meltano UI:

::: warning Note
This is an example invocation of gunicorn, please refer to
the [gunicorn documentation](http://docs.gunicorn.org/en/stable/settings.html) for more details.
:::

Start gunicorn with 4 workers, alternatively you can use `$(nproc)`:

```bash
gunicorn -c python:meltano.api.wsgi.config -w 4 meltano.api.wsgi:app
```
