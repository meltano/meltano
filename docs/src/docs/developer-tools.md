# Developer Tools

Meltano is primarily offered to end-users as a hosted software-as-a-service (SaaS) solution for busy non-technical business owners looking to gain insights into their business data. However, we are also [an open source project](https://gitlab.com/meltano/meltano), and you have the option to [self-host Meltano](http://localhost:8080/docs/developer-tools.html#self-hosted-installation).

- [Self-Hosted Installation Guide](/docs/developer-tools.html#self-hosted-installation)
- [Upgrading Meltano Version](/docs/developer-tools.html#upgrading-meltano-version)
- [Command Line Interface](/docs/developer-tools.html#command-line-interface)
- [Environment Variables](/docs/developer-tools.html#environment-variables)
- [Role-Based Access Control](/docs/developer-tools.html#role-based-access-control-alpha)
- [Open Source Contributor Guide](/docs/developer-tools.html#contributor-guide)

## Self-Hosted Installation

This section provides guides for getting set up with a self-hosted instance of Meltano's open source data analytics software on your local computer or using popular hosting solutions:

- [Local Installation](/docs/developer-tools.html#local-installation)
- [Docker](/docs/developer-tools.html#installing-on-docker)
- Amazon Web Services (AWS)

::: tip
Are you trying Meltano for the first time? You can skip the installation process and we'll set you up with a free 30-day trial of Meltano as a hosted service. If you decide you want to switch to self-hosted later we can clone your instance so you can take it with you. [Sign up here.](https://meltano.typeform.com/to/NJPwxv)
:::

### Local Installation

In this section, we will install Meltano as an application you can access locally from your browser and on the command line. If you prefer to install to Docker, please view the installation instructions [here](/docs/installation.html#installing-on-docker).

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

Now that you have successfully installed Meltano and its requirements, you can create your first project.

#### Create your first project

To initialize a new project, open your terminal and navigate to the directory that you'd like to store your Meltano projects in.

Next, to create your project, you will use the `meltano init` command which takes a `PROJECT_NAME` that is of your own choosing. For this guide, let's create a project called "carbon."

::: info
Meltano shares anonymous usage data with the team through Google Analytics. This is used to help us learn about how Meltano is being used to ensure that we are making Meltano even more useful to our users.

If you would prefer to use Meltano without sending the team this data, learn how to configure this through our [environment variables docs](/docs/environment-variables.html#anonymous-usage-data).
:::

```bash
meltano init yourprojectname
```

This will create a new directory named `projectname` and initialize Meltano's basic directory structure inside it.

Inside the Meltano project directory, all plugin configuration (which may include tokens and passwords) is stored inside the `.meltano` directory,
which is automatically added to the project's `.gitignore` file to prevent this potentially sensitive information from accidentally being pushed up to a hosted Git repository.

### Setup your loader

At this time, the GUI for configuring the loader from your project has been temporarily disabled. As a result, you will need to supply your database configuration through a `.env` file.

Once you create the file, you will need to paste in the configuration for your database. For example, PostgreSQL configurations can [be found here](/loaders/postgres.html#intermediate-connecting-meltano-to-an-existing-postgresql-database).

After saving your configurations, you can load your configurations by running:

```bash
source .env
```

And just like that, your loader is configured!

### Start the application

Now that you've created your first Meltano project, let's change directory to our new project and start Meltano UI:

```bash
cd yourprojectname
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

You are now ready to add data sources, configure reporting databases, schedule updates and build dashboards!

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

### Troubleshooting Installation

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
