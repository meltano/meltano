---
title: Plugin Definition Syntax
description: YAML syntax for defining plugins for Meltano Hub.
layout: doc
weight: 3
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

## `docs`

The URL of the plugin's documentation.

```yaml
docs: https://docs.meltano.com/guide/orchestration
```

## `repo`

The URL of the plugin's repository (in GitHub, GitLab, etc.).

```yaml
repo: https://github.com/apache/airflow
```

## `capabilities`

Array of capabilities that the plugin supports.

```yaml
capabilities:
- catalog
- discover
- state
- about
- stream-maps
```

## `pip_url`

A string with the plugin's [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/#options) argument. Can point to multiple packages and include any of the pip install options.

```yaml
pip_url: apache-airflow==2.1.2 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.1.2/constraints-${MELTANO__PYTHON_VERSION}.txt
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
logo_url: /assets/logos/orchestrators/airflow.png
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

```yaml
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
```

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

### `requires.<plugin_type>.name`

### `requires.<plugin_type>.variant`

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

## `settings`

Each plugin variant in Meltano Hub has a `settings` property. Nested under this property are a variable amount of individual settings. In the Meltano UI these settings are parsed to generate a configuration form. To improve the UX of this form, each setting has a number of optional properties.

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

```yaml
settings:
- name: setting_name
  aliases:
  - setting_name_alias
  - setting_name_alias_2
```

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

Use to delegate to an environment variable for overriding this setting's value.

### `settings[*].kind`

Optional. Use for a first-class input control. Default is `string`, others are `integer`, `boolean`, `date_iso8601`, `password`, `options`, `file`, `array`, `object`, and `hidden`.

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

### `settings[*].label`

Optional. Human-friendly text display of the setting name.

```yaml
settings:
- name: setting_name
  label: Setting Name
```

### `settings[*].placeholder`

Optional. Use to set the input's placeholder default.

### `settings[*].protected`

Optional. Use in combination with [`value`](#settingsvalue) to provide an uneditable default in the UI.

```yaml
settings:
- name: setting_name
  protected: true
```

### `settings[*].tooltip`

Optional. Use to provide a tooltip for the setting in the Meltano UI.

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
