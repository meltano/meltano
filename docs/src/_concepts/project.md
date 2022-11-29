---
title: Projects
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
layout: doc
weight: 1
---

<!-- The following is reproduced in docs/src/README.md#meltano-init -->

At the core of the Meltano experience is your Meltano project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/guide/integration) and [transformed](/guide/transformation),
how the pipelines should be [orchestrated](/guide/orchestration),
and how the various [plugins](#plugins) that make up your pipelines should be [configured](/guide/configuration).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/reference/command-line-interface#init).

## <a name="meltano-yml-project-file"></a>`meltano.yml` project file

At a minimum, a Meltano project must contain a project file named `meltano.yml`,
which contains your project configuration and tells Meltano that a particular directory is a Meltano project.

The only required property is `version`, which currently always holds the value `1`.

### Configuration

At the root of `meltano.yml`, and usually at the top of the file, you will find project-specific configuration.

In a newly initialized project, a few [environments](/concepts/environments) will be populated to get you started.

To learn which settings are available, refer to the [Settings reference](/reference/settings).

### Plugins

Your project's [plugins](/concepts/plugins#project-plugins),
typically [added to your project](/guide/plugin-management#adding-a-plugin-to-your-project)
using [`meltano add`](/reference/command-line-interface#add),
are defined under the `plugins` property, inside an array named after the [plugin type](/concepts/plugins#types) (e.g. `extractors`, `loaders`).

Every plugin in your project needs to have:

1. a `name` that's unique among plugins of the same type,
2. a [base plugin description](/concepts/plugins#project-plugins) describing the package in terms Meltano can understand, and
3. [configuration](/guide/configuration) that can be defined across [various layers](/guide/configuration#configuration-layers), including the definition's [`config` property](#plugin-configuration).

A base plugin description consists of the `pip_url`, `executable`, `capabilities`, and `settings` properties,
but not every plugin definition will specify these explicitly:

- An [**inheriting plugin definition**](#inheriting-plugin-definitions) has an **`inherit_from`** property and inherits its base plugin description from another plugin in your project or a [discoverable plugin](/concepts/plugins#discoverable-plugins) identified by name.
- A [**custom plugin definition**](#custom-plugin-definitions) has a **`namespace`** property instead and explicitly defines its base plugin description.
- A [**shadowing plugin definition**](#shadowing-plugin-definitions) has neither property and implicitly inherits its base plugin description from the [discoverable plugin](/concepts/plugins#discoverable-plugins) with the same **`name`**.

When inheriting a base plugin description, the plugin definition does not need to explicitly specify a `pip_url`
(the package's [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument),
but you may want to override the inherited value and set the property explicitly to [point at a (custom) fork](/guide/plugin-management#using-a-custom-fork-of-a-plugin) or to [pin a package to a specific version](/guide/plugin-management#using-a-custom-fork-of-a-plugin).
When a plugin is added using `meltano add`, the `pip_url` is automatically repeated in the plugin definition for convenience.

In order to support version-specific pip constraint files, the pip_url value can optionally be parameterized using the
`${MELTANO__PYTHON_VERSION}` variable. This is a special variable populated by Meltano with the specific version of Python used to
install the plugin and will inject the major and minor versions (e.g. 3.8, 3.9, etc.).

#### Inheriting plugin definitions

A plugin defined with an `inherit_from` property inherits its [base plugin description](/concepts/plugins#project-plugins) from another plugin identified by name. To find the matching plugin, other plugins in your project are considered first, followed by
[discoverable plugins](/concepts/plugins#discoverable-plugins):

```yml{5,7}
plugins:
  extractors:
  - name: tap-postgres          # Shadows discoverable `tap-postgres` (see below)
  - name: tap-postgres--billing
    inherit_from: tap-postgres  # Inherits from project's `tap-postgres`
  - name: tap-bigquery--events
    inherit_from: tap-bigquery  # Inherits from discoverable `tap-bigquery`
```

When inheriting from another plugin in your project, its [configuration](/guide/configuration) is also inherited as if the values were defaults, which can then be overridden as appropriate:

```yml{10-12,15-18}
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: '2020-10-01T00:00:00Z'
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: '2020-12-01T00:00:00Z' # `start_date` is overridden
      view_id: 789012
```

Note that the presence of a [`variant` property](#variants) causes only discoverable plugins to be considered
(even if there is also a matching plugin in the project),
since only these can have multiple [variants](/concepts/plugins#variants):

```yml{6,8-9}
plugins:
  loaders:
  - name: target-snowflake          # Shadows discoverable `target-snowflake` (see below)
    variant: datamill-co            # using variant `datamill-co`
  - name: target-snowflake--derived
    inherit_from: target-snowflake  # Inherits from project's `target-snowflake`
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake  # Inherits from discoverable `target-snowflake`
    variant: transferwise           # using variant `transferwise`
```

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#plugin-inheritance).

#### Custom plugin definitions

A plugin defined with a `namespace` property (but no `inherit_from` property) is a [custom plugin](/concepts/plugins#custom-plugins) that explicitly defines its [base plugin description](/concepts/plugins#project-plugins):

```yaml{4-14}
plugins:
  extractors:
  - name: tap-covid-19
    namespace: tap_covid_19
    pip_url: tap-covid-19
    executable: tap-covid-19
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: api_token
    - name: user_agent
    - name: start_date
```

To learn how to add a custom plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#custom-plugins).

#### Shadowing plugin definitions

A plugin defined without an `inherit_from` or `namespace` property implicitly inherits its [base plugin description](/concepts/plugins#project-plugins) from the [discoverable plugin](/concepts/plugins#discoverable-plugins) with the same `name`, as a form of [shadowing](https://en.wikipedia.org/wiki/Variable_shadowing):

```yaml{3}
plugins:
  extractors:
  - name: tap-gitlab
```

To learn how to add a discoverable plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#discoverable-plugins).

##### Variants

If multiple [variants](/concepts/plugins#variants) of a discoverable plugin are available,
the `variant` property can be used to choose a specific one:

```yaml{4}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
```

If no `variant` is specified, the _original_ variant supported by Meltano is used.
Note that this is not necessarily the _default_ variant that is recommended to new users and would be used if the plugin were newly added to the project.

#### Plugin configuration

A plugin's [configuration](/guide/configuration) is stored under a `config` property.
Values for [plugin extras](/guide/configuration#plugin-extras) are stored among the plugin's other properties, outside of the `config` object:

```yaml{3-7}
extractors:
- name: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

#### Plugin commands

Plugin [commands](/reference/command-line-interface#commands) are defined by the `commands` property. The keys are the name of the command and the values are the arguments to be passed to the plugin executable. These can contain dynamic references to [configuration](/guide/configuration) using the [Environment variable form](/guide/configuration#environment-variables) of the configuration option.

```yaml{3-7}
transformers:
- name: dbt
  executable: dbt
  commands:
    seed: seed --project-dir $DBT_PROJECT_DIR --profile $DBT_PROFILE --target $DBT_TARGET --select $DBT_MODEL
    snapshot: snapshot --project-dir $DBT_PROJECT_DIR --profile $DBT_PROFILE --target $DBT_TARGET --select $DBT_MODEL
```

Commands can optionally specify some documentation displayed when [listing commands](/reference/command-line-interface#commands). They can also optionally specify an alternative executable from the default one for the plugin.

```yaml
- name: dagster
  executable: dagster
  commands:
    ui:
      description: Start the webserver
      executable: dagit
      args: -w $DAGSTER_HOME/workspace.yaml
    scheduler:
      description: Run the scheduler daemon
      executable: dagster-daemon
      args: run
```

##### Containerized commands

Commands can specify a `container_spec` for containerized execution. To execute containerized commands where possible, use the [`--containers`](/reference/command-line-interface#containerized-commands) flag.

See the full YAML reference for the [container spec](/reference/plugin-definition-syntax#commandscommand_namecontainer_spec) for more information.

### Jobs

Your project's predefined pipelines, typically created using [`meltano job`](/reference/command-line-interface#job), are defined under the `jobs` property.

A job definition must have a `name` and one or more `tasks`:

```yaml
jobs:
  - name: tap-foo-to-target-bar-dbt
    tasks:
      - tap-foo target-bar dbt:run
  - name: tap-foo-to-targets-bar-and-baz
    tasks:
      - tap-foo target-bar
      - tap-foo target-baz
```

You can learn more about how tasks are defined and run in the [`meltano job` documentation](/reference/command-line-interface#job).

### Schedules

Your project's pipeline schedules,
typically [created](/guide/orchestration#create-a-schedule)
using [`meltano schedule`](/reference/command-line-interface#schedule),
are defined under the `schedules` property.

A scheduled job must have a `name`, `job` and `interval`:

```yaml
schedules:
  - name: foo-to-bar
    job: tap-foo-to-target
    interval: "@hourly"
```

The value for `job` must be the name of an existing [job](#jobs) within the project.

Alternatively, you can provide a `name`, `extractor`, `loader`, `transform`, and `interval` in place of a `job`:

```yaml
- name: foo-to-bar-elt
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: @hourly
```

[Pipeline-specific configuration](/guide/integration#pipeline-specific-configuration) can be specified using [environment variables](/guide/configuration#configuring-settings) in an `env` dictionary:

```yaml{7-9}
schedules:
- name: foo-to-bar
  job: tap-foo-to-target-bat
  interval: '@hourly'
  env:
    TAP_FOO_BAR: bar
    TAP_FOO_BAZ: baz
```

To learn more about pipeline schedules and orchestration, refer to the [Orchestration guide](/guide/orchestration).

### Multiple YAML Files

As your project grows, and your `meltano.yml` with it, you may wish to break your config into multiple `.yml` files and to store those subfiles in various places in your Project folder hierachy.

This can be done by creating new `.yml` files and adding them (directly or via a [glob pattern](<https://en.wikipedia.org/wiki/Glob_(programming)>)) to the `include_paths` key of your `meltano.yml`:

```yaml
include_paths:
  - "./subconfig_[0-9].yml"
  - "./*/subconfig_[0-9].yml"
  - "./*/**/subconfig_[0-9].yml"
```

Meltano will use these paths or patterns to collect the config from them for use in your Project. Although the creation of subfiles is manual, once created any elements within each subfile can be updated using the `meltano config` CLI. Adding new config elements places them in `meltano.yml`. We are working on ways to direct new config into specific subfiles ([#2985](https://github.com/meltano/meltano/issues/2925)).

Currently supported elements in subfiles are [plugins](/concepts/project#plugins), [schedules](/concepts/project#plugins) and [environments](/concepts/environments).

## `.gitignore`

A newly initialized project comes with a [`.gitignore` file](https://git-scm.com/docs/gitignore) to ensure that
environment-specific and potentially sensitive [configuration](/guide/configuration) stored inside the
[`.meltano` directory](#meltano-directory) and [`.env` file](#env) is not leaked accidentally.

All other files are recommended to be checked into the repository and shared between all users
and environments that may use the project.

## `.env`

Optionally, your project can contain a [`.env` file](https://github.com/theskumar/python-dotenv#usages) specifying
[environment variables](/guide/configuration#environment-variables)
used to [configure Meltano and its plugins](/guide/configuration#configuring-settings).

Typically, this file is used to store configuration that is environment-specific or sensitive,
and should not be stored in [`meltano.yml`](#meltano-yml-project-file) and checked into version control.

[`meltano config <plugin> set`](/reference/command-line-interface#config) will automatically store configuration in `meltano.yml` or `.env` as appropriate.

In a newly initialized project, this file will be included in [`.gitignore`](#gitignore) by default.

## `.meltano` directory

Meltano stores various files for internal use inside a `.meltano` directory inside your project.

**Note**: `$MELTANO_SYS_DIR_ROOT` can be used as a replacement to `$MELTANO_PROJECT_ROOT/.meltano` directory.

These files are specific to the environment Meltano is running in, and should not be checked into version control.
In a newly initialized project, this directory will be included in [`.gitignore`](#gitignore) by default.

While you would usually not want to modify files in this directory directly, knowing what's in there can aid in debugging:

- `.meltano/meltano.db`: The default SQLite [system database](#system-database).
- `.meltano/logs/elt/<state_id>/<run_id>/elt.log`, e.g. `.meltano/logs/elt/gitlab-to-postgres/<UUID>/elt.log`: [`meltano elt`](/reference/command-line-interface#elt) output logs for the specified pipeline run.
- `.meltano/run/bin`: Symlink to the [`meltano` executable](/reference/command-line-interface) most recently used in this project.
- `.meltano/run/elt/<state_id>/<run_id>/`, e.g. `.meltano/run/elt/gitlab-to-postgres/<UUID>/`: Directory used by [`meltano elt`](/reference/command-line-interface#elt) to store pipeline-specific generated plugin config files, like an [extractor](/concepts/plugins#extractors)'s `tap.config.json`, `tap.properties.json`, and `state.json`.
- `.meltano/run/<plugin name>/`, e.g. `.meltano/run/tap-gitlab/`: Directory used by [`meltano invoke`](/reference/command-line-interface#invoke) to store generated plugin config files.
- `.meltano/<plugin type>/<plugin name>/venv/`, e.g. `.meltano/extractors/tap-gitlab/venv/`: [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) directory that a plugin's [pip package](https://pip.pypa.io/en/stable/) was installed into by [`meltano add`](/reference/command-line-interface#add) or [`meltano install`](/reference/command-line-interface#install).

If `$MELTANO_SYS_DIR_ROOT` is set, all the above mentioned paths `.meltano/*` will point to `$MELTANO_SYS_DIR_ROOT/*`.

## System database

Meltano stores various types of metadata in a project-specific system database,
that takes the shape of a `meltano.db` SQLite database stored inside the [`.meltano` directory](#meltano-directory) by default.
Like all files stored in the `.meltano` directory, the system database is also environment-specific.

You can choose to use a different system database backend or configuration using the [`database_uri` setting](/reference/settings#database-uri).

While you would usually not want to modify the system database directly, knowing what's in there can aid in debugging.

Meltano's CLI utilizes the following tables:

- `runs` table: One row for each [`meltano elt`](/reference/command-line-interface#elt) or [`meltano run`](/reference/command-line-interface#run) pipeline run, holding started/ended timestamps and [incremental replication state](/guide/integration#incremental-replication-state).
- `plugin_settings` table: [Plugin configuration](/guide/configuration#configuration-layers) set using [`meltano config <plugin> set`](/reference/command-line-interface#config) or [the UI](/reference/ui) when the project is [deployed as read-only](/reference/settings#project-readonly).
- `user` table: Users for [the deprecated Meltano UI](/guide/troubleshooting#meltano-ui) created using [`meltano user add`](/reference/command-line-interface#user).

The remaining tables in the database are used exclusively by [Meltano UI](/guide/troubleshooting#meltano-ui), mostly for authentication and authorization purposes:

- `role`
- `role_permissions`
- `oauth`
- `embed_tokens`
- `subscriptions`

### Support for other database types

Meltano currently supports the following databases as backends for state and configuration:

* PostgreSQL
* SQLite
* MS SQL Server

PostgresSQL and SQLite are supported out of the box, while MS SQL Server requires installing Meltano with the [`mssql` Python extra](/guide/advanced-topics#installing-optional-components).

Support for other databases is planned:

* [MySQL](https://github.com/meltano/meltano/issues/6529)

If you would like to see support for a specific database, please [open an issue](https://github.com/meltano/meltano/issues/new?assignees=meltano%2Fengineering&labels=kind%2FFeature%2Cvaluestream%2FMeltano&template=feature.yml&title=feature%3A+%3Ctitle%3E)
