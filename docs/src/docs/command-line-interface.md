---
metaTitle: Using the Meltano CLI
description: The Meltano command line interface makes it easy to develop, run, and debug every step of the data analysis lifecycle.
sidebarDepth: 2
---

# CLI reference

Meltano provides a command line interface (CLI) that allows you to manage the configuration and orchestration of Meltano projects. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

## `add`

`meltano add` lets you add [plugins](/docs/plugins.html) to your Meltano project.

Specifically, it will:
1. add the plugin to your project's `meltano.yml` file under `plugins: <type>s:`, e.g. `plugins: extractors:`,
2. create a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for the plugin at `.meltano/<type>s/<name>/venv`, e.g. `.meltano/extractors/tap-gitlab/venv`, and
3. install the plugin's [pip package](https://pip.pypa.io/en/stable/) into the virtual environment using `pip install <pip_url>`.

(Some plugin types have slightly different or additional behavior; refer to the [plugin type documentation](/docs/plugins.html) for more details.)

Once the plugin has been added to your project, you can configure it using [`meltano config`](#config),
invoke its executable using [`meltano invoke`](#invoke), and use it in a pipeline using [`meltano elt`](#elt).

### How to use: Known plugins

Plugins that are already [known to Meltano](/docs/contributor-guide.html#known-plugins) will show up when you run [`meltano discover`](#discover),
and can be added to your project by simply specifying their `type` and `name`:

```bash
meltano add <type> <name>
meltano add extractor <name>
meltano add loader <name>
meltano add transform <name>
meltano add model <name>
meltano add dashboard <name>
meltano add orchestrator <name>
meltano add transformer <name>
meltano add files <name>

# For example:
meltano add extractor tap-gitlab
meltano add loader target-postgres
```

An `--include-related` flag can be passed to automatically install all transform, model, and dashboard plugins related to an extractor:

```bash
meltano add --include-related extractor tap-gitlab
```

### How to use: Custom plugins

Plugins that Meltano isn't familiar with yet, like arbitrary Singer taps and targets, can be added using the `--custom` flag:

```bash
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19
meltano add --custom loader pipelinewise-target-postgres
```

Since no additional metadata about this plugin will be known to Meltano yet,
it will ask you some additional questions to learn where the plugin's package can be found,
how to interact with it, and how it can be expected to behave: (Note that more context is provided in the actual command prompts.)

```bash
$ meltano add --custom extractor tap-covid-19
# Specify namespace, which will serve as the:
# - prefix for configuration environment variables
# - identifier to find related/compatible plugins
# - default value for the `schema` setting when used
#   with loader target-postgres or target-snowflake
(namespace): tap_covid_19

# Specify `pip install` argument, for example:
# - PyPI package name:
(pip_url): tap-covid-19
# - Git repository URL:
(pip_url): git+https://github.com/singer-io/tap-covid-19.git
# - local directory, in editable/development mode:
(pip_url): -e extract/tap-covid-19

# Specify the package's executable name
(executable): tap-covid-19

# Specify supported Singer features (executable flags)
(capabilities): catalog,discover,state

# Specify supported settings (`config.json` keys)
(settings): api_token,user_agent,start_date
```

If you're adding a Singer tap or target that's listed on Singer's [index of taps](https://www.singer.io/#taps) or [targets](https://www.singer.io/#targets), simply providing the package name as `name`, `pip_url`, and `executable` should suffice. If it's a tap or target you have developed or are developing yourself, you'll want to set `pip_url` to either a Git repository URL or local directory path. If you add the `-e` flag ahead of the local path, the package will be installed in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).

To find out what `settings` a tap or target supports, reference its README and/or documentation. If the `capabilities` (executable flags) a tap supports are not described there, try [one of these tricks](/docs/contributor-guide.html#how-to-test-a-tap).

::: tip
Once you've successfully added your custom plugin to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!
:::

## `config`

Enables you to manage the [configuration](/docs/configuration.html) of Meltano itself or any of its plugins, as well as [plugin extras](#how-to-use-plugin-extras).

When no explicit `--store` is specified, `meltano config <plugin> set` will automatically store the value in the [most appropriate location](/docs/configuration.html#configuration-layers):
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
meltano config <plugin> list

# View the plugin's current configuration.
meltano config <plugin>

# Sets the configuration's setting `<name>` to `<value>`.
meltano config <plugin> set <name> <value>

# Values are parsed as JSON, and interpreted as simple strings when invalid
meltano config <plugin> set <name> <string>             # String with no meaning in JSON
meltano config <plugin> set <name> "<word> <word> ..."  # Multi-word string with no meaning in JSON
meltano config <plugin> set <name> <json>               # JSON that fits in a single word
meltano config <plugin> set <name> '<json>'             # JSON in a string argument
meltano config <plugin> set <name> '"<string>"'         # JSON string
meltano config <plugin> set <name> <number>             # JSON number, e.g. 100 or 3.14
meltano config <plugin> set <name> <true/false>         # Boolean True or False
meltano config <plugin> set <name> '[<elem>, ...]'      # Array
meltano config <plugin> set <name> '{"<key>": <value>, ...}' # JSON object

# Remove the configuration's setting `<name>`.
meltano config <plugin> unset <name>

# Clear the configuration (back to defaults).
meltano config <plugin> reset

# Set, unset, or reset in a specific location
meltano config <plugin> set --store=meltano_yml <name> <value> # set in `meltano.yml`
meltano config <plugin> unset --store=dotenv <name> # unset in `.env`
meltano config <plugin> reset --store=db # reset in system database
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano config --plugin-type=<type> <plugin> ...
```

#### Nested properties

Nested properties can be set (and unset) by specifying a list of property names:

```bash
meltano config <plugin> set <property> <subproperty> <value>
meltano config <plugin> set <property> <deep> <nesting> <value>

meltano config <plugin> unset <property> <subproperty>
```

This will result in the following configuration being passed on to the plugin:

```json
{"<property>": {"<subproperty>": "<value>", "<deep>": {"<nesting>": "<value>"}}}
```

##### Dot seperator

Note that `meltano config <plugin> list` always displays full config keys
with nesting represented by the `.` seperator, matching the internal flattened representation:

```bash
meltano config <plugin> list
# => <property>.<subproperty>
# => <property>.<deep>.<nesting>
```

You can also set nested properties using the `.` seperator, but specifying a list of names is preferred
since this will result in the nesting being reflected in the plugin's `config` object in `meltano.yml`:

```bash
meltano config <plugin> set <property> <deep> <nesting> <value>
# `meltano.yml`:
#  config:
#    <property>:
#      <deep>:
#        <nesting>: <value>

meltano config <plugin> set <property>.<deep>.<nesting> <value>
# `meltano.yml`:
#  config:
#    <property>.<deep>.<nesting>: <value>
```

### How to use: Plugin extras

In the context of `meltano config`, [plugin extras](/docs/configuration.html#plugin-extras) are distinguished from regular plugin-specific settings using an underscore (`_`) prefix, e.g. `_example_extra`. This also applies in the environment variables that can be used to override them at runtime: since setting names for extras are prefixed with underscores (`_`), they get an extra underscore to separate them from the plugin namespace, e.g. `TAP_EXAMPLE__EXAMPLE_EXTRA`.

By default, `meltano config <plugin>` and `meltano config <plugin> list` only take into account regular plugin settings.
An `--extras` flag can be passed to view or list only extras instead.

Be aware that `meltano config <plugin> reset` resets both regular settings _and_ extras.

```bash
# List all extras for the specified plugin with their names,
# environment variables, and current values
meltano config <plugin> list --extras

# View the plugin's current extras
meltano config --extras <plugin>

# Set value of extra `<extra>` to `<value>` through the `_<extra>` setting
meltano config <plugin> set _<extra> <value>

# Unset extra `<extra>`
meltano config <plugin> unset _<extra>

# Reset regular settings _and_ extras
meltano config <plugin> reset
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

This allows you to run your ELT pipeline to Extract, Load, and Transform data using an extractor and loader of your choosing,
and optional transformations.

To allow subsequent pipeline runs with the same extractor/loader/transform combination to pick up right where the previous run left off,
each ELT run has a Job ID that is used to store and look up the incremental [pipeline state](/docs/integration.html#pipeline-state) in the [system database](/docs/production.html#storing-metadata). If no stable identifier is provided using the `--job_id` flag or the `MELTANO_JOB_ID` environment variable, extraction will always start from scratch and a one-off Job ID is automatically generated using the current date and time.

All the output generated by this command is also logged in `.meltano/run/elt/{job_id}/{run_id}/elt.log`. The `run_id` is a UUID autogenerated at each run.

### How to use

```bash
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--job_id TEXT] [--dry]
```

#### Parameters

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

- The `--job_id` flag identifies related EL(T) runs when storing and looking up [pipeline state](/docs/integration.html#pipeline-state).

- A `--full-refresh` flag can be passed to perform a full refresh, ignoring state left behind by any previous runs with the same job ID.

#### Examples

```bash
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres
```

### Debugging

If extraction, loading, or transformation is failing, or otherwise not behaving as expected,
you can learn more about what's going on behind the scenes by setting Meltano's
[`cli.log_level` setting](/docs/settings.html#cli-log-level) to `debug`,
using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI flag:

```bash
MELTANO_CLI_LOG_LEVEL=debug meltano elt ...

meltano --log-level=debug elt ...
```

In debug mode, `meltano elt` will log the arguments and environment used to invoke the Singer tap and target executables (and `dbt`, when running transformations), including the paths to the generated config, catalog, and state files, for you to review:

```bash
$ meltano --log-level=debug elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl
meltano            | INFO Running extract & load...
meltano            | INFO Found state from 2020-08-05 21:30:20.487312.
meltano            | DEBUG Invoking: ['demo-project/.meltano/extractors/tap-gitlab/venv/bin/tap-gitlab', '--config', 'demo-project/.meltano/run/tap-gitlab/tap.config.json', '--state', 'demo-project/.meltano/run/tap-gitlab/state.json']
meltano            | DEBUG Env: {'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2020-05-01'}
meltano            | DEBUG Invoking: ['demo-project/.meltano/loaders/target-jsonl/venv/bin/target-jsonl', '--config', 'demo-project/.meltano/run/target-jsonl/target.config.json']
meltano            | DEBUG Env: {'MELTANO_EXTRACTOR_NAME': 'tap-gitlab', 'MELTANO_EXTRACTOR_NAMESPACE': 'tap_gitlab', 'MELTANO_EXTRACT_API_URL': 'https://gitlab.com', 'MELTANO_EXTRACT_PRIVATE_TOKEN': '', 'MELTANO_EXTRACT_GROUPS': '', 'MELTANO_EXTRACT_PROJECTS': 'meltano/meltano', 'MELTANO_EXTRACT_ULTIMATE_LICENSE': 'False', 'MELTANO_EXTRACT_START_DATE': '2020-05-01', 'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2020-05-01', 'TARGET_JSONL_DESTINATION_PATH': 'output', 'TARGET_JSONL_DO_TIMESTAMP_FILE': 'False'}
```

Additionally, all [Singer messages](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#output) output by the tap and target will be logged, identified by `<plugin name> (out)` prefixes:

```
tap-gitlab         | INFO Starting sync
tap-gitlab (out)   | {"type": "SCHEMA", "stream": "projects", "schema": {"type": "object", "properties": {...}}, "key_properties": ["id"]}
tap-gitlab (out)   | {"type": "RECORD", "stream": "projects", "record": {"id": 7603319, "name": "Meltano", ...}, "time_extracted": "2020-08-05T21:30:22.988250Z"}
tap-gitlab (out)   | {"type": "STATE", "value": {"project_7603319": "2020-08-05T21:04:59.158000Z"}}
tap-gitlab         | INFO Sync complete
target-jsonl (out) | {"project_7603319": "2020-08-05T21:04:59.158000Z"}
meltano            | INFO Incremental state has been updated at 2020-08-05 21:30:26.669170.
meltano            | DEBUG Incremental state: {'project_7603319': '2020-08-05T21:04:59.158000Z'}
meltano            | INFO Extract & load complete!
```

## `init`

Used to create a new Meltano project directory inside the current working directory.

The new project directory will contain:

- a `meltano.yml` file that will list any [`plugins` you'll add](/docs/plugin-management.html#adding-extractors-and-loaders-to-your-project) and [pipeline `schedules` you'll create](/#orchestration),
- stubs for `.gitignore`, `README.md`, and `requirements.txt` for you to edit (or delete) as appropriate, and
- empty `model`, `extract`, `load`, `transform`, `analyze`, `notebook`, and `orchestrate` directories for you to use (or delete) as you please.

The [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats) will be enabled by default, unless the `--no_usage_stats` flag is provided or the `MELTANO_DISABLE_TRACKING` environment variable is enabled.

### How to use

```bash
# Format
meltano init [project_name] [--no_usage_stats]
```

#### Parameters

- **project_name** - This determines the folder name for the project

#### Options

- **no_usage_stats** - This flag disables the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats).

#### Examples

```bash
# Initialize a new Meltano project in the
# "demo-project" directory, and...
# - share anonymous usage data with the Meltano team
#   to help them gauge interest in Meltano and its
#   features and drive development time accordingly:
meltano init demo-project
# - OR don't share anything with the Meltano team
#   about this specific project:
meltano init demo-project --no_usage_stats
# - OR don't share anything with the Meltano team
#   about any project I initialize ever:
SHELLRC=~/.$(basename $SHELL)rc # ~/.bashrc, ~/.zshrc, etc
echo "export MELTANO_DISABLE_TRACKING=1" >> $SHELLRC
meltano init demo-project # --no_usage_stats is implied
```

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
meltano invoke <plugin> PLUGIN_ARGS...
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano invoke --plugin-type=<type> <plugin> PLUGIN_ARGS...
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

Selection rules will be stored in the extractor's [`select` extra](/docs/plugins.html#select-extra).

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
# List all available entities and attributes
meltano select --list --all tap-covid-19

# Include all attributes of an entity
meltano select tap-covid-19 eu_ecdc_daily "*"

# Include specific attributes of an entity
meltano select tap-covid-19 eu_daily date
meltano select tap-covid-19 eu_daily country
meltano select tap-covid-19 eu_daily cases
meltano select tap-covid-19 eu_daily deaths

# Exclude matching attributes of all entities
meltano select tap-covid-19 --exclude "*" "git_*"

# List selected (enabled) entities and attributes
meltano select --list tap-covid-19
```

Example output:

```
Enabled patterns:
    eu_ecdc_daily.*
    eu_daily.date
    eu_daily.country
    eu_daily.cases
    eu_daily.deaths
    !*.git_*

Selected attributes:
    [automatic] eu_daily.__sdc_row_number
    [automatic] eu_daily.git_path
    [selected ] eu_daily.date
    [selected ] eu_daily.country
    [selected ] eu_daily.cases
    [selected ] eu_daily.deaths
    [automatic] eu_ecdc_daily.__sdc_row_number
    [automatic] eu_ecdc_daily.git_path
    [selected ] eu_ecdc_daily.date
    [selected ] eu_ecdc_daily.datetime
    [selected ] eu_ecdc_daily.country
    [selected ] eu_ecdc_daily.cases
    [selected ] eu_ecdc_daily.deaths
```

::: tip
Most shells parse glob syntax: you must escape the special characters in the select pattern by quoting the pattern.
:::

### Exclude Parameter

Use `--exclude` to exclude all attributes that match the filter.

Attributes that are `automatic` are always included, even if they match an exclude pattern. Only attributes that are `available` can be excluded.

Exclusion has precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern first.

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
- Update files [managed by](/docs/plugins.html#update-extra) [file bundles](/docs/plugins.html#file-bundles)
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
