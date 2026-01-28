---
title: Plugin Definition Syntax
description: YAML syntax for defining plugins for Meltano Hub.
layout: doc
sidebar_position: 3
---

This document describes the syntax for defining plugins contributed to Meltano Hub.

## `name`

Required. The name of the plugin. The tuple `(name, variant)` must be unique.

```yaml
name: airflow
```

## `variant`

Required. The name of the variant. New variants of existing plugins usually come form forks or re-implementations.

```yaml
variant: apache
```

## `namespace`

Required. This is used to configure multiple plugins that are meant to work together.

```yaml
namespace: airflow
```

## `label`

A human-readable label for the plugin.

```yaml
label: Airflow
```

## `description`

A brief description of what the tool, API, or file is used for.

An example description for Salesforce:

```yaml
description: Customer-relationship management & customer success platform
```

## `docs`

The URL of the plugin's documentation.

```yaml
docs: https://docs.meltano.com/guide/orchestration
```

## `repo`

The URL of the plugin's repository (in GitHub, GitLab, etc.). In the case of extensions
wrapping another application this should point the applications repository, not the extensions.

```yaml
repo: https://github.com/apache/airflow
```

## `ext_repo`

The URL of the plugin's extension repository itself (in GitHub, GitLab, etc.).

```yaml
ext_repo: https://github.com/meltano/airflow-ext
```

## `executable`

The default executable to call when invoking plugin commands.

```yaml
executable: airflow_invoker
```

## `capabilities`

Array of capabilities that the plugin supports. For example:

```yaml
capabilities:
- catalog
- discover
- state
```

The capabilities vary by plugin type. Below are the capabilities organized by type.

### Extractor capabilities

