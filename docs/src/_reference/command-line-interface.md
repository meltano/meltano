---
title: Command Line
description: Meltano provides a command line interface (CLI) that makes it easy to manage your project, plugins, and EL(T) pipelines.
layout: doc
weight: 1
---

Meltano provides a command line interface (CLI) that makes it easy to manage your [project](/concepts/project), [plugins](/guide/plugin-management), and [EL(T) pipelines](/guide/integration).
To quickly find the `meltano` subcommand you're looking for, use the Table of Contents in the sidebar.
For a better understanding of command line documentation syntax, the [docopt](http://docopt.org/) standard is useful.

## `add`

`meltano add` lets you add [plugins](/concepts/plugins#project-plugins) to your Meltano project.

Specifically, it will:

1. Look for the [plugin definition](/concepts/project#plugins) in [Meltano Hub](https://hub.meltano.com/)
2. Add it to your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) under `plugins: <type>s:`, e.g. `plugins: extractors`
3. Store the plugin definition in the `./plugins` directory (see [Lock Artifacts](/concepts/plugins#lock-artifacts))
4. Assuming a valid `pip_url` is specified, install the new plugin using [`meltano install <type> <name>`](#install), which will:
   1. Create a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for the plugin inside the [`.meltano` directory](/concepts/project#meltano-directory) at `.meltano/<type>s/<name>/venv`, e.g. `.meltano/extractors/tap-gitlab/venv`
   2. Install the plugin's [pip package](https://pip.pypa.io/en/stable/) into the virtual environment using `pip install <pip_url>`

(Some plugin types have slightly different or additional behavior; refer to the [plugin type documentation](/concepts/plugins#types) for more details.)

Once the plugin has been added to your project, you can configure it using [`meltano config`](#config),
invoke its executable using [`meltano invoke`](#invoke), and use it in a pipeline using [`meltano elt`](#elt).

To learn more about adding a plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#adding-a-plugin-to-your-project).

> Note: Unlike [`meltano install`](#install), this command installs plugins serially to avoid missing dependencies (e.g. a [`transform`](/concepts/plugins#transforms) requires the [`dbt` plugin](/guide/transformation) to be installed first).

### How to use

The only required arguments are the new plugin's [type](/concepts/plugins#types) and unique name:

```bash
meltano add <type> <name>

# For example:
meltano add extractor tap-gitlab
meltano add loader target-postgres
```

Without a `--custom` or `--inherit-from` option, this will add the
[discoverable plugin](/concepts/plugins#discoverable-plugins) with the provided name
to your [`meltano.yml` project file](/concepts/project#plugins)
using a [shadowing plugin definition](/concepts/project#shadowing-plugin-definitions).

If multiple [variants](/concepts/plugins#variants) of the discoverable plugin are available, the specific variant to add can be identified using the `--variant` option:

```bash
meltano add <type> <name> --variant <variant>

# For example:
meltano add loader target-postgres --variant transferwise
```

To add a [custom plugin](/concepts/plugins#custom-plugins) using a [custom plugin definition](/concepts/project#custom-plugin-definitions), use the `--custom` flag:

```bash
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19

# If you're using Docker, don't forget to mount the project directory,
# and ensure that interactive mode is enabled so that Meltano can ask you
# additional questions about the plugin and get your answers over STDIN:
docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom extractor tap-covid-19
```

To add a plugin [inheriting from](/concepts/plugins#plugin-inheritance) an existing one using an [inheriting plugin definition](/concepts/project#inheriting-plugin-definitions), use the `--inherit-from` option:

```bash
meltano add <type> <name> --inherit-from <existing-name>

# For example:
meltano add extractor tap-ga--client-foo --inherit-from tap-google-analytics
```

#### Parameters

- `--custom`: Add a [custom plugin](/concepts/plugins#custom-plugins). The command will prompt you for the package's [base plugin description](/concepts/plugins#project-plugins) metadata.

- `--inherit-from=<existing-name>`: Add a plugin [inheriting from](/concepts/plugins#plugin-inheritance) an existing plugin in the project or a [discoverable plugin](/concepts/plugins#discoverable-plugins) identified by name.

- `--as=<new-name>`: `meltano add <type> <name> --as=<new-name>` is equivalent to `meltano add <type> <new-name> --inherit-from=<name>`, and can be used to add a [discoverable plugin](/concepts/plugins#discoverable-plugins) to your project with a different name.

- `--variant=<variant>`: Add a specific (non-default) [variant](/concepts/plugins#variants) of the identified [discoverable plugin](/concepts/plugins#discoverable-plugins).

## `config`

Enables you to manage the [configuration](/guide/configuration) of Meltano itself or any of its plugins, as well as [plugin extras](#how-to-use-plugin-extras).

When no explicit `--store` is specified, `meltano config <plugin> set` will automatically store the value in the [most appropriate location](/guide/configuration#configuration-layers):

- the [system database](/concepts/project#system-database), if the project is [deployed as read-only](/reference/settings#project-readonly);
- the current location, if a setting's default value has already been overwritten;
- [`.env`](/concepts/project#env), if a setting is sensitive or environment-specific (defined as `kind: password` or `env_specific: true`);
- [`meltano.yml`](/concepts/project#meltano-yml-project-file) otherwise.

If supported by the plugin type, its configuration can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

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

# Test the plugin's current configuration, if supported.
meltano config <plugin> test
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
{
  "<property>": {
    "<subproperty>": "<value>",
    "<deep>": { "<nesting>": "<value>" }
  }
}
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
since this will result in the nesting being reflected in the plugin's `config` object in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file):

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

### Using `config` with Environments

If you have multiple [Meltano Environments](/concepts/environments) you can specify the environment name:

```bash
meltano --environment=<ENVIRONMENT> config <plugin>
```

### How to use: Plugin extras

In the context of `meltano config`, [plugin extras](/guide/configuration#plugin-extras) are distinguished from regular plugin-specific settings using an underscore (`_`) prefix, e.g. `_example_extra`. This also applies in the [environment variables](/guide/configuration#configuring-settings) that can be used to override them at runtime: since setting names for extras are prefixed with underscores (`_`), they get an extra underscore to separate them from the plugin name, e.g. `TAP_EXAMPLE__EXAMPLE_EXTRA`.

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

Lists the available [discoverable plugins](/concepts/plugins#discoverable-plugins) and their [variants](/concepts/plugins#variants).

### How to Use

```bash
# List all available plugins
meltano discover all

# Only list available extractors
meltano discover extractors

# Only list available loaders
meltano discover loaders

```

## `elt`

This allows you to run your ELT pipeline to Extract, Load, and Transform data using an [extractor](/concepts/plugins#extractors) and [loader](/concepts/plugins#loaders) of your choosing,
and optional [transformations](/concepts/plugins#transformers).

To allow subsequent pipeline runs with the same extractor/loader/transform combination to pick up right where the previous run left off,
each ELT run has a State ID that is used to store and look up the [incremental replication state](/guide/integration#incremental-replication-state) in the [system database](/guide/production#storing-metadata). If no stable identifier is provided using the `--state-id` flag or the `MELTANO_STATE_ID` environment variable, extraction will always start from scratch and a one-off State ID is automatically generated using the current date and time.

All the output generated by this command is also logged inside the [`.meltano` directory](/concepts/project#meltano-directory) at `.meltano/logs/elt/{state_id}/{run_id}/elt.log`. The `run_id` is a UUID autogenerated at each run.

<div class="notification is-info">
  <p>The command <a href="/reference/command-line-interface#run"><code>meltano run</code></a> is the recommended way to run cross-plugin workflows, including ELT, in a composable manner.</p>
</div>

### How to use

```bash
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--state-id TEXT]
```

#### Parameters

- The `--state-id` option identifies related EL(T) runs when storing and looking up [incremental replication state](/guide/integration#incremental-replication-state).

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

- A `--full-refresh` flag can be passed to perform a full refresh, ignoring state left behind by any previous runs with the same State ID.

- A `--force` flag can be passed to force a new run even when a pipeline with the same State ID is already running, which would result in an error otherwise.

- A `--catalog` option can be passed to manually provide a [catalog file](https://hub.meltano.com/singer/spec#catalog-files) for the extractor, as an alternative to letting one be [generated on the fly](/guide/integration#extractor-catalog-generation).
  This is equivalent to setting the [`catalog` extractor extra](/concepts/plugins#catalog-extra).

- A `--state` option can be passed to manually provide a [state file](https://hub.meltano.com/singer/spec#state-files) for the extractor, as an alternative to letting state be [looked up based on the State ID](/guide/integration#incremental-replication-state).
  This is equivalent to setting the [`state` extractor extra](/concepts/plugins#state-extra).

- One or more `--select <entity>` options can be passed to only extract records for matching [selected entities](#select).
  Similarly, `--exclude <entity>` can be used to extract records for all selected entities _except_ for those specified.

  Notes:

  - The entities that are currently selected for extraction can be discovered using [`meltano select --list <extractor>`](#select).
  - [Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in entity identifiers to match multiple entities at once.
  - Exclusion using `--exclude` takes precedence over inclusion using `--select`.
  - Specifying `--select` and/or `--exclude` is equivalent to setting the [`select_filter` extractor extra](/concepts/plugins#select-filter-extra).

- A `--dump` option can be passed (along with any of the other options) to dump the content of a pipeline-specific generated file to [STDOUT](<https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)>) instead of actually running the pipeline.
  This can aid in debugging [extractor catalog generation](/guide/integration#extractor-catalog-generation), [incremental replication state lookup](/guide/integration#incremental-replication-state), and [pipeline environment variables](/guide/integration#pipeline-environment-variables).

  Supported values are:

  - `catalog`: Dump the extractor [catalog file](https://hub.meltano.com/singer/spec#catalog-files) that would be passed to the tap's executable using the `--catalog` option.
  - `state`: Dump the extractor [state file](https://hub.meltano.com/singer/spec#state-files) that would be passed to the tap's executable using the `--state` option.
  - `extractor-config`: Dump the extractor [config file](https://hub.meltano.com/singer/spec#config-files) that would be passed to the tap's executable using the `--config` option.
  - `loader-config`: Dump the loader [config file](https://hub.meltano.com/singer/spec#config-files) that would be passed to the target's executable using the `--config` option.

  Like any standard output, the dumped content can be [redirected](<https://en.wikipedia.org/wiki/Redirection_(computing)>) to a file using `>`, e.g. `meltano elt ... --dump=state > state.json`.

#### Examples

```bash
meltano elt tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres

meltano elt tap-gitlab target-postgres --state-id=gitlab-to-postgres --full-refresh

meltano elt tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano elt tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano elt tap-gitlab target-postgres --select commits
meltano elt tap-gitlab target-postgres --exclude project_members

meltano elt tap-gitlab target-postgres --state-id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

### Using `elt` with Environments

The `--environment` option can be passed to specify a [Meltano Environment](/concepts/environments) context for running.

```bash
meltano --environment=prod elt tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres
```

### Debugging

If extraction, loading, or transformation is failing, or otherwise not behaving as expected,
you can learn more about what's going on behind the scenes by setting Meltano's
[`cli.log_level` setting](/reference/settings#cli-log-level) to `debug`,
using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI option:

```bash
MELTANO_CLI_LOG_LEVEL=debug meltano elt ...

meltano --log-level=debug elt ...
```

In debug mode, `meltano elt` will log the arguments and [environment](/guide/configuration#accessing-from-plugins) used to invoke the Singer tap and target executables (and `dbt`, when running transformations), including the paths to the generated
[config](https://hub.meltano.com/singer/spec#config-files),
[catalog](https://hub.meltano.com/singer/spec#catalog-files), and
[state](https://hub.meltano.com/singer/spec#state-files) files, for you to review:

```bash
$ meltano --log-level=debug elt tap-gitlab target-jsonl --state-id=gitlab-to-jsonl
meltano            | INFO Running extract & load...
meltano            | INFO Found state from 2020-08-05 21:30:20.487312.
meltano            | DEBUG Invoking: ['demo-project/.meltano/extractors/tap-gitlab/venv/bin/tap-gitlab', '--config', 'demo-project/.meltano/run/tap-gitlab/tap.config.json', '--state', 'demo-project/.meltano/run/tap-gitlab/state.json']
meltano            | DEBUG Env: {'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2021-03-01'}
meltano            | DEBUG Invoking: ['demo-project/.meltano/loaders/target-jsonl/venv/bin/target-jsonl', '--config', 'demo-project/.meltano/run/target-jsonl/target.config.json']
meltano            | DEBUG Env: {'MELTANO_EXTRACTOR_NAME': 'tap-gitlab', 'MELTANO_EXTRACTOR_NAMESPACE': 'tap_gitlab', 'MELTANO_EXTRACT_API_URL': 'https://gitlab.com', 'MELTANO_EXTRACT_PRIVATE_TOKEN': '', 'MELTANO_EXTRACT_GROUPS': '', 'MELTANO_EXTRACT_PROJECTS': 'meltano/meltano', 'MELTANO_EXTRACT_ULTIMATE_LICENSE': 'False', 'MELTANO_EXTRACT_START_DATE': '2021-03-01', 'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2021-03-01', 'TARGET_JSONL_DESTINATION_PATH': 'output', 'TARGET_JSONL_DO_TIMESTAMP_FILE': 'False'}
```

Note that the contents of these pipeline-specific generated files can also easily be dumped to [STDOUT](<https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)>) or a file using the `--dump` option described above.

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

## `environment`

Use the `environment` command to manage [Environments](/concepts/environments) in your Meltano project.

### How to use

```bash
# Add an environment
meltano environment add <environment_name>

# Remove an environment
meltano environment remove <environment_name>

# List available environments
meltano environment list
```

Once an Environment is configured, the `--environment` option or `MELTANO_ENVIRONMENT` environment variable can be used with the following commands:

- [`config`](#using-config-with-environments)
- [`elt`](#using-elt-with-environments)
- [`invoke`](#using-invoke-with-environments)
- [`select`](#using-select-with-environments)

If there is a value provided for `default_environment` in your `meltano.yml` these commands will be run using that Environment if no `--environment` option or `MELTANO_ENVIRONMENT` environment variable is provided. If you have `default_environment` set this way but would prefer to use no environment use the option `--environment=null` (or its equivalent using a space instead of an `=`: `--environment null`) or use the `--no-environment` flag.

### Examples

```bash
# Add a new Environment
meltano environment add prod

# List existing Environments
meltano environment list

# Add plugin configuration within the new Environment
meltano --environment=prod config target-postgres set batch_size_rows 50000

# Remove an Environment
meltano environment remove prod
```

## `init`

Used to create a new [Meltano project](/concepts/project) directory inside the current working directory.

The new project directory will contain:

- a [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) that will list any [`plugins` you'll add](/guide/plugin-management#adding-a-plugin-to-your-project) and [pipeline `schedules` you'll create](/guide/orchestration),
- stubs for `.gitignore`, `README.md`, and `requirements.txt` for you to edit (or delete) as appropriate, and
- empty `extract`, `load`, `transform`, `notebook`, and `orchestrate` directories for you to use (or delete) as you please.

[Anonymous usage statistics](/reference/settings#send-anonymous-usage-stats) are enabled by default, unless the `--no_usage_stats` flag is provided, the `MELTANO_SEND_ANONYMOUS_USAGE_STATS` environment variable is disabled, or you set `send_anonymous_usage_stats: false` in your `meltano.yml`.

### How to use

```bash
# Format
meltano init [project_name] [--no_usage_stats]
```

#### Parameters

- **project_name** - This determines the folder name for the project

#### Options

- **no_usage_stats** - This flag disables the [`send_anonymous_usage_stats` setting](/reference/settings#send-anonymous-usage-stats).

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
echo "export MELTANO_SEND_ANONYMOUS_USAGE_STATS=0" >> $SHELLRC
meltano init demo-project # --no_usage_stats is implied
```

## `install`

Installs dependencies of your project based on the **meltano.yml** file.

Optionally, provide a plugin type argument to only (re)install plugins of a certain type.
Additionally, plugin names can be provided to only (re)install those specific plugins.

Use `--include-related` to automatically install transforms related to installed extractor plugins.

Subsequent calls to `meltano install` will upgrade a plugin to it's latest version, if any. To completely uninstall and reinstall a plugin, use `--clean`.

Meltano installs plugins in parallel. The number of plugins to install in parallel defaults to the number of CPUs on the machine, but can be controlled with `--parallelism`. Use `--parallelism=1` to disable the feature and install them one at a time.

<div class="notification is-info">
  <p>If you're using a custom Docker image, make sure `python3-venv` is installed:</p>
<pre>
FROM ubuntu:20.04

RUN apt-get update && \
 apt-get install -y -q \
 gcc \
 sqlite3 \
 libsqlite3-dev \
 python3 \
 python3-pip \
 python3-venv # Add this line

RUN pip3 install meltano

WORKDIR /meltano
COPY meltano.yml meltano.yml
RUN mkdir .meltano/ && meltano install

</pre>
</div>

### How to Use

```bash
meltano install

meltano install extractors
meltano install extractor tap-gitlab
meltano install extractors tap-gitlab tap-adwords


meltano install --include-related

meltano install --parallelism=16
meltano install --clean
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

A `--dump` option can be passed to dump the content of a generated [config file](https://hub.meltano.com/singer/spec#config-files) or [extractor catalog file](https://hub.meltano.com/singer/spec#catalog-files) to [STDOUT](<https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)>) instead of actually invoking the plugin:

```bash
meltano invoke --dump=config <plugin>
meltano invoke --dump=catalog <plugin>
```

Like any standard output, the dumped content can be [redirected](<https://en.wikipedia.org/wiki/Redirection_(computing)>) to a file using `>`, e.g. `meltano invoke --dump=catalog <plugin> > state.json`.

### Using `invoke` with Environments

If you have multiple [Meltano Environments](/concepts/environments) you can specify the environment name:

```bash
meltano --environment=<ENVIRONMENT> invoke <plugin> [PLUGIN]_ARGS...]
```

### Commands

Plugins can define [commands](/concepts/project#plugin-commands), which are shortcuts for combinations of arguments. These can be invoked with the shortcut command of the form `meltano invoke <plugin>:<command>`.

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

### Containerized commands

To execute plugins inside containers, use the `--containers` flag:

```bash
meltano invoke --containers dbt:compile
```

### Debugging plugin environment

When debugging plugin configuration, it is often useful to view environment variables being provided to a plugin at runtime.
This can be achieved using `--log-level=debug` but for readability and convenience, the `meltano invoke` command also supports printing individual environment variables to stdout at runtime:

```bash
# Print the runtime value PLUGIN_ENVIRONMENT_VARIABLE_1:
meltano invoke --print-var <PLUGIN_ENVIRONMENT_VARIABLE_1> <PLUGIN_NAME>

# The option supports printing multiple variables as well.

# # Print the runtime values of both PLUGIN_ENVIRONMENT_VARIABLE_1 and PLUGIN_ENVIRONMENT_2 on separate lines:
meltano invoke --print-var <PLUGIN_ENVIRONMENT_VARIABLE_1> --print-var <PLUGIN_ENVIRONMENT_VARIABLE_2> <PLUGIN_NAME>
```

## `lock`

`meltano lock` creates lock files for [non-custom](/concepts/plugins#custom-plugins) plugins in the project.

### How to use

```bash
# Lock all plugins
meltano lock --all

# Lock all plugins of a certain type
meltano lock --all --plugin-type=<type>

# Lock specific plugins
meltano lock <name> <name_two>

# Lock specific plugins and disambiguate by type
meltano lock <name> <name_two> --plugin-type=<type>

# Use --update in combination with any of the above to update the lock file
# with the latest definition from MeltanoHub
meltano lock --all --update
```

## `remove`

`meltano remove` removes one or more [plugins](/concepts/plugins#project-plugins) of the same [type](/concepts/plugins#types) from your Meltano [project](/concepts/project).

Specifically, [plugins](/concepts/plugins#project-plugins) will be removed from the:

- [`meltano.yml` project file](/concepts/project)
- Installation found in the [`.meltano` directory](/concepts/project#meltano-directory) under `.meltano/<plugin_type>/<plugin_name>`
- `plugin_settings` table in the [system database](/concepts/project#system-database)
- `./plugins/<plugin type>/` lock file directory

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

## `run`

Run a set of command blocks in series.

Command blocks are specified as a list of plugin names, e.g. `meltano run some_tap some_mapping some_target some_plugin:some_cmd` and
are run in the order they are specified from left to right. A failure in any block will cause the entire run to abort.

Multiple commmand blocks can be chained together or repeated, and extractor/loader pairs will automatically be linked to perform EL work.
If you have an active environment defined, a State ID is autogenerated for each extractor/loader pair and used to store and look up the [incremental replication state](/guide/integration#incremental-replication-state) in the [system database](/guide/production#storing-metadata).
This allows subsequent runs with the same extractor and loader combinations to start where the previous run ended.
The format of the generated id's is `<environment_name>:<tap_name>-to-<target_name>`.
Note that [inline mapping names](/concepts/plugins#mappers) are _not included_ when generating IDs.

Note that if no environment is active, `meltano run` _does not_ generate a State ID and it does not track state.

In addition to explicitly specifying plugin names you can also execute one or more named
[jobs](/reference/command-line-interface#job) alongside other commands.

### How to use

```bash
meltano run tap-gitlab target-postgres
meltano run tap-gitlab target-postgres dbt-postgres:clean dbt-postgres:test dbt-postgres:run
meltano run tap-gitlab target-postgres tap-salesforce target-mysql
meltano run tap-gitlab target-postgres dbt-postgres:run tap-postgres target-bigquery
meltano --environment=<ENVIRONMENT> run tap-gitlab target-postgres
meltano run tap-gitlab one-mapping another-mapping target-postgres
meltano run tap-gitlab target-postgres simple-job
```

#### Parameters

When an active environment is present, `run` will attempt to run incrementally and save state by default.
However, four top level flags are provided to alter behavior:

- `--dry-run` just parse the invocation, validate it, and explain what would be executed. Does not execute anything.
  (implicitly enables --log-level=debug for 'console' named handlers).
- `--no-state-update` will disable state saving for this invocation.
- `--full-refresh` will force a full refresh and ignore the prior state. The new state after completion will still be updated with the execution results, unless `--no-state-update` is also specified.
- `--force` will force a job run even if a conflicting job with the same generated ID is in progress.

Examples:

```bash
# run the two pipelines in series
# the autogenerated ID for the first EL pair will be 'dev:tap-gitlab-to-target-postgres'
# the autogenerated ID for the second EL pair will be 'dev:tap-gitlab-to-target-mysql'
meltano --environment=prod run tap-gitlab hide-secrets target-postgres tap-salesforce target-mysql

# run the pipelines in series, performing a full refresh for all.
meltano--environment=stg run --full-refresh tap-gitlab target-postgres tap-salesforce target-mysql ...

# run the pipelines in series, forcing each if a conflicting job is found.
meltano--environment=dev run --force tap-gitlab target-postgres tap-salesforce target-mysql ...

```

### Using `run` with Environments

If you have multiple Meltano Environments you can specify the environment name:

```bash
meltano --environment=<ENVIRONMENT> run ...
```

Note that if no environment is active, `meltano run` _does not_ generate a state ID and it does not track state.

## `job`

Use the `job` command to define one or more sequences of tasks. A job can contain a single task or many tasks.
As of today all tasks are run sequentially.
You can run a specified job by passing the job name as an argument to [`meltano run`](#run).
You can also schedule jobs using [`meltano schedule`](#schedule).

### How to use

```bash
# Add a job with a single task representing a run command
meltano job add <job_name> --tasks "<tap_name> <mapping_name> <target_name> <command>"

# Add a new job with multiple tasks by passing arrays in yaml format, where each item represents a run command.
# This will generate one task per array element:
# task 1: <tap_name> <target_name>
# task 2: <command>
# task 3: <tap2_name> <target2_name>
# etc.
meltano job add <job_name> --tasks "[<tap_name> <target_name>, <command>, <tap2_name> <target2_name>, ...]"

# Update an existing job with new tasks
meltano job set <job_name> --tasks "<tap_name> <mapping_name> <target_name> <command>"
meltano job set <job_name> --tasks "[<tap_name> <target_name>, <command>, <tap2_name> <target2_name>, ...]"

# List all jobs
meltano job list
meltano job list --format=json

# List a named job
meltano job list <job_name>
meltano job list <job_name> --format=json

# Remove a named job
meltano job remove <job_name>
```

##### Tasks

A task should be of the same format as arguments supplied to [the `meltano run` command](#run), which can be any valid sequence of plugins (e.g. extractors, mappers, loaders, utilities, etc.) and [plugin commands](/concepts/project#plugin-commands).
Note that such a sequence is only valid if it is one of:

1. An extractor followed directly by a loader. E.g. `tap-gitlab target-postgres`
1. An extractor followed by one or more mappers and then a loader. E.g. `tap-gitlab hide-gitlab-secrets target-postgres`
1. A plugin command invocation. E.g. `dbt-postgres:run`
1. Any sequence of the above. E.g. `tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run tap-zendesk target-csv`

If a job has only one task, that task can be supplied as a single quoted argument:

```bash
# A task with a single extractor and loader
meltano job add tap-gitlab-to-target-postgres --tasks "tap-gitlab target-postgres"

# A more complex task
meltano job add tap-gitlab-to-target-postgres-processed --tasks "tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run"
```

This would add the following to your `meltano.yml`:

```yaml
jobs:
  - name: tap-gitlab-to-target-postgres
    tasks:
      - tap-gitlab target-postgres
  - name: tap-gitlab-to-target-postgres-processed
    tasks:
      - tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run
```

When an Airflow DAG is generated for a job, each task in the job definition will become a single task in the generated DAG.
So while it is certainly possible to define all your jobs using only one task each, there are many scenarios in which it would
be useful or even necessary to split your job into multiple tasks.
For instance, job steps which must always run, fail, and be retried as a group should always be a part of the same task.
And long-running job steps should likely be grouped into a separate task from shorter-running downstream steps so that those downstream steps can be rerun on their own.

Each individual task must itself be a valid sequence of extractors, mappers, loaders, and plugin commands.
When multiple tasks are defined in a job, they should be supplied to the `meltano job add` command as an array in YAML format.

For instance the `tap-gitlab-to-target-postgres-processed` job in the above example could also be created as:

```bash
meltano job add tap-gitlab-to-target-postgres-processed --tasks "[tap-gitlab hide-gitlab-secrets target-postgres, dbt-postgres:run]"
```

This would add the following to your `meltano.yml`:

```yaml
jobs:
  - name: tap-gitlab-to-target-postgres-processed-multiple-tasks
    tasks:
      - tap-gitlab hide-gitlab-secrets target-postgres
      - dbt-postgres:run
```

While `tap-gitlab-to-target-postgres-processed` and `tap-gitlab-to-target-postgres-processed-multiple-tasks` will run the same steps of the pipeline in the same order, [scheduling](#schedule) the former will result in a generated DAG consisting of a single task while scheduling the latter will result in a generated DAG consisting of two tasks.

### Examples

```bash
# Add a new job named "simple-demo" that contains two tasks
# Task 1: tap-gitlab hide-gitlab-secrets target-mysql
# Task 2: tap-gitlab target-csv
meltano job add simple-demo --tasks "[tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run, tap-gitlab target-csv]"

# list the job named "simple-demo"
meltano job list simple-demo --format=json
# run the job named "simple-demo" using meltano run
meltano run simple-demo
# run the job named "simple-demo" AND another EL pair using meltano run
meltano run simple-demo tap-mysql target-bigquery
# remove the job named "simple-demo"
meltano job remove simple-demo
```

## `schedule`

<div class="notification is-info">
  <p>An <code>orchestrator</code> plugin is required to use <code>meltano schedule</code>: refer to the <a href="/guide/orchestration">Orchestration</a> documentation to get started with Meltano orchestration.</p>
</div>

Use the `schedule` command to define ELT or Job pipelines to be run by an orchestrator at regular intervals.
These scheduled pipelines will be added to your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file).
You can schedule both [jobs](#job) or legacy [`meltano elt`](#elt) tasks.

You can run a specific scheduled pipeline's corresponding [`meltano run`](#run) or [`meltano elt`](#elt) command as a one-off using `meltano schedule run <schedule_name>`.
Any command line options (e.g. `--select=<entity>` or `--dry-run`) will be passed on to the underlying commands.

### How to use

The interval argument can be a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression) or one of the following presets:
`@hourly` (`0 * * * *`), `@daily` (`0 0 * * *`), `@weekly` (`0 0 * * 0`), `@monthly` (`0 0 1 * *`), `@yearly` (`0 0 1 1 *`), or `@once` (for schedules to be triggered manually through the UI).

```bash
# Add a schedule
# Schedule a job named "my_job" to run everyday
meltano schedule add <schedule_name> --job my_job --interval "@daily"
# Schedule an ELT task to run hourly
meltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform run --interval "@hourly"

# List all schedules
meltano schedule list [--format=json]

# Remove a named schedule
meltano schedule remove <schedule_name>

# Update a named schedule changing the interval
meltano schedule set <schedule_name> --interval <new-interval>
# Update a named schedule changing the referenced job
meltano schedule set <schedule_name> --job <new-job>
# Update a named ELT scheduled changing the interval AND changing the extractor
meltano schedule set <schedule_name> --extractor <new-tap> --interval <new-interval>

# Run a schedule
meltano schedule run <schedule_name>
```

### Examples

```bash
# Add a new schedule named "gitlab-sync" to run the job named "gitlab-to-mysql" every day
meltano schedule add gitlab-sync --job gitlab-to-mysql --interval "@daily"

# Perform a dry-run of the schedule named "gitlab-sync"
# Behind the scenes, this will execute a `meltano run --dry-run gitlab-sync`
meltano schedule run gitlab-sync --dry-run

# Update the schedule named "gitlab-sync" to run the job named "gitlab-to-postgres" instead of "gitlab-to-mysql"
meltano schedule set gitlab-sync --job gitlab-to-postgres
# Update the schedule named "gitlab-sync" to run weekly instead of daily
meltano schedule set gitlab-sync --interval "@weekly"

# Add a legacy ELT based schedule named "gitlab-to-jsonl" to run every minute
# This specifies that the following command is to be run every minute:
# meltano elt tap-gitlab target-jsonl --state-id=gitlab-to-jsonl
meltano schedule add gitlab-to-jsonl --extractor tap-gitlab --loader target-jsonl --interval="* * * * *"
# Update the schedule named "gitlab-to-jsonl" to use target-csv instead of target-jsonl
meltano schedule set gitlab-to-jsonl --loader target-csv
```

## `select`

Use the `select` command to add select patterns to a specific extractor in your Meltano project.

- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attributes for a specific tap.

Selection rules will be stored in the extractor's [`select` extra](/concepts/plugins#select-extra).

<div class="notification is-warning">
  <p>Not all taps support this feature. In addition, taps needs to support the <code>--discover</code> switch. You can use <code>meltano invoke tap-... --discover</code> to see if the tap supports it.</p>
</div>

### How to use

[Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in selection patterns to match multiple entities or attributes at once:

- `*`: matches any sequence of characters
- `?`: matches one character
- `[abc]`: matches either `a`, `b`, or `c`
- `[!abc]`: matches any character **but** `a`, `b`, or `c`

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

Use `--rm` or `--remove` to remove previously added select patterns.

### Using `select` with Environments

If you have multiple [Meltano Environments](/concepts/environments) you can specify the environment name:

```bash
meltano --environment=<ENVIRONMENT> select <tap_name>
```

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

Remove patterns (`--rm` or `--remove`):

```bash
# Remove previously added select patterns
meltano select tap-gitlab --rm tags "*"
meltano select tap-gitlab --rm --exclude "*" "*_url"
meltano select tap-gitlab --rm commits id
```

<div class="notification is-info">
  <p>Most shells parse glob syntax: you must escape the special characters in the select pattern by quoting the pattern.</p>
</div>

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

## `state`

Manage Singer State for jobs via the CLI.

For more information about how Meltano uses incremental replication state, see [the data integration guide](/guide/integration#incremental-replication-state).

### clear

Clear the state for a given `state_id`.
Prompts for confirmation.

#### How to use

```bash
meltano state clear [--force] <state_id>
```

#### Parameters

- The `--force` option will disable confirmation prompts. _Use with caution._

#### Examples

```bash
# Clear state. Meltano will prompt for confirmation.
meltano state clear dev:tap-gitlab-to-target-jsonl

# Clear state, overriding confirmation prompt.
meltano state clear --force dev:tap-gitlab-to-target-jsonl
```

### get

Retrieve state for a given `state_id`.

#### How to use

```bash
meltano state get <state_id>
```

#### Examples

```bash
# Print the state that would be used in the next run of dev:tap-gitlab-to-target-jsonl
meltano state get dev:tap-gitlab-to-target-jsonl
```

### list

List all `state_ids` found in the system database.

#### How to use

```bash
meltano state list [--pattern] <PATTERN>
```

#### Parameters

- The `--pattern` option allows filtering returned state IDs by using `*` as a wildcard.

<div class="notification is-info">
  <p>"<samp>*</samp>" is subject to auto-expansion in most shells: you must escape the " <samp>*</samp>" by quoting the pattern.</p>
</div>

#### Examples

```bash
# List all state IDs
meltano state list

# List only those state IDs that start with "dev:"
meltano state list 'dev:*'

# List only those state IDs that contain "tap-gitlab"
meltano state list --pattern '*tap-gitlab*'
```

### merge

Merge new state onto existing state for a state ID.

<div class="notification is-info">
	<p><strong>Not seeing merged state in the system database?</strong></p>
	<p>Merged state is computed at <em>execution</em> time.
	The <samp>merge</samp> command merely
	adds a new <samp>payload</samp> to the database which is merged together with
	existing payloads the next time state is read via <samp>meltano elt</samp>, <samp>meltano run</samp>, or <samp>meltano state get</samp>.
	</p>
</div>

#### How to use

```bash
# Read state from a file
meltano state merge <state_id> --input-file <file>

# Read state from a command-line argument
meltano state merge <state_id> <RAW STATE JSON>

# Merge state onto other state
meltano state merge <state_id> --from-state-id <src_state_id>
```

#### Parameters

- The `--input-file` option specifies a file to read the state from.
- The `--from-state-id` option specifies an existing state ID to read the state from.

State must be provided in exactly one of these ways: via `--input-file`, via `--from-state-id`, or via a command line argument.

#### Examples

```bash
# Provide state via a command-line argument.
# The argument must be valid JSON with a top-level key of "singer_state"
# Only the "project_123456_issues" key will be overwritten. Any other bookmarks will remain untouched.
meltano state merge dev:tap-gitlab-to-target-jsonl '{"singer_state": {"project_123456_issues": "2020-01-01"}}'

# Provide state via a file.
# The file must contain valid JSON with a top-level key of "singer_state"
# These two lines have the same effect as the one line above.
echo '{"singer_state": {"project_123456_issues": "2020-01-01"}}' > gitlab_state.json
meltano state merge dev:tap-gitlab-to-target-jsonl --input-file gitlab_state.json

# Provide state via existing state.
meltano state merge dev:tap-gitlab-to-target-jsonl --from-state-id prod:tap-gitlab-to-target-jsonl
```

### set

Set state for a job.

#### How to use

```bash
# Read state from a file
# Meltano will prompt for confirmation.
meltano state set <state_id> --input-file <file>

# Read state from a file, overriding confirmation prompt.
meltano state set --force <state_id> --input-file <file>

# Read state from a command-line argument
# Meltano will prompt for confirmation.
meltano state set <state_id> <RAW STATE JSON>

# Read state from a command-line argument, overriding confirmation prompt.
meltano state set --force <state_id> <RAW STATE JSON>
```

#### Parameters

- The `--input-file` option specifies a file to read the state from.
- The `--force` option will disable confirmation prompts. _Use with caution._

#### Examples

```bash
# Provide state via a command-line argument, overriding confirmation prompt.
# The argument must be valid JSON with a top-level key of "singer_state"
# ALL state will be overwritten. Only the "project_123456_issues" bookmark will be used in subsequent runs.
meltano state set --force dev:tap-gitlab-to-target-jsonl '{"singer_state": {"project_123456_issues": "2020-01-01"}}'

# Provide state via a file, overriding confirmation prompt.
# The file must contain valid JSON with a top-level key of "singer_state"
# These two lines have the same effect as the one line above.
echo '{"singer_state": {"project_123456_issues": "2020-01-01"}}' > gitlab_state.json
meltano state set --force dev:tap-gitlab-to-target-jsonl --input-file gitlab_state.json
```

## `test`

Run tests for one or more plugins. A test is any [command](/reference/command-line-interface#commands) with a name starting with `test`.

### How to use

```bash
# Runs all tests for all plugins
meltano test --all

# Run all available tests for one or more selected plugins
meltano test <plugin1> <plugin2>

# Run a named test for a single plugin
meltano test <plugin>:<test-name>

# Run a named test for one or more plugins
meltano test <plugin1>:<test-name1> <plugin2>:<test-name2>
```

## `ui`

- `meltano ui`: Start the Meltano UI.

### `start` (default)

Start the Meltano UI.

### `setup`

<div class="notification is-info">
  <p>This command is only relevant for production-grade setup.</p>
</div>

Generate secrets for the [`ui.secret_key`](/reference/settings#ui-secret-key)
and [`ui.password_salt`](/reference/settings#ui-password-salt) settings, that
will be stored in your project's [`.env` file](/concepts/project#env) along with the
specified value for the [`ui.server_name` setting](/reference/settings#ui-server-name).

In production, you will likely want to move these settings to actual environment variables, since `.env` is in `.gitignore` by default.

<div class="notification is-danger">
  <p><strong>Regenerating secrets will cause the following:</strong></p>
  <p>
    <ul>
      <li>All passwords will be invalid</li>
      <li>All sessions will be expired</li>
    </ul>
  </p>
  <p>Use with caution!</p>
</div>

#### How to use

The `--bits` flag can be used to specify the size of the secrets, default to 256.

```bash
# Format
meltano ui setup [--bits=256] <server_name>

meltano ui setup meltano.example.com
```

## `user`

<div class="notification is-info">
  <p>This command is only relevant when Meltano is run with authentication enabled.</p>
</div>

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
- Update files [managed by](/concepts/plugins#update-extra) [file bundles](/concepts/plugins#file-bundles)
- Apply migrations to [system database](/concepts/project#system-database)

### How to use

```bash
meltano upgrade
meltano upgrade --skip-package # Skip upgrading the Meltano package

meltano upgrade package # Only upgrade Meltano package
meltano upgrade files # Only update files managed by file bundles
meltano upgrade database # Only apply migrations to system database
```

## `version`

It is used to check which version of Meltano currently installed.

### How to use

```bash
meltano --version
```
