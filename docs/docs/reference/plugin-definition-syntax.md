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

The full list of defined capabilities is below:

- [`catalog`](#catalog-capability)
- [`properties`](#properties-capability)
- [`discover`](#discover-capability)
- [`state`](#state-capability)
- [`about`](#about-capability)
- [`stream-maps`](#stream-maps-capability)

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

## `pip_url`

A string with the plugin's [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/#options) argument. Can point to multiple packages and include any of the pip install options.

```yaml
pip_url: apache-airflow==2.10.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${MELTANO__PYTHON_VERSION}.txt
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

  Any setting you can add to `airflow.cfg` can be added to `meltano.yml`, manually or using `meltano config`. For example, `[core] executor = SequentialExecutor` becomes `meltano config airflow set core executor SequentialExecutor` on the CLI, or `core.executor: SequentialExecutor` in `meltano.yml`. Config sections indicated by `[section]` in `airflow.cfg` become nested dictionaries in `meltano.yml`.
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

Optional. Use for a first-class input control. Default is `string`, others are `integer`, `boolean`, `decimal`, `date_iso8601`, `options`, `file`, `array`, and `object`.

```yaml
settings:
- name: setting_name
  kind: integer
```

```yaml
settings:
- name: setting_name
  env: SOME_API_KEY
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

## `env`

Optional. Environment variables that will be used when [expanding environment variables in lower levels within your project's configuration](../guide/configuration#expansion-in-setting-values), and when running the plugin. These environment variables can make use of other environment variables from higher levels [as explained in the configuration guide](../guide/configuration#environment-variable-expansion).

```yaml
env:
  ENV_VAR_NAME: env var value
  PATH: "${PATH}:${MELTANO_PROJECT_ROOT}/bin"
```