- [`catalog`](#catalog-capability)
- [`properties`](#properties-capability)
- [`discover`](#discover-capability)
- [`state`](#state-capability)
- [`about`](#about-capability)
- [`stream-maps`](#stream-maps-capability)
- [`activate-version`](#activate-version-capability)
- [`batch`](#batch-capability)
- [`test`](#test-capability)
- [`log-based`](#log-based-capability)
- [`schema-flattening`](#schema-flattening-capability)
- [`structured-logging`](#structured-logging-capability)

### Loader capabilities

- [`about`](#about-capability)
- [`stream-maps`](#stream-maps-capability)
- [`activate-version`](#activate-version-capability)
- [`batch`](#batch-capability)
- [`soft-delete`](#soft-delete-capability)
- [`hard-delete`](#hard-delete-capability)
- [`datatype-failsafe`](#datatype-failsafe-capability)
- [`schema-flattening`](#schema-flattening-capability)
- [`structured-logging`](#structured-logging-capability)

### Mapper capabilities

- [`about`](#about-capability)
- [`stream-maps`](#stream-maps-capability)
- [`structured-logging`](#structured-logging-capability)

### `catalog` capability

Declares that the plugin supports stream and property selection using the `--catalog` CLI argument, which is a newer version of the [`--properties` capability](#properties-capability).

Note: The `catalog` capability is a newer version of the [`properties` capability](#properties-capability). Singer taps which support field and stream selection logic should declare the `properties` or `catalog` capability, but not both.

### `properties` capability

Declares that the plugin supports stream and property selection using the `--properties` CLI argument.

Note: The `properties` capability is an older version of the [`--catalog` capability](#catalog-capability). Singer taps which support field and stream selection logic should declare the `properties` or `catalog` capability, but not both.

### `discover` capability

Declares that the plugin can be run with the `--discover` CLI argument, which generates a `catalog.json` file. This is used by Meltano in combination with the `catalog` or `properties` capability to customize the catalog and to apply selection logic.

### `state` capability

Declares that the plugin is able to perform incremental processing using the `--state` CLI option.

Note: This capability must be declared in order to use incremental data replication.

### `about` capability

Declares that the plugin supports a `--about` CLI argument and a paired `--format=json` to optionally print the plugin's metadata in a machine readable format. This capability can be used by users to better understand the capabilities and settings expected by the plugin. It may also be used by Meltano and MeltanoHub codebase to auto-detect behaviors and capabilities.

### `stream-maps` capability

For Singer connectors, declares the ability to perform inline transformations or 'mappings' within the stream. For more details, please see the [Singer SDK Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html) documentation.

### `activate-version` capability

Declares that the plugin supports the `ACTIVATE_VERSION` message type, which is used to indicate that all records for a stream have been sent and any records not seen should be soft-deleted.

### `batch` capability

Declares that the plugin supports batch processing of records, allowing for more efficient data transfer by grouping records together.

### `test` capability

Declares that the plugin supports a `--test` CLI argument for testing connectivity and configuration without performing a full sync.

### `log-based` capability

For extractors only. Declares that the plugin supports log-based replication (e.g., using database change data capture).

### `schema-flattening` capability

Declares that the plugin supports schema flattening, which can flatten nested objects into separate columns.

### `structured-logging` capability

Declares that the plugin outputs structured logs (typically JSON format) that can be parsed and processed by Meltano.

### `soft-delete` capability

For loaders only. Declares that the plugin supports soft deletion of records (marking records as deleted without physically removing them).

### `hard-delete` capability

For loaders only. Declares that the plugin supports hard deletion of records (physically removing records from the destination).

### `datatype-failsafe` capability

For loaders only. Declares that the plugin has failsafe handling for data type mismatches, allowing ingestion to continue even when encountering unexpected data types.

## `pip_url`

A string with the plugin's [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/#options) argument. Can point to multiple packages and include any of the pip install options.

```yaml
pip_url: apache-airflow==2.10.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${MELTANO__PYTHON_VERSION}.txt
```

## `python`

The Python version or path to use for this plugin. Can be specified as a version number (e.g., `3.11`), a path to an executable (e.g., `/usr/bin/python3.10`), or an executable name to find within `$PATH` (e.g., `python3.11`).

If not specified, the Python executable that was used to run Meltano will be used (within a separate virtual environment).

```yaml
python: "3.11"
```

```yaml
python: /usr/bin/python3.10
```

## `supported_python_versions`

Optional. An array of Python versions that this plugin supports. This is used by Meltano to automatically select a compatible Python version when the plugin is not compatible with Meltano's own Python version.

```yaml
supported_python_versions:
- "3.10"
- "3.11"
- "3.12"
```

## `maintenance_status`

The maintenance status of the plugin. See the [JSON schema](https://github.com/meltano/hub/blob/main/schemas/plugin_definitions/hub_metadata.schema.json) for the most up-to-date list of maintenance statuses.

```yaml
maintenance_status: active  # allowed values: active, beta, development, inactive, deprecated, unknown
```

## `domain_url`

The URL of the plugin's domain.

```yaml
domain_url: https://ads.google.com
```

## `logo_url`

Path to the plugin's logo in the Meltano Hub repository.

```yaml
logo_url: /assets/logos/utilities/airflow.png
```

## `definition`

Markdown formatted text that defines what the plugin is and what it does.

```yaml
definition: is an [utilities](/concepts/plugins#utilities) that allows for workflows to be programmatically authored, scheduled, and monitored via Airflow.
```

## `settings_preamble`

Text to display before the settings in Meltano Hub, in Markdown format.

```yaml
settings_preamble: |
  Meltano [centralizes the configuration](https://docs.meltano.com/guide/configuration) of all of the plugins in your project, including Airflow's. This means that if the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html) tells you to put something in `airflow.cfg`, you can use `meltano config`, `meltano.yml`, or environment variables instead, and get the benefits of Meltano features like [environments](https://docs.meltano.com/concepts/environments).

  Any setting you can add to `airflow.cfg` can be added to `meltano.yml`, manually or using `meltano config`. For example, `[core] executor = SequentialExecutor` becomes `meltano config set airflow core executor SequentialExecutor` on the CLI, or `core.executor: SequentialExecutor` in `meltano.yml`. Config sections indicated by `[section]` in `airflow.cfg` become nested dictionaries in `meltano.yml`.
```

## `next_steps`

Documentation for the next steps after installing the plugin, in Markdown format.

````yaml
next_steps: |
  1. Use the [meltano schedule](https://docs.meltano.com/reference/command-line-interface#schedule) command to create pipeline schedules in your project, to be run by Airflow.

  1. If you're running Airflow for the first time in a new environment, create an admin user:

     ```sh
     meltano invoke airflow:create-admin
     # This is equivalent to `airflow users create` with some arguments in the Airflow documentation
     ```

  1. Launch the Airflow UI and log in using the username/password you created:

     ```sh
     meltano invoke airflow:ui
     ```

     By default, the UI will be available at at [`http://localhost:8080`](http://localhost:8080). You can change this using the `webserver.web_server_port` setting documented below.

  1. Start Scheduler or execute Airflow commands directly using the instructions in [the Meltano docs](https://docs.meltano.com/guide/orchestration#starting-the-airflow-scheduler).
````

## `usage`

Free text describing how to use the plugin, in Markdown format.

```yaml
usage: |
  ## Troubleshooting

  ### Error: `pg_config executable not found` or `libpq-fe.h: No such file or directory`

  This error message indicates that the [`libpq`](https://www.postgresql.org/docs/current/libpq.html) dependency is missing.

  To resolve this, refer to the ["Dependencies" section](#dependencies) above.
```

## `keywords`

Array of arbitrary keywords associated with the plugin, for search and classification purposes.

```yaml
keywords:
- api
- meltano_sdk
```

## `requires`

Other plugins that this plugin depends on.

Example:

```yaml
requires:
  files:
  - name: files-airflow
    variant: meltano
```

### `requires.<plugin_type>[*].name`

See the full in the [`requires` section](#requires) above.

### `requires.<plugin_type>[*].variant`

See the full in the [`requires` section](#requires) above.

## `requires_meltano`

Optional. A version specifier for the Meltano version required by this plugin. If the version of Meltano being used does not satisfy this requirement, Meltano will exit with an error when attempting to invoke the plugin.

This field uses the same syntax as Python package version specifiers and supports complex version requirements.

Examples:

```yaml
# Require Meltano 3.0 or higher
requires_meltano: ">=3.0.0"

# Require Meltano 3.x (3.0 or higher, but less than 4.0)
requires_meltano: ">=3.0.0,<4.0.0"

# Require exactly Meltano 3.5.0
requires_meltano: "==3.5.0"

# Require Meltano 3.6 or higher, but less than 3.8
requires_meltano: ">=3.6.0,<3.8.0"
```

Note: This field should only be present in plugin lockfiles, not in `meltano.yml` for plugins from Meltano Hub. It is primarily used by the Hub to indicate compatibility requirements for specific plugin versions.

## `commands`

The [commands](/concepts/project#plugin-commands) that are available for this plugin.

Example:

```yaml
commands:
  create-admin:
    args: "users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.org"
    description: Create an admin user.
  ui:
    args: webserver
    description: Start the Airflow webserver.
```

### `commands.<command_name>.args`

Command line arguments for the command.

### `commands.<command_name>.description`

Friendly description of the command.

### `commands.<command_name>.executable`

Optionally, override the plugin's default `executable` when running this command.

### `commands.<command_name>.container_spec`

The container specification to use for the command.

Example:

```yaml
- name: dbt
  pip_url: dbt-core~=1.0.1 dbt-postgres~=1.0.1
  commands:
    compile:
      args: compile
      container_spec:
        command: compile
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
        - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
    docs-generate:
      args: docs generate
      container_spec:
        command: docs generate
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
         - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
    docs-serve:
      args: docs serve
      container_spec:
        command: docs serve --no-browser
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
        - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
        ports:
          "8080": "8080/tcp"
```

Use this with [`meltano invoke`](/reference/command-line-interface#containerized-commands) to run commands in a container.

#### `commands.<command_name>.container_spec.image`

The Docker image to use for the command.

#### `commands.<command_name>.container_spec.command`

The command to run in the container.

#### `commands.<command_name>.container_spec.entrypoint`

The container entrypoint to use for the command.

#### `commands.<command_name>.container_spec.ports`

Mapping of host ports to container ports.

#### `commands.<command_name>.container_spec.volumes`

An array of host volumes to mount in the container.

#### `commands.<command_name>.container_spec.env`

A mapping of environment variables to set in the container.

## `settings_group_validation`

An array of arrays listing the minimal valid group of settings required to use the connector. A common use case is defining which settings are required for different authorization methods.

An example definition for Redshift where there are 3 types of authorization available:

```yaml
settings_group_validation:
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_profile
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_access_key_id
  - aws_secret_access_key
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_session_token
```

## `settings`

Each plugin variant in Meltano Hub has a `settings` property. Nested under this property are a variable amount of individual settings. To improve the UX of this form, each setting has a number of optional properties.

Example:

```yaml
settings:
- name: core.dags_folder
  label: DAGs Folder
  value: $MELTANO_PROJECT_ROOT/orchestrate/dags
  env: AIRFLOW__CORE__DAGS_FOLDER
- name: core.plugins_folder
  label: Plugins Folder
  value: $MELTANO_PROJECT_ROOT/orchestrate/plugins
  env: AIRFLOW__CORE__PLUGINS_FOLDER
```

### `settings[*].name`

Required. The name of the setting.

```yaml
settings:
- name: setting_name
```

### `settings[*].aliases`

Optional. An array of aliases for the setting.

An alias is an alternative setting name that can be used in 'meltano.yml' and 'meltano config set'. For example,

```yaml
plugins:
- name: target-rdbms
  settings:
  - name: dbname
    aliases:
    - database
    - database_name
```

means that, along with the `TARGET_RDBMS_DBNAME` environment variable, the `target-rdbms` plugin also supports the `TARGET_RDBMS_DATABASE` and `TARGET_RDBMS_DATABASE_NAME` environment variables for the same setting. It also means that the `dbname` setting can be used in `meltano.yml` and `meltano config set` using the `database` and `database_name` aliases.

### `settings[*].description`

Optional. Use to provide inline contextual help for the setting.

```yaml
settings:
- name: setting_name
  description: |
    This is a setting description.
```

### `settings[*].documentation`

Optional. Use to provide a link to external supplemental documentation for the setting.

```yaml
settings:
- name: setting_name
  documentation: https://docs.meltano.com/reference/configuration#setting_name
```

### `settings[*].env`

Meltano takes the value of the setting and injects it into the plugin's runtime environment as this environment variable, in addition to the default environment variable (of the form `<PLUGIN_NAME>_<SETTING_NAME>`, etc.).

For example, the following setting definition:

```yaml
settings:
- name: setting_name
  env: SOME_API_KEY
```

will result in the plugin being able to access the value of the setting via the `SOME_API_KEY` environment variable.

### `settings[*].hidden`
Optional. Use to hide a setting.

```yaml
settings:
- name: setting_name
  hidden: true
```

### `settings[*].kind`

Optional. Use for a first-class input control. Default is `string`. Supported values are:

- `string` - A text string (default)
- `integer` - An integer number
- `boolean` - A true/false value
- `decimal` - A decimal number
- `date_iso8601` - An ISO 8601 formatted date
- `email` - An email address
- `file` - A file path
- `array` - An array of values
- `object` - A nested object
- `options` - A selection from predefined options (use with [`options`](#settingsoptions))

```yaml
settings:
- name: setting_name
  kind: integer
```

:::caution
  <p><code>kind: hidden</code> is deprecated in favour of <a href="#settingshidden"><code>hidden: true</code></a>.</p>
  <p><code>kind: password</code> is deprecated in favour of <a href="#settingssensitive"><code>sensitive: true</code></a>.</p>
:::

:::tip
  <p>Starting with Meltano v3.7, settings of kind `date_iso8601` can have relative date values, like `3 days ago`, `yesterday`, `last week`, etc.</p>
:::

### `settings[*].label`

Optional. Human-friendly text display of the setting name.

```yaml
settings:
- name: setting_name
  label: Setting Name
```

### `settings[*].placeholder`

Optional. Use to set the input's placeholder default.

### `settings[*].sensitive`
Optional. Use to mark a setting as sensitive (e.g. a password, token or code).

```yaml
settings:
- name: setting_name
  kind: string
  sensitive: true
```

### `settings[*].tooltip`

Optional. Use to provide a tooltip for the setting when rendered within a UI that supports tooltips.

```yaml
settings:
- name: setting_name
  tooltip: Here is some more info...
```

### `settings[*].value`

Optional. Use to set a default value for the setting

```yaml
settings:
- name: setting_name
  value: default_value
```

### `settings[*].options`

Optional. Use with `kind: options` to define the available choices for the setting. Each option has a `label` for display and a `value` for the actual configuration value.

```yaml
settings:
- name: output_format
  kind: options
  label: Output Format
  description: The format of the output file.
  options:
  - label: JSON
    value: json
  - label: CSV
    value: csv
  - label: Parquet
    value: parquet
```

### `settings[*].value_processor`

Optional. A pre-processor to apply to the setting value before it is used. Used primarily with `kind: object` to transform keys.

Available processors:
- `nest_object` - Convert a flat object with period-delimited keys to a nested object
- `upcase_string` - Convert the setting value to uppercase

```yaml
settings:
- name: config
  kind: object
  value_processor: nest_object
```

### `settings[*].value_post_processor`

Optional. A post-processor to apply to the setting value after it is resolved.

Available processors:
- `nest_object` - Convert a flat object with period-delimited keys to a nested object
- `upcase_string` - Convert the setting value to uppercase
- `stringify` - Convert the JSON object to a string
- `parse_date` - Parse the setting value as a date

```yaml
settings:
- name: start_date
  kind: date_iso8601
  value_post_processor: parse_date
```

## `env`

Optional. Environment variables that will be used when [expanding environment variables in lower levels within your project's configuration](../guide/configuration#expansion-in-setting-values), and when running the plugin. These environment variables can make use of other environment variables from higher levels [as explained in the configuration guide](../guide/configuration#environment-variable-expansion).

```yaml
env:
  ENV_VAR_NAME: env var value
  PATH: "${PATH}:${MELTANO_PROJECT_ROOT}/bin"
```

## Plugin Type-Specific Attributes

The following attributes are specific to certain plugin types.

### Loader-specific attributes

#### `dialect`

For loaders only. The name of the dialect of the target database. This is used so that transformers in the same pipeline can determine the type of database to connect to.

```yaml
dialect: postgres
```

### Mapper-specific attributes

#### `mappings`

For mappers only. An array of named mapping configurations that can be invoked. Each mapping has a `name` and a `config` object.

```yaml
mappings:
- name: hash-emails
  config:
    stream_maps:
      users:
        email: fake("email")
- name: remove-pii
  config:
    stream_maps:
      users:
        __filter__: record["country"] == "US"
```

### Transform-specific attributes (dbt)

#### `vars`

For dbt transform plugins only. An object containing dbt model variables that will be passed to dbt.

```yaml
vars:
  my_variable: my_value
  another_variable: 123
```

#### `package_name`

For dbt transform plugins only. The name of the dbt package's internal dbt project (the value of `name` in `dbt_project.yml`).

```yaml
package_name: my_dbt_project
```
