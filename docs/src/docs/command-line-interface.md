---
metaTitle: Using the Meltano CLI
description: The Meltano command line interface makes it easy to develop, run, and debug every step of the data analysis lifecycle.
sidebarDepth: 2
lastUpdatedSignificantly: 2020-05-07
---

# Command Line Interface

Meltano provides a command line interface (CLI) that allows you to manage the configuration and orchestration of Meltano instances. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

## `add`

The `add` command allows you to add an extractor, loader, or transform to your Meltano instance.

### Extractor / Loader

When you add a extractor or loader to a Meltano instance, Meltano will:

1. Add it to the `meltano.yml` file
1. Install it in the `.meltano` directory with `venv` and `pip3`

You can run `meltano add` with `--include-related` to automatically install all transform, model, and dashboard plugins related to an extractor.

#### Examples

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

### Transform

When you add a transform to a Meltano instance, Meltano will:

1. Install dbt transformer to enable transformations (if needed)
1. Add transform to `meltano.yml file`
1. Update the dbt packages and project configuration

#### Example

```bash
# Transform Template
meltano add [transform] [name_of_transform]
```

### Model

When you add a model to a Meltano instance, Meltano will:

1. Add a model bundle to your `meltano.yml` file to help you interactively generate SQL
1. Install the model inside the `.meltano` directory which is then available to use in the Meltano webapp

#### Example

```bash
meltano add model [name_of_model]
```

### Dashboard

When you add a dashboard to a Meltano instance, Meltano will:

1. Add a dashboard bundle to your `meltano.yml` file
1. Install the dashboard and reports inside the `analyze` directory which are then available to use in the Meltano webapp

#### Example

```bash
meltano add dashboard [name_of_dashboard]
```

### Orchestration

When you add an orchestrator to a Meltano instance, Meltano will:

1. Add an orchestrator plugin to your **meltano.yml**
1. Install it

#### Example

```bash
meltano add orchestrator [name_of_orchestrator]
```

## `config`

Enables you to change a plugin's configuration.

Meltano uses configuration layers to resolve a plugin's configuration:

1. Environment variables
1. Plugin's `config` attribute in **meltano.yml**, set manually or using `meltano config <plugin_name> set`. Inside values, [environment variables](#pipeline-environment-variables) can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
1. System database, which holds settings set via the UI or `meltano config <plugin_name> set --store=db`
1. Default values set in the setting definition in **discovery.yml**

::: info
Sensitive settings such as _passwords_ or _keys_ should not be stored in `meltano.yml`,
since the entire contents of this file are available to the Meltano UI and its users.

Instead, these sensitive values should be stored in environment variables or the system database.

You can use `meltano config <plugin_name> list` to find the environment variable associated with a setting.

Note that in each of these cases, Meltano stores the configuration as-is, without encryption.
:::

### How to use

```bash
# Displays the plugin's configuration.
meltano config <plugin_name>

# List the available settings for the plugin.
meltano config <plugin_name> list

# Sets the configuration's setting `<name>` to `<value>`.
meltano config <plugin_name> set <name> <value> # store in `meltano.yml`
meltano config <plugin_name> set --store=db <name> <value> # store in system database

# Remove the configuration's setting `<name>`.
meltano config <plugin_name> unset <name> # remove from `meltano.yml`
meltano config <plugin_name> unset --store=db <name> # remove from system database

# Clear the configuration (back to defaults).
meltano config <plugin_name> reset # remove from `meltano.yml`
meltano config <plugin_name> reset --store=db # remove from system database
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano config --plugin-type=<plugin_type> <plugin_name> ...
```

## `discover`

Lists the available plugins you are interested in.

### How to Use

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

## `elt`

This allows you to run your ELT pipeline to Extract, Load, and Transform the data with configurations of your choosing:

1. The `job_id` is autogenerated using the current date and time if it is not provided (via `--job_id` or `$MELTANO_JOB_ID`)
1. The `run_id` is a UUID autogenerated at each run
1. All the output generated by this command is also logged in `.meltano/run/elt/{job_id}/{run_id}/elt.log`

### How to use

```bash
meltano elt <extractor> <loader> [--job_id TEXT] [--transform run] [--dry]
```

### Parameters

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

### Pipeline environment variables

To allow loaders and transformers to adapt their configuration and behavior based on the extractor and loader they are run with,
`meltano elt` dynamically sets a number of pipeline-specific environment variables before compiling their configuration and invoking their executables.

In addition to variables set through the environment or your project's `.env` file, the following variables describing the extractor are available to loaders _and_ transformers:

- `MELTANO_EXTRACTOR_NAME`: the extractor's `name`, e.g. `tap-gitlab`
- `MELTANO_EXTRACTOR_NAMESPACE`: the extractor's `namespace`, e.g. `tap_gitlab`
- `MELTANO_EXTRACT_<SETTING_NAME>`: one environment variable for each of the extractor's settings, e.g. `MELTANO_EXTRACT_PRIVATE_TOKEN` for the `private_token` setting
- `<SETTING_ENV>`: all of the extractor's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `TAP_GITLAB_API_URL` for the `api_url` setting

Additionally, the following variables describing the loader are available to transformers:

- `MELTANO_LOADER_NAME`: the loader's `name`, e.g. `target-postgres`
- `MELTANO_LOADER_NAMESPACE`: the loader's `namespace`, e.g. `postgres`
- `MELTANO_LOAD_<SETTING_NAME>`: one environment variable for each of the loader's settings, e.g. `MELTANO_LOAD_SCHEMA` for the `schema` setting
- `<SETTING_ENV>`: all of the loader's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `PG_ADDRESS` for the `host` setting

Inside your loader or transformer's `config` object in `meltano.yml`, you can reference these (and other) environment variables as `$VAR` (as a single word) or `${VAR}` (inside a word). Inside your plugin, you can reference these through `os.environ` (if using Python) as usual.

This feature is used to dynamically configure the `target-postgres` and `target-snowflake` loaders and `dbt` transformer as appropriate, independent of the specific extractor and loader used:
- `target-postgres` and `target-snowflake` default value for `schema`: `$MELTANO_EXTRACTOR_NAMESPACE`, e.g. `tap_gitlab`
- `dbt` default value for `target`: `$MELTANO_LOADER_NAMESPACE`, e.g. `postgres` or `snowflake`, which correspond to the target names in `transform/profile/profiles.yml`
- `dbt` default value for `source_schema`: `$MELTANO_LOAD_SCHEMA`, e.g. `tap_gitlab`
- `dbt` default value for `models`: `$MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`, e.g. `tap_gitlab my_meltano_model`

### Examples

```bash
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres
```

## `init`

Used to create a new meltano project with a basic infrastructure in place in the current directory that the user is in.

### How to use

```bash
# Format
meltano init [project_name] [--no_usage_stats]
```

### Parameters

- **project_name** - This determines the folder name for the project

### Options

- **no_usage_stats** - This flag disables sending anonymous usage data when creating a new project.

## `install`

Installs all the dependencies of your project based on the **meltano.yml** file.

Optionally, provide a plugin type argument to only (re)install plugins of a certain type.

Use `--include-related` to automatically install transform, model, and dashboard plugins related to installed extractor plugins.

### How to Use

```bash
meltano install

meltano install extractors

meltano install models

meltano install --include-related
```

## `invoke`

Invoke the plugin's executable with specified arguments.

### How to use

```bash
meltano invoke <plugin_name> PLUGIN_ARGS...
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano invoke --plugin-type=<plugin_type> <plugin_name> PLUGIN_ARGS...
```

## `list`

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

## `schedule`

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

## `select`

Use the `select` command to add select patterns to a specific extractor in your Meltano project.

- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attributes for a specific tap.

::: warning
Not all taps support this feature. In addition, taps needs to support the `--discover` switch. You can use `meltano invoke tap-... --discover` to see if the tap supports it.
:::

### How to use

Meltano select patterns are inspired by the [glob](<https://en.wikipedia.org/wiki/Glob_(programming)>) syntax you might find in your operating system.

- `*`: matches any sequence of characters
- `?`: matches one character
- `[abc]`: matches either `a`, `b`, or `c`
- `[!abc]`: matches any character **but** `a`, `b`, or `c`

### Examples

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

### Exclude Parameter

Use `--exclude` to exclude all attributes that match the filter. Note

::: info
Attributes that are `automatic` are always included, even if they match an exclude pattern. Only attributes that are `available` can be excluded.
:::

::: info
Exclusion has precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern first.
:::

#### Examples

```bash
meltano select --exclude tap-carbon-intensity '*' 'longitude'
```

```bash
meltano select --exclude tap-carbon-intensity '*' 'latitude'
```

This will exclude all `longitude` and `latitude` attributes.

## `ui`

- `meltano ui`: Start the Meltano UI.

### `start` (default)

Start the Meltano UI.

### `setup`

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

#### --bits

Specify the size of the secrets, default to 256.

## `user`

::: tip
This command is only relevant when Meltano is run with authentication enabled.
:::

### `add`

Create a Meltano user account, active and ready to be used.

#### --overwrite, -f

Update the user instead of creating a new one.

#### --role, -G

Add the user to the role. Meltano ships with two built-in roles: `admin` and `regular`.

#### How to use

```bash
meltano user add admin securepassword --role admin
```

## `upgrade`

Upgrade Meltano and the Meltano project to the latest version.

## `version`

It is used to check which version of Meltano currently installed.

### How to use

```bash
meltano --version
```
