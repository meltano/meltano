---
metaTitle: Using the Meltano CLI
description: The Meltano command line interface makes it easy to develop, run, and debug every step of the data analysis lifecycle.
sidebarDepth: 2
lastUpdatedSignificantly: 2020-05-07
---

# Command Line Interface

Meltano provides a command line interface (CLI) that allows you to manage the configuration and orchestration of Meltano projects. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

## `add`

The `add` command allows you to add plugins to your Meltano project.

### Extractor / Loader

When you add an extractor or loader to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Install it into its own virtual environment in the `.meltano` directory using `pip3`

You can run `meltano add` with `--include-related` to automatically install all transform, model, and dashboard plugins related to an extractor.

#### Examples

```bash
# Extractor / Loader Template
meltano add [extractor | loader] [name_of_plugin]
meltano add [extractors | loaders] [name_of_plugin...]

# Extractor Example
meltano add extractor tap-gitlab
meltano add extractors tap-gitlab tap-google-analytics

# Extractor Example including related plugins
meltano add --include-related extractor tap-google-analytics

# Loader Example
meltano add loader target-postgres
```

### Transform

When you add a transform to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Update the dbt packages and project configuration

#### Example

```bash
# Transform Template
meltano add transform [name_of_transform]
meltano add transforms [name_of_transform...]
```

### Model

When you add a model to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Install the model inside the `.meltano` directory which is then available to use in the Meltano webapp  file to help you interactively generate SQL

#### Example

```bash
meltano add model [name_of_model]
meltano add models [name_of_model...]
```

### Dashboard

When you add a dashboard plugin to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Install the dashboard and reports inside the `analyze` directory which are then available to use in the Meltano webapp

#### Example

```bash
meltano add dashboard [name_of_dashboard]
meltano add dashboards [name_of_dashboard...]
```

### Orchestrator

