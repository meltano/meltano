---
description: Meltano provides a command line interface (CLI) that makes it easy to manage your project, plugins, and EL(T) pipelines.
---

# CLI Reference

Meltano provides a command line interface (CLI) that makes it easy to manage your [project](/docs/project.html), [plugins](/docs/plugin-management.html), and [EL(T) pipelines](/docs/integration.html).
To quickly find the `meltano` subcommand you're looking for, use the Table of Contents in the sidebar.
For a better understanding of command line documentation syntax, the [docopt](http://docopt.org/) standard is useful.

## `add`

`meltano add` lets you add [plugins](/docs/plugins.html#project-plugins) to your Meltano project.

Specifically, it will:
1. add a new [plugin definition](/docs/project.html#plugins) to your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) under `plugins: <type>s:`, e.g. `plugins: extractors:`, and
2. assuming a valid `pip_url` is specified, install the new plugin using [`meltano install <type> <name>`](#install), which will:
   1. create a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for the plugin inside the [`.meltano` directory](/docs/project.html#meltano-directory) at `.meltano/<type>s/<name>/venv`, e.g. `.meltano/extractors/tap-gitlab/venv`, and
   2. install the plugin's [pip package](https://pip.pypa.io/en/stable/) into the virtual environment using `pip install <pip_url>`.

(Some plugin types have slightly different or additional behavior; refer to the [plugin type documentation](/docs/plugins.html#types) for more details.)

Once the plugin has been added to your project, you can configure it using [`meltano config`](#config),
invoke its executable using [`meltano invoke`](#invoke), and use it in a pipeline using [`meltano elt`](#elt).

To learn more about adding a plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-a-plugin-to-your-project).

> Note: Unlike [`meltano install`](#install), this command installs plugins serially to avoid missing dependencies (e.g. a [`transform`](/docs/plugins#transforms) requires the [`dbt` plugin](/docs/transforms) to be installed first).

### How to use

The only required arguments are the new plugin's [type](/docs/plugins.html#types) and unique name:

```bash
meltano add <type> <name>

# For example:
meltano add extractor tap-gitlab
meltano add loader target-postgres
```

Without a `--custom` or `--inherit-from` option, this will add the
[discoverable plugin](/docs/plugins.html#discoverable-plugins) with the provided name
to your [`meltano.yml` project file](/docs/project.html#plugins)
using a [shadowing plugin definition](/docs/project.html#shadowing-plugin-definitions).

If multiple [variants](/docs/plugins.html#variants) of the discoverable plugin are available, the specific variant to add can be identified using the `--variant` option:

```bash
meltano add <type> <name> --variant <variant>

# For example:
meltano add loader target-postgres --variant transferwise
```

To add a [custom plugin](/docs/plugins.html#custom-plugins) using a [custom plugin definition](/docs/project.html#custom-plugin-definitions), use the `--custom` flag:

```bash
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19

# If you're using Docker, don't forget to mount the project directory,
# and ensure that interactive mode is enabled so that Meltano can ask you
# additional questions about the plugin and get your answers over STDIN:
docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom extractor tap-covid-19
```

To add a plugin [inheriting from](/docs/plugins.html#plugin-inheritance) an existing one using an [inheriting plugin definition](/docs/project.html#inheriting-plugin-definitions), use the `--inherit-from` option:

```bash
meltano add <type> <name> --inherit-from <existing-name>

# For example:
meltano add extractor tap-ga--client-foo --inherit-from tap-google-analytics
```

#### Parameters

- `--custom`: Add a [custom plugin](/docs/plugins.html#custom-plugins). The command will prompt you for the package's [base plugin description](/docs/plugins.html#project-plugins) metadata.

- `--inherit-from=<existing-name>`: Add a plugin [inheriting from](/docs/plugins.html#plugin-inheritance) an existing plugin in the project or a [discoverable plugin](/docs/plugins.html#discoverable-plugins) identified by name.

- `--as=<new-name>`: `meltano add <type> <name> --as=<new-name>` is equivalent to `meltano add <type> <new-name> --inherit-from=<name>`, and can be used to add a [discoverable plugin](/docs/plugins.html#discoverable-plugins) to your project with a different name.

- `--variant=<variant>`: Add a specific (non-default) [variant](/docs/plugins.html#variants) of the identified [discoverable plugin](/docs/plugins.html#discoverable-plugins).

- `--include-related`: Also add transform, dashboard, and model plugins related to the identified discoverable extractor.

## `config`

Enables you to manage the [configuration](/docs/configuration.html) of Meltano itself or any of its plugins, as well as [plugin extras](#how-to-use-plugin-extras).

When no explicit `--store` is specified, `meltano config <plugin> set` will automatically store the value in the [most appropriate location](/docs/configuration.html#configuration-layers):
- the [system database](/docs/project.html#system-database), if the project is [deployed as read-only](/docs/settings.html#project-readonly);
- the current location, if a setting's default value has already been overwritten;
- [`.env`](/docs/project.html#env), if a setting is sensitive or environment-specific (defined as `kind: password` or `env_specific: true`);
- [`meltano.yml`](/docs/project.html#meltano-yml-project-file) otherwise.

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

##### Dot separator

Note that `meltano config <plugin> list` always displays full config keys
with nesting represented by the `.` separator, matching the internal flattened representation:

```bash
meltano config <plugin> list
# => <property>.<subproperty>
# => <property>.<deep>.<nesting>
```

You can also set nested properties using the `.` separator, but specifying a list of names is preferred
since this will result in the nesting being reflected in the plugin's `config` object in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

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

In the context of `meltano config`, [plugin extras](/docs/configuration.html#plugin-extras) are distinguished from regular plugin-specific settings using an underscore (`_`) prefix, e.g. `_example_extra`. This also applies in the [environment variables](/docs/configuration.html#configuring-settings) that can be used to override them at runtime: since setting names for extras are prefixed with underscores (`_`), they get an extra underscore to separate them from the plugin name, e.g. `TAP_EXAMPLE__EXAMPLE_EXTRA`.

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

Lists the available [discoverable plugins](/docs/plugins.html#discoverable-plugins) and their [variants](/docs/plugins.html#variants).

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

This allows you to run your ELT pipeline to Extract, Load, and Transform data using an [extractor](/docs/plugins.html#extractors) and [loader](/docs/plugins.html#loaders) of your choosing,
and optional [transformations](/docs/plugins.html#transformers).

To allow subsequent pipeline runs with the same extractor/loader/transform combination to pick up right where the previous run left off,
each ELT run has a Job ID that is used to store and look up the [incremental replication state](/docs/integration.html#incremental-replication-state) in the [system database](/docs/production.html#storing-metadata). If no stable identifier is provided using the `--job_id` flag or the `MELTANO_JOB_ID` environment variable, extraction will always start from scratch and a one-off Job ID is automatically generated using the current date and time.

All the output generated by this command is also logged inside the [`.meltano` directory](/docs/project.html#meltano-directory) at `.meltano/logs/elt/{job_id}/{run_id}/elt.log`. The `run_id` is a UUID autogenerated at each run.

### How to use

```bash
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--job_id TEXT]
```

#### Parameters

- The `--job_id` option identifies related EL(T) runs when storing and looking up [incremental replication state](/docs/integration.html#incremental-replication-state).

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

- A `--full-refresh` flag can be passed to perform a full refresh, ignoring state left behind by any previous runs with the same job ID.

- A `--force` flag can be passed to force a new run even when a pipeline with the same Job ID is already running, which would result in an error otherwise.

- A `--catalog` option can be passed to manually provide a [catalog file](https://hub.meltano.com/singer/spec#catalog-files) for the extractor, as an alternative to letting one be [generated on the fly](/docs/integration.html#extractor-catalog-generation).
  This is equivalent to setting the [`catalog` extractor extra](/docs/plugins.html#catalog-extra).

- A `--state` option can be passed to manually provide a [state file](https://hub.meltano.com/singer/spec#state-files) for the extractor, as an alternative to letting state be [looked up based on the Job ID](/docs/integration.html#incremental-replication-state).
  This is equivalent to setting the [`state` extractor extra](/docs/plugins.html#state-extra).

- One or more `--select <entity>` options can be passed to only extract records for matching [selected entities](#select).
  Similarly, `--exclude <entity>` can be used to extract records for all selected entities _except_ for those specified.

  Notes:
  - The entities that are currently selected for extraction can be discovered using [`meltano select --list <extractor>`](#select).
  - [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity identifiers to match multiple entities at once.
  - Exclusion using `--exclude` takes precedence over inclusion using `--select`.
  - Specifying `--select` and/or `--exclude` is equivalent to setting the [`select_filter` extractor extra](/docs/plugins.html#select-filter-extra).

- A `--dump` option can be passed (along with any of the other options) to dump the content of a pipeline-specific generated file to [STDOUT](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) instead of actually running the pipeline.
  This can aid in debugging [extractor catalog generation](/docs/integration.html#extractor-catalog-generation), [incremental replication state lookup](/docs/integration.html#incremental-replication-state), and [pipeline environment variables](/docs/integration.html#pipeline-environment-variables).

  Supported values are:

  - `catalog`: Dump the extractor [catalog file](https://hub.meltano.com/singer/spec#catalog-files) that would be passed to the tap's executable using the `--catalog` option.
  - `state`: Dump the extractor [state file](https://hub.meltano.com/singer/spec#state-files) that would be passed to the tap's executable using the `--state` option.
  - `extractor-config`: Dump the extractor [config file](https://hub.meltano.com/singer/spec#config-files) that would be passed to the tap's executable using the `--config` option.
  - `loader-config`: Dump the loader [config file](https://hub.meltano.com/singer/spec#config-files) that would be passed to the target's executable using the `--config` option.

  Like any standard output, the dumped content can be [redirected](https://en.wikipedia.org/wiki/Redirection_(computing)) to a file using `>`, e.g. `meltano elt ... --dump=state > state.json`.

#### Examples

```bash
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

meltano elt tap-gitlab target-postgres --job_id=gitlab-to-postgres --full-refresh

meltano elt tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano elt tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano elt tap-gitlab target-postgres --select commits
meltano elt tap-gitlab target-postgres --exclude project_members

meltano elt tap-gitlab target-postgres --job_id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

### Debugging

If extraction, loading, or transformation is failing, or otherwise not behaving as expected,
you can learn more about what's going on behind the scenes by setting Meltano's
[`cli.log_level` setting](/docs/settings.html#cli-log-level) to `debug`,
using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI option:

```bash
MELTANO_CLI_LOG_LEVEL=debug meltano elt ...

meltano --log-level=debug elt ...
```

In debug mode, `meltano elt` will log the arguments and [environment](/docs/configuration.html#accessing-from-plugins) used to invoke the Singer tap and target executables (and `dbt`, when running transformations), including the paths to the generated
[config](https://hub.meltano.com/singer/spec#config-files),
[catalog](https://hub.meltano.com/singer/spec#catalog-files), and
[state](https://hub.meltano.com/singer/spec#state-files) files, for you to review:

```bash
$ meltano --log-level=debug elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl
meltano            | INFO Running extract & load...
meltano            | INFO Found state from 2020-08-05 21:30:20.487312.
meltano            | DEBUG Invoking: ['demo-project/.meltano/extractors/tap-gitlab/venv/bin/tap-gitlab', '--config', 'demo-project/.meltano/run/tap-gitlab/tap.config.json', '--state', 'demo-project/.meltano/run/tap-gitlab/state.json']
meltano            | DEBUG Env: {'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2020-05-01'}
meltano            | DEBUG Invoking: ['demo-project/.meltano/loaders/target-jsonl/venv/bin/target-jsonl', '--config', 'demo-project/.meltano/run/target-jsonl/target.config.json']
meltano            | DEBUG Env: {'MELTANO_EXTRACTOR_NAME': 'tap-gitlab', 'MELTANO_EXTRACTOR_NAMESPACE': 'tap_gitlab', 'MELTANO_EXTRACT_API_URL': 'https://gitlab.com', 'MELTANO_EXTRACT_PRIVATE_TOKEN': '', 'MELTANO_EXTRACT_GROUPS': '', 'MELTANO_EXTRACT_PROJECTS': 'meltano/meltano', 'MELTANO_EXTRACT_ULTIMATE_LICENSE': 'False', 'MELTANO_EXTRACT_START_DATE': '2020-05-01', 'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2020-05-01', 'TARGET_JSONL_DESTINATION_PATH': 'output', 'TARGET_JSONL_DO_TIMESTAMP_FILE': 'False'}
```

Note that the contents of these pipeline-specific generated files can also easily be dumped to [STDOUT](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) or a file using the `--dump` option described above.

Additionally, all [Singer messages](https://hub.meltano.com/singer/spec#messages) output by the tap and target will be logged, identified by `<plugin name> (out)` prefixes:

```bash
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

Used to create a new [Meltano project](/docs/project.html) directory inside the current working directory.

The new project directory will contain:

- a [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) that will list any [`plugins` you'll add](/docs/plugin-management.html#adding-a-plugin-to-your-project) and [pipeline `schedules` you'll create](/#orchestration),
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

Meltano installs plugins in parallel. The number of plugins to install in parallel defaults to the number of CPUs on the machine, but can be controlled with `--parallelism`. Use `--parallelism=1` to disable the feature and install them one at a time.

### How to Use

```bash
meltano install

meltano install extractors
meltano install extractor tap-gitlab
meltano install extractors tap-gitlab tap-adwords

meltano install models

meltano install --include-related

meltano install --parallelism=16
```

## `invoke`

Invoke the plugin's executable with specified arguments.

### How to use

```bash
meltano invoke <plugin> [PLUGIN]_ARGS...]
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```bash
meltano invoke --plugin-type=<type> <plugin> [PLUGIN_ARGS...]
```

A `--dump` option can be passed to dump the content of a generated [config file](https://hub.meltano.com/singer/spec#config-files) or [extractor catalog file](https://hub.meltano.com/singer/spec#catalog-files) to [STDOUT](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) instead of actually invoking the plugin:

```bash
meltano invoke --dump=config <plugin>
meltano invoke --dump=catalog <plugin>
```

Like any standard output, the dumped content can be [redirected](https://en.wikipedia.org/wiki/Redirection_(computing)) to a file using `>`, e.g. `meltano invoke --dump=catalog <plugin> > state.json`.

### Commands

Plugins can define [commands](/docs/configuration.html#plugin-commands), which are shortcuts for combinations of arguments. These can be invoked with the shortcut command of the form `meltano invoke <plugin>:<command>`.

```bash
meltano invoke dbt:seed
meltano invoke dbt:snapshot
```

Additional arguments can be specified as well, which will be appended to the command.

```bash
meltano invoke dbt:seed --show --threads 5
```

To see what commands a plugin supports, use `--list-command`:

```bash
meltano invoke --list-commands dbt
```

## `remove`

`meltano remove` removes one or more [plugins](/docs/plugins.html#project-plugins) of the same [type](/docs/plugins.html#types) from your Meltano [project](/docs/project.html).

Specifically, [plugins](/docs/plugins.html#project-plugins) will be removed from the:
- [`meltano.yml` project file](/docs/project.html)
- Installation found in the [`.meltano` directory](/docs/project.html#meltano-directory) under `.meltano/<plugin_type>/<plugin_name>`
- `plugin_settings` table in the [system database](/docs/project.html#system-database)

### How to Use

```bash
meltano remove <type> <name>
meltano remove <type> <name> <name_two>
```

### Examples

```bash
# meltano will attempt to remove an extractor called tap-gitlab
meltano remove extractor tap-gitlab

# meltano will attempt to remove two loaders; target-postgres and target-csv
meltano remove loader target-postgres target-csv
```

## `schedule`

::: tip
An `orchestrator` plugin is required to use `meltano schedule`: refer to the [Orchestration](/docs/orchestration.html) documentation to get started with Meltano orchestration.
:::

Use the `schedule` command to define ELT pipelines to be run by an orchestrator at regular intervals. These scheduled pipelines will be added to your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

You can run a specific scheduled pipeline's corresponding [`meltano elt`](#elt) command as a one-off using `meltano schedule run <schedule_name>`.
Any command line options (e.g. `--select=<entity>` or `--dump=config`) will be passed on to [`meltano elt`](#elt).

### How to use

The interval argument can be a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression) or one of the following presets:
`@hourly` (`0 * * * *`), `@daily` (`0 0 * * *`), `@weekly` (`0 0 * * 0`), `@monthly` (`0 0 1 * *`), `@yearly` (`0 0 1 1 *`), or `@once` (for schedules to be triggered manually through the UI).

```bash
# Add a schedule
meltano schedule <schedule_name> <extractor> <loader> <interval> [--transform={run,skip,only}]

# List all schedules
meltano schedule list [--format=json]

# Run a schedule
meltano schedule run <schedule_name>
```

### Examples

```bash
meltano schedule gitlab-to-postgres tap-gitlab target-postgres @daily --transform=run
# This specifies that the following command is to be run once a day:
# meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres

meltano schedule gitlab-to-jsonl tap-gitlab target-jsonl "* * * * *"
# This specifies that the following command is to be run every minute:
# meltano elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl

meltano schedule run gitlab-to-jsonl --select=commits
# This will run:
# meltano elt tap-gitlab target-jsonl --job_id=gitlab-to-jsonl --select=commits
```

## `select`

Use the `select` command to add select patterns to a specific extractor in your Meltano project.


- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attributes for a specific tap.

Selection rules will be stored in the extractor's [`select` extra](/docs/plugins.html#select-extra).

::: warning
Not all taps support this feature. In addition, taps needs to support the `--discover` switch. You can use `meltano invoke tap-... --discover` to see if the tap supports it.
:::

### How to use

[Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in selection patterns to match multiple entities or attributes at once:

- `*`: matches any sequence of characters
- `?`: matches one character
- `[abc]`: matches either `a`, `b`, or `c`
- `[!abc]`: matches any character **but** `a`, `b`, or `c`

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

### Examples

```bash
# List all available entities and attributes
meltano select tap-gitlab --list --all

# Include all attributes of an entity
meltano select tap-gitlab tags "*"

# Include specific attributes of an entity
meltano select tap-gitlab commits id
meltano select tap-gitlab commits project_id
meltano select tap-gitlab commits created_at
meltano select tap-gitlab commits author_name
meltano select tap-gitlab commits message

# Exclude matching attributes of all entities
meltano select tap-gitlab --exclude "*" "*_url"

# List selected (enabled) entities and attributes
meltano select tap-gitlab --list
```

Example output:

```
Enabled patterns:
    tags.*
    commits.id
    commits.project_id
    commits.created_at
    commits.author_name
    commits.message
    !*.*_url

Selected attributes:
    [selected ] commits.author_name
    [selected ] commits.created_at
    [automatic] commits.id
    [selected ] commits.message
    [selected ] commits.project_id
    [automatic] tags.commit_id
    [selected ] tags.message
    [automatic] tags.name
    [automatic] tags.project_id
    [selected ] tags.target
```

::: tip
Most shells parse glob syntax: you must escape the special characters in the select pattern by quoting the pattern.
:::

### Exclude Parameter

Use `--exclude` to exclude all attributes that match the filter.

Attributes that are `automatic` are always included, even if they match an exclude pattern. Only attributes that are `available` can be excluded.

Exclusion takes precedence over inclusion. If an attribute is excluded, there is no way to include it back without removing the exclusion pattern first.

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
will be stored in your project's [`.env` file](/docs/project.html#env) along with the
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

Upgrade Meltano and your Meltano project to the latest version.

When called without arguments, this will:
- Upgrade the `meltano` package
- Update files [managed by](/docs/plugins.html#update-extra) [file bundles](/docs/plugins.html#file-bundles)
- Apply migrations to [system database](/docs/project.html#system-database)
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
