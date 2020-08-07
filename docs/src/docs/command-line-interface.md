---
metaTitle: Using the Meltano CLI
description: The Meltano command line interface makes it easy to develop, run, and debug every step of the data analysis lifecycle.
sidebarDepth: 2
---

# Command Line Interface

Meltano provides a command line interface (CLI) that allows you to manage the configuration and orchestration of Meltano projects. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

## `add`

`meltano add` lets you add plugins (extractors, loaders, transforms, models, dashboards, orchestrators, transformers, and file bundles) to your Meltano project.

Specifically, it will:
1. add the plugin to your project's `meltano.yml` file under `plugins: <type>s:`, e.g. `plugins: extractors:`,
2. create a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for the plugin at `.meltano/<type>s/<name>/venv`, e.g. `.meltano/extractors/tap-gitlab/venv`, and
3. install the plugin's [pip package](https://pip.pypa.io/en/stable/) into the virtual environment using `pip install <pip_url>`.

(Some plugin types have slightly different or additional behavior; see [plugin-specific behavior](#plugin-specific-behavior) below for more details.)

Once the plugin has been added to your project, you can configure it using [`meltano config`](#config),
invoke its executable using [`meltano invoke`](#invoke), and use it in a pipeline using [`meltano elt`](#elt).

::: info
Whenever you add a new plugin to a Meltano project, it will be
installed into your project's `.meltano` directory automatically, as described above.

However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in `meltano.yml`.
:::

### How to use: Known plugins

Plugins that are already [known to Meltano](/docs/contributor-guide.html#known-plugins) will show up when you run [`meltano discover`](#discover),
and can be added to your project by simply specifying their `type` and `name`:

```shell
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

```shell
meltano add --include-related extractor tap-gitlab
```

### How to use: Custom plugins

Plugins that Meltano isn't familiar with yet, like arbitrary Singer taps and targets, can be added using the `--custom` flag:

```shell
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19
meltano add --custom loader pipelinewise-target-postgres
```

Since no additional metadata about this plugin will be known to Meltano yet,
it will ask you some additional questions to learn where the plugin's package can be found,
how to interact with it, and how it can be expected to behave: (Note that more context is provided in the actual command prompts.)

```shell
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
Once you've succesfully added your custom plugin to your Meltano project, don't forget to make it [known to Meltano](/docs/contributor-guide.html#known-plugins) to make it easier for other people to install in the future!
:::

### Plugin-specific behavior

#### Transform

Transform plugins are not pip packages, but [dbt packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) containing [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models).

As such, their `pip_url`s point at [dbt packages stored in Git](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages), and they are installed by adding this `git` URL to your project's `transform/packages.yml` and enabling the packaged model in `transform/dbt_project.yml`.

#### Dashboard

Dashboard plugins are pip packages bundling Meltano dashboards and reports.

The bundled dashboards and reports will be added to your project's `analyze` directory automatically as part of installation.

#### Transformer and orchestrator

Transformer and orchestrator plugins have related [file bundles](#file-bundle) that will be added to your project automatically as part of installation.

#### File bundle

File bundle plugins are pip packages bundling files you may want in your Meltano project.

The bundled files will be added to your project automatically as part of installation. The file bundle plugin itself will not be added to `meltano.yml` unless it contains files that are [managed by the file bundle](#file-bundle-extra-update) and to be updated automatically when [`meltano upgrade`](#upgrade) is run.

## `config`

Enables you to manage the configuration of Meltano itself or any of its plugins, as well as [plugin extras](#plugin-extras).

Meltano uses configuration layers to resolve a plugin's configuration:

<!-- The following is reproduced from docs/src/README.md#meltano-config with minor edits. -->

1. **Environment variables**, set through [your shell at `meltano elt` runtime](/docs/command-line-interface.html#pipeline-specific-configuration), a [`.env` file](https://github.com/theskumar/python-dotenv#usages) in your project directory, a [scheduled pipeline](#schedule)'s `env` dictionary in `meltano.yml`, or any other method. You can use `meltano config <plugin> list` to list the available variable names.
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

```shell
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

```shell
meltano config --plugin-type=<type> <plugin> ...
```

#### Nested properties

Nested properties can be set (and unset) by specifying a list of property names:

```shell
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

```shell
meltano config <plugin> list
# => <property>.<subproperty>
# => <property>.<deep>.<nesting>
```

You can also set nested properties using the `.` seperator, but specifying a list of names is preferred
since this will result in the nesting being reflected in the plugin's `config` object in `meltano.yml`:

```shell
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

### Custom settings

Meltano keeps track of the settings a plugin supports using [`settings` metadata](/docs/contributor-guide.html#connector-settings), and will list them all when you run `meltano config <plugin> list`.

If you've [added a custom plugin](#how-to-use-custom-plugins) to your project, you will have been asked provide the names of the supported configuration options yourself.
If the plugin was already [known to Meltano](/docs/contributor-guide.html#known-plugins) when you added it to your project, this metadata will already be known as well.

If a plugin supports a setting that is not yet known to Meltano (because it may have been added after the `settings` metadata was specified, for example),
you do not need to modify the `settings` metadata to be able to use it.

Instead, you can define a custom setting by adding the setting name (key) to your project's `config` object in `meltano.yml` with the desired value (or simply `null`), by manually editing the file or using `meltano config <plugin> set <key> <value>`:

```shell
meltano config tap-example set custom_setting value
```

```yaml
extractors:
- name: tap-example
  pip_url: tap-example
  config:
    known_setting: value
    custom_setting: value
```

As long as the custom setting exists in `meltano.yml`, it will behave and can be interacted with just like any regular (known) setting. It will show up in `meltano config <plugin> list` and `meltano config <plugin>`, and the value that will be passed on to the plugin can be [overridden using an environment variable](#pipeline-specific-configuration):

```shell
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

### Plugin extras

`meltano config` can also be used to manage so-called plugin extras:
additional configuration options specific to the type of plugin (e.g. all extractors)
that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:
- [Extractors](#extractor--loader)
  - [`select`](#extractor-extra-select)
  - [`metadata`](#extractor-extra-metadata)
  - [`schema`](#extractor-extra-schema)
- [Transforms](#transform)
  - [`vars`](#transform-extra-vars)
- [File bundles](#file-bundle)
  - [`update`](#file-bundle-extra-update)

The values of these extras are stored in `meltano.yml` among the plugin's other properties, _outside_ of the `config` object:

```yaml
extractors:
- name: tap-example
  pip_url: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

Extras can be thought of and interacted with as a special kind of setting.

In the context of `meltano config`, extras are distinguished from regular plugin-specific settings using an underscore (`_`) prefix, e.g. `_example_extra`. This also applies in the environment variables that can be used to override them at runtime: since setting names for extras are prefixed with underscores (`_`), they get an extra underscore to separate them from the plugin namespace, e.g. `TAP_EXAMPLE__EXAMPLE_EXTRA`.

By default, `meltano config <plugin>` and `meltano config <plugin> list` only take into account regular plugin settings.
An `--extras` flag can be passed to view or list only extras instead.

Be aware that `meltano config <plugin> reset` resets both regular settings _and_ extras.

```shell
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

### Extractor extra: `select`

- Setting: `_select`
- Environment variable: `<NAMESPACE>__SELECT`
- Default: `["*.*"]`

An [extractor](#extractor--loader)'s `select` [extra](#plugin-extras) holds an array of [entity selection rules](#select)
to apply to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](#elt) or [`meltano invoke`](#invoke).

While this extra can be managed using `meltano config` or environment variables like any other setting,
selection rules are typically specified using [`meltano select`](#select).

#### How to use

##### On the command line

```shell
meltano config <plugin> set _select '["<entity>.<attribute>", ...]'

export <NAMESPACE>__SELECT='["<entity>.<attribute>", ...]'

meltano select <plugin> <entity> <attribute>

# For example:
meltano config tap-gitlab set _select '["project_members.*", "commits.*"]'

export TAP_GITLAB__SELECT='["project_members.*", "commits.*"]'

meltano select tap-gitlab project_members "*"
meltano select tap-gitlab commits "*"
```

##### In `meltano.yml`

```yaml
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  select:
  - project_members.*
  - commits.*
```

### Extractor extra: `metadata`

- Setting: `_metadata`, alias: `metadata`
- Environment variable: `<NAMESPACE>__METADATA`
- Default: `{}` (an empty object)

An [extractor](#extractor--loader)'s `metadata` [extra](#plugin-extras) holds an object describing
[Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
rules to apply to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](#elt) or [`meltano invoke`](#invoke).

Stream (entity) metadata `<key>: <value>` pairs (e.g. `{"replication-method": "INCREMENTAL"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values.
These [nested properties](#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<key>`.

Property (attribute) metadata `<key>: <value>` pairs (e.g. `{"is-replication-key": true}`) are nested under top-level entity identifiers and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<attribute>.<key>`.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](#select).

Like [entity selection rules](#select), metadata rules allow for [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like
patterns in the entity and attribute identifiers to match multiple entities and/or attributes at once.

#### How to use

##### On the command line

```shell
meltano config <plugin> set _metadata <entity> <key> <value>
meltano config <plugin> set _metadata <entity> <attribute> <key> <value>

export <NAMESPACE>__METADATA='{"<entity>": {"<key>": "<value>", "<attribute>": {"<key>": "<value>"}}}'

# Once metadata has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <NAMESPACE>__METADATA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table replication-method INCREMENTAL
meltano config tap-postgres set _metadata some_table replication-key created_at
meltano config tap-postgres set _metadata some_table created_at is-replication-key true

export TAP_POSTGRES__METADATA_SOME_TABLE_REPLICATION_METHOD=FULL_TABLE
```

##### In `meltano.yml`

```yaml
extractors:
- name: tap-postgres
  pip_url: tap-postgres
  metadata:
    some_table:
      replication-method: INCREMENTAL
      replication-key: created_at
      created_at:
        is-replication-key: true
```

### Extractor extra: `schema`

- Setting: `_schema`
- Environment variable: `<NAMESPACE>__SCHEMA`
- Default: `{}` (an empty object)

An [extractor](#extractor--loader)'s `schema` [extra](#plugin-extras) holds an object describing
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) override
rules to apply to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](#elt) or [`meltano invoke`](#invoke).

[JSON Schema](https://json-schema.org/) descriptions for specific properties (attributes) (e.g. `{"type": ["string", "null"], "format": "date-time"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values, and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](#nested-properties) can also be thought of and interacted with as settings named `_schema.<entity>.<attribute>` and `_schema.<entity>.<attribute>.<key>`.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](#select).

Like [entity selection rules](#select), schema rules allow for [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like
patterns in the entity and attribute identifiers to match multiple entities and/or attributes at once.

#### How to use

##### On the command line

```shell
meltano config <plugin> set _schema <entity> <attribute> <schema description>
meltano config <plugin> set _schema <entity> <attribute> <key> <value>

export <NAMESPACE>__SCHEMA='{"<entity>": {"<attribute>": {"<key>": "<value>"}}}'

# Once schema descriptions have been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <NAMESPACE>__SCHEMA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table created_at type '["string", "null"]'
meltano config tap-postgres set _metadata some_table created_at format date-time

export TAP_POSTGRES__SCHEMA_SOME_TABLE_CREATED_AT_FORMAT=date
```

##### In `meltano.yml`

```yaml
extractors:
- name: tap-postgres
  pip_url: tap-postgres
  schema:
    some_table:
      created_at:
        type: ["string", "null"]
        format: date-time
```

### Transform extra: `vars`

- Setting: `_vars`
- Environment variable: `<NAMESPACE>__VARS`
- Default: `{}` (an empty object)

A [transform](#transform)'s `vars` [extra](#plugin-extras) holds an object representing [dbt model variables](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-variables)
that can be referenced from a model using the [`var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/var).

When the transform is installed using [`meltano install`](#install), this object will be used as the dbt model's `vars` object in `transform/dbt_project.yml`.

Because these variables are handled by dbt rather than Meltano, environment variables (including Meltano's [pipeline environment variables](#pipeline-environment-variables)) can be referenced using the [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) instead of `$VAR` or `${VAR}`.

#### How to use

##### On the command line

```shell
meltano config <plugin> set _vars <key> <value>

export <NAMESPACE>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'

```

##### In `meltano.yml`

```yaml
transforms:
- name: tap-gitlab
  pip_url: dbt-tap-gitlab
  vars:
    schema: '{{ env_var(''DBT_SOURCE_SCHEMA'') }}'
```

### File bundle extra: `update`

- Setting: `_update`
- Environment variable: `<NAMESPACE>__UPDATE`
- Default: `{}` (an empty object)

A [file bundle](#file-bundle)'s `update` [extra](#plugin-extras) holds an object mapping file paths (of files inside the bundle, relative to the project root) to booleans.

When a file path's value is `True`, the file is considered to be managed by the file bundle and updated automatically when [`meltano upgrade`](#upgrade) is run.

#### How to use

##### On the command line

```shell
meltano config <plugin> set _update <path> <true/false>

export <NAMESPACE>__UPDATE='{"<path>": <true/false>}'

# For example:
meltano config --plugin-type=files dbt set _update transform/dbt_project.yml false

export DBT__UPDATE='{"transform/dbt_project.yml": false}'
```

##### In `meltano.yml`

```yaml
files:
- name: dbt
  pip_url: files-dbt
  update:
    transform/dbt_project.yml: false
```

## `discover`

Lists the available plugins you are interested in.

### How to Use

```shell
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

```shell
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--job_id TEXT] [--dry]
```

#### Parameters

- The `--transform` option can be:

  - `run`: run the Transforms
  - `skip`: skip the Transforms (Default)
  - `only`: only run the Transforms (skip the Extract and Load steps)

- A `--full-refresh` flag can be passed to perform a full refresh, ignoring the state left behind by any previous runs with the same job ID.

#### Examples

```shell
meltano elt tap-gitlab target-postgres --transform=run --job_id=gitlab-to-postgres
```

### Plugin configuration

Per the [`meltano config` rules](/docs/command-line-interface.html#config), `meltano elt` will determine the configuration of the extractor, loader, and (optionally) transformer by looking in **the environment**, a [**`.env` file**](https://github.com/theskumar/python-dotenv#usages) in your project directory, the [system database](/docs/settings.html#database-uri), and finally your project's **`meltano.yml` file**, falling back to a default value if nothing was found.

You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list all available settings with their names, environment variables, and current values. [`meltano config <plugin>`](/docs/command-line-interface.html#config) will print the current configuration in JSON format.

#### Pipeline-specific configuration

If you'd like to specify (or override) the values of certain settings at runtime, on a per-pipeline basis, you can set them in the `meltano elt` execution environment using [environment variables](https://en.wikipedia.org/wiki/Environment_variable).

This lets you use the same extractors and loaders (Singer taps and targets) in multiple pipelines, configured differently each time.

On a shell, you can explicitly `export` environment variables, that will be passed along to every following command invocation, or you can specify them in-line with a specific invocation, ahead of the command:

```shell
export TAP_FOO_BAR=bar
export TAP_FOO_BAZ=baz
meltano elt ...

TAP_FOO_BAR=bar TAP_FOO_BAZ=baz meltano elt ...
```

To verify that these environment variables will be picked up by Meltano as you intented, you can test them with `meltano config <plugin>` before running `meltano elt`.

If you're using [`meltano schedule`](#schedule) to [schedule your pipelines](/#orchestration), you can specify environment variables for each pipeline in `meltano.yml`, where each entry in the `schedules` array can have an `env` dictionary:

```yaml
schedules:
- name: foo-to-bar
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: '@hourly'
  start_date: 2020-01-01 00:00:00
  env:
    TAP_FOO_BAR: bar
    TAP_FOO_BAZ: baz
```

Different runners and execution/orchestration platforms will have their own way of specifying environment variables along with a command invocation.

Airflow's [`BashOperator`](https://airflow.apache.org/docs/stable/_api/airflow/operators/bash_operator/index.html#airflow.operators.bash_operator.BashOperator), for example, supports an `env` parameter:

```python
BashOperator(
    # ...
    bash_command="meltano elt ...",
    env={
        "TAP_FOO_BAR": "bar",
        "TAP_FOO_BAZ": "baz",
    },
)
```

### Pipeline state

Most extractors (Singer taps) generate [state](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file) when they are run, that can be passed along with a subsequent invocation to have the extractor pick up where it left off the previous time.

Loaders (Singer targets) take in data and state messages from extractors and are responsible for forwarding the extractor state to Meltano once the associated data has been successfully persisted in the destination.

Meltano stores this pipeline state in its [system database](/docs/production.html#storing-metadata), identified by the ELT run's Job ID.

When `meltano elt` is run a subsequent time, it will look for the most recent completed (successful or failed) pipeline run with the same job ID that generated some state. If found, this state is then passed along to the extractor.

::: tip Not seeing state picked up after a failed run?

Some loaders only emit their state once their work is completely done, even if some data may have been persisted already, and if earlier state messages from the extractor could have been forwarded to Meltano. When a pipeline with such a loader fails or is otherwise interrupted, no state will have been emitted yet, and a subsequent ELT run will not be able to pick up where this run actually left off.

:::

### Debugging

If extraction, loading, or transformation is failing, or otherwise not behaving as expected,
you can learn more about what's going on behind the scenes by setting Meltano's
[`cli.log_level` setting](/docs/settings.html#cli-log-level) to `debug`,
using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI flag:

```shell
MELTANO_CLI_LOG_LEVEL=debug meltano elt ...

meltano --log-level=debug elt ...
```

In debug mode, `meltano elt` will log the arguments and environment used to invoke the Singer tap and target executables (and `dbt`, when running transformations), including the paths to the generated config, catalog, and state files, for you to review:

```shell
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

### Pipeline environment variables

To allow loaders and transformers to adapt their configuration and behavior based on the extractor and loader they are run with,
`meltano elt` dynamically sets a number of pipeline-specific environment variables before compiling their configuration and invoking their executables.

In addition to variables [set through the environment](#pipeline-specific-configuration) or a `.env` file in your project directory, the following variables describing the extractor are available to loaders _and_ transformers:

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

## `init`

Used to create a new meltano project with a basic infrastructure in place in the current directory that the user is in.

### How to use

```shell
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

```shell
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

```shell
meltano invoke <plugin> PLUGIN_ARGS...
```

If multiple plugins share the same name, you can provide an additional `--plugin-type` argument to disambiguate:

```shell
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

```shell
# Add a schedule
meltano schedule <schedule_name> <extractor> <loader> <interval> [--transform={run,skip,only}]

# List all schedules
meltano schedule list [--format=json]
```

### Examples

```shell
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

```shell
meltano select tap-carbon-intensity '*' 'name*'
```

This will select all attributes starting with `name`.

```shell
meltano select tap-carbon-intensity 'region'
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

```shell
meltano select --exclude tap-carbon-intensity '*' 'longitude'
```

```shell
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

```shell
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

```shell
meltano user add admin securepassword --role admin
```

## `upgrade`

Upgrade Meltano and the Meltano project to the latest version.

When called without arguments, this will:
- Upgrade the `meltano` package
- Update files [managed by](#file-bundle-extra-update) [file bundles](#file-bundle)
- Apply migrations to system database
- Recompile models

### How to use

```shell
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

```shell
meltano --version
```