When you add an orchestrator to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Install it into its own virtual environment in the `.meltano` directory using `pip3`
1. Install any related [file bundles](#file-bundle) to add orchestrator-specific files to your Meltano project

#### Example

```bash
meltano add orchestrator [name_of_orchestrator]
```

### Transformer

When you add an transformer to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml`
1. Install it into its own virtual environment in the `.meltano` directory using `pip3`
1. Install any related [file bundles](#file-bundle) to add transformer-specific files to your Meltano project

#### Example

```bash
meltano add transformer [name_of_transformer]
```

### File bundle

When you add a file bundle to a Meltano project, Meltano will:

1. Add the plugin to `meltano.yml` if any of the files it contains are managed by the file bundle and to be updated automatically when [`meltano upgrade`](#upgrade) is run.
2. Add the bundled files to your Meltano project

#### Example

```bash
meltano add files [name_of_file_bundle...]
```

## `config`

Enables you to manage the configuration of Meltano itself or any of its plugins.

Meltano uses configuration layers to resolve a plugin's configuration:

<!-- The following is reproduced from docs/src/README.md#meltano-config with minor edits. -->

1. **Environment variables**, set through your shell, a [`.env` file](https://github.com/theskumar/python-dotenv#usages) in your project directory, a [scheduled pipeline](#schedule)'s `env` object in `meltano.yml`, or any other method. You can use `meltano config <plugin> list` to list the available variable names.
2. **Your project's `meltano.yml` file**, under the plugin's `config` key.
   - Inside values, [environment variables](#pipeline-environment-variables) can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
3. **Your project's [**system database**](/docs/settings.html#database-uri)**, which lives at `.meltano/meltano.db` by default and (among other things) stores configuration set using [`meltano config <plugin> set`](#config) or [the UI](#ui) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. **The default `value`s** set on the plugin's `settings` object in the global `discovery.yml` file (in the case of [known plugins](/docs/contributor-guide.html#known-plugins)) or your project's `meltano.yml` file (in the case of custom plugins). `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in your project's `meltano.yml` file and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, a (`.gitignore`d) `.env` file in your project directory, or the system database.

When no explicit `--store` is specified, `meltano config <plugin> set` will automatically store the value in the most appropriate location:
- the system database, if the project is [deployed as read-only](/docs/settings.html#project-readonly);
- the current location, if a setting's default value has already been overwritten;
- `.env`, if a setting is sensitive or environment-specific (defined as `kind: password` or `env_specific: true`);
- `meltano.yml` otherwise.

### How to use

To manage the configuration of Meltano itself, specify `meltano` as the plugin name.

```bash
# List all settings for Meltano itself with their names,
# environment variables, and current values
meltano config meltano list

# List all settings for the specified plugin with their names,
# environment variables, and current values
meltano config <plugin_name> list

# View the plugin's current configuration.
meltano config <plugin_name>

# Sets the configuration's setting `<name>` to `<value>`.
meltano config <plugin_name> set <name> <value>

# Remove the configuration's setting `<name>`.
meltano config <plugin_name> unset <name>

# Clear the configuration (back to defaults).
meltano config <plugin_name> reset

# Set, unset, or reset in a specific location
meltano config <plugin_name> set --store=meltano_yml <name> <value> # set in `meltano.yml`
meltano config <plugin_name> unset --store=dotenv <name> # unset in `.env`
meltano config <plugin_name> reset --store=db # reset in system database
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano config --plugin-type=<plugin_type> <plugin_name> ...
```

#### Nested properties

Nested properties can be set (and unset) by specifying a list of property names:

```bash
meltano config <plugin_name> set <property> <subproperty> <value>
meltano config <plugin_name> set <property> <deep> <nesting> <value>

meltano config <plugin_name> unset <property> <subproperty>
```

This will result in the following configuration being passed on to the plugin:

```json
{"<property>": {"<subproperty>": "<value>", "<deep>": {"<nesting>": "<value>"}}}
```

##### Dot seperator

Note that `meltano config <plugin_name> list` always displays full config keys
with nesting represented by the `.` seperator, matching the internal flattened representation:

```bash
meltano config <plugin_name> list
# => <property>.<subproperty>
# => <property>.<deep>.<nesting>
```

You can also set nested properties using the `.` seperator, but specifying a list of names is preferred
since this will result in the nesting being reflected in the plugin's `config` object in `meltano.yml`:

```bash
meltano config <plugin_name> set <property> <deep> <nesting> <value>
# `meltano.yml`:
#  config:
#    <property>:
#      <deep>:
#        <nesting>: <value>

meltano config <plugin_name> set <property>.<deep>.<nesting> <value>
# `meltano.yml`:
#  config:
#    <property>.<deep>.<nesting>: <value>
```

### Singer metadata

On extractors (Singer taps), [stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
can be configured using special [nested properties](#nested-properties) `metadata.<entity>.<key>` and `metadata.<entity>.<attribute>.<key>`,
where `<entity>` refers to a stream's `tap_stream_id` value, and `<attribute>` to one of the stream's properties.

Like [`meltano select`](#select) rules, metadata rules allow for [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like
patterns in the entity and attribute identifiers.

```bash
meltano config <plugin_name> set metadata <entity> <key> <value>
meltano config <plugin_name> set metadata <entity> <attribute> <key> <value>

# For example:
meltano config tap-postgres set metadata "some_schema-*" replication-method INCREMENTAL
meltano config tap-postgres set metadata "some_schema-*" replication-key created_at

meltano config tap-postgres set metadata some_schema-some_table some_column custom-metadata custom-value
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
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--job_id TEXT] [--dry]
```

### Parameters

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

- A `--full-refresh` flag can be passed to perform a full refresh, ignoring the state left behind by any previous runs with the same job ID.

### Pipeline environment variables

To allow loaders and transformers to adapt their configuration and behavior based on the extractor and loader they are run with,
`meltano elt` dynamically sets a number of pipeline-specific environment variables before compiling their configuration and invoking their executables.

In addition to variables set through the environment or a `.env` file in your project directory, the following variables describing the extractor are available to loaders _and_ transformers:

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

Installs dependencies of your project based on the **meltano.yml** file.

Optionally, provide a plugin type argument to only (re)install plugins of a certain type.
Additionally, plugin names can be provided to only (re)install those specific plugins.

Use `--include-related` to automatically install transform, model, and dashboard plugins related to installed extractor plugins.

### How to Use

```bash
meltano install

meltano install extractors
meltano install extractor tap-gitlab
meltano install extractors tap-gitlab tap-adwords

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

## `schedule`

::: tip
An `orchestrator` plugin is required to use `meltano schedule`: refer to the [Orchestration](/docs/orchestration.html) documentation to get started with Meltano orchestration.
:::

Use the `schedule` command to define ELT pipelines to be run by an orchestrator at regular intervals. These scheduled pipelines will be added to your project's `meltano.yml`.

### How to use

The interval argument can be a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression) or one of the following presets:
`@hourly` (`0 * * * *`), `@daily` (`0 0 * * *`), `@weekly` (`0 0 * * 0`), `@monthly` (`0 0 1 * *`), `@yearly` (`0 0 1 1 *`), or `@once` (for schedules to be triggered manually through the UI).

```bash
# Add a schedule
meltano schedule <schedule_name> <extractor> <loader> <interval> [--transform={run,skip,only}]

# List all schedules
meltano schedule list [--format=json]
```

### Examples

```bash
meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily --transform=run
# This specifies that the following command is to be run once a day:
# meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

meltano schedule gitlab-to-jsonl tap-gitlab target-jsonl "* * * * *"
# This specifies that the following command is to be run every minute:
# meltano elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl
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

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

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

Generate secrets for the [`ui.secret_key`](/docs/settings.html#ui-secret-key)
and [`ui.password_salt`](/docs/settings.html#ui-password-salt) settings, that
will be stored in a `.env` file in your project directory along with the
specified value for the [`ui.server_name` setting](/docs/settings.html#ui-server-name).

In production, you will likely want to move these settings to actual environment variables, since `.env` is in `.gitignore` by default.

::: warning
Regenerating secrets will cause the following:

  - All passwords will be invalid
  - All sessions will be expired

Use with caution!
:::

#### How to use

The `--bits` flag can be used to specify the size of the secrets, default to 256.

```bash
# Format
meltano ui setup [--bits=256] <server_name>

meltano ui setup meltano.example.com
```

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

When called without arguments, this will:
- Upgrade the `meltano` package
- Update files managed by [file bundles](#file-bundle)
- Apply migrations to system database
- Recompile models

### How to use

```bash
meltano upgrade
meltano upgrade --skip-package # Skip upgrading the Meltano package

meltano upgrade package # Only upgrade Meltano package
meltano upgrade files # Only update files managed by file bundles
meltano upgrade database # Only apply migrations to system database
meltano upgrade models # Only recompile models
```

## `version`

It is used to check which version of Meltano currently installed.

### How to use

```bash
meltano --version
```
