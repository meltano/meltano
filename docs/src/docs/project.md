---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Projects

<!-- The following is reproduced in docs/src/README.md#meltano-init -->

At the core of the Meltano experience is your Meltano project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/docs/integration.html) and [transformed](/docs/transforms.html),
how the pipelines should be [orchestrated](/docs/orchestration.html),
and how the various [plugins](#plugins) that make up your pipelines should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init).

## `meltano.yml` project file

At a minimum, a Meltano project must contain a project file named `meltano.yml`,
which contains your project configuration and tells Meltano that a particular directory is a Meltano project.

The only required property is `version`, which currently always holds the value `1`.

### Configuration

At the root of `meltano.yml`, and usually at the top of the file, you will find project-specific configuration.

In a newly initialized project, only the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats)
will be set.

To learn which settings are available, refer to the [Settings reference](/docs/settings.html).

### Plugins

Your project's [plugins](/docs/plugins.html#project-plugins),
typically [added to your project](/docs/plugin-management.html#adding-a-plugin-to-your-project)
using [`meltano add`](/docs/command-line-interface.html#add),
are defined under the `plugins` property, inside an array named after the [plugin type](/docs/plugins.html#types) (e.g. `extractors`, `loaders`).

Every plugin in your project needs to have:
1. a `name` that's unique among plugins of the same type,
2. a [base plugin description](/docs/plugins.html#project-plugins) describing the package in terms Meltano can understand, and
3. [configuration](/docs/configuration.html) that can be defined across [various layers](/docs/configuration.html#configuration-layers), including the definition's [`config` property](#plugin-configuration).

A base plugin description consists of the `pip_url`, `executable`, `capabilities`, and `settings` properties,
but not every plugin definition will specify these explicitly:

- An [**inheriting plugin definition**](#inheriting-plugin-definitions) has an **`inherit_from`** property and inherits its base plugin description from another plugin in your project or a [discoverable plugin](/docs/plugins.html#discoverable-plugins) identified by name.
- A [**custom plugin definition**](#custom-plugin-definitions) has a **`namespace`** property instead and explicitly defines its base plugin description.
- A [**shadowing plugin definition**](#shadowing-plugin-definitions) has neither property and implicitly inherits its base plugin description from the [discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same **`name`**.

When inheriting a base plugin description, the plugin definition does not need to explicitly specify a `pip_url`
(the package's [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument),
but you may want to override the inherited value and set the property explicitly to [point at a (custom) fork](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin) or to [pin a package to a specific version](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin#pinning-a-plugin-to-a-specific-version).
When a plugin is added using `meltano add`, the `pip_url` is automatically repeated in the plugin definition for convenience.

In order to support version-specific pip constraint files, the pip_url value can optionally be parameterized using the
`${MELTANO__PYTHON_VERSION}` variable. This is a special variable populated by Meltano with the specific version of Python used to
install the plugin and will inject the major and minor versions (e.g. 3.8, 3.9, etc.).

#### Inheriting plugin definitions

A plugin defined with an `inherit_from` property inherits its [base plugin description](/docs/plugins.html#project-plugins) from another plugin identified by name. To find the matching plugin, other plugins in your project are considered first, followed by
[discoverable plugins](/docs/plugins.html#discoverable-plugins):

```yml{5,7}
plugins:
  extractors:
  - name: tap-postgres          # Shadows discoverable `tap-postgres` (see below)
  - name: tap-postgres--billing
    inherit_from: tap-postgres  # Inherits from project's `tap-postgres`
  - name: tap-bigquery--events
    inherit_from: tap-bigquery  # Inherits from discoverable `tap-bigquery`
```

When inheriting from another plugin in your project, its [configuration](/docs/configuration.html) is also inherited as if the values were defaults, which can then be overridden as appropriate:

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
since only these can have multiple [variants](/docs/plugins.html#variants):

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

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#plugin-inheritance).

#### Custom plugin definitions

A plugin defined with a `namespace` property (but no `inherit_from` property) is a [custom plugin](/docs/plugins.html#custom-plugins) that explicitly defines its [base plugin description](/docs/plugins.html#project-plugins):

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

To learn how to add a custom plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).

#### Shadowing plugin definitions

A plugin defined without an `inherit_from` or `namespace` property implicitly inherits its [base plugin description](/docs/plugins.html#project-plugins) from the [discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same `name`, as a form of [shadowing](https://en.wikipedia.org/wiki/Variable_shadowing):

```yaml{3}
plugins:
  extractors:
  - name: tap-gitlab
```

To learn how to add a discoverable plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#discoverable-plugins).

##### Variants

If multiple [variants](/docs/plugins.html#variants) of a discoverable plugin are available,
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

A plugin's [configuration](/docs/configuration.html) is stored under a `config` property.
Values for [plugin extras](/docs/configuration.html#plugin-extras) are stored among the plugin's other properties, outside of the `config` object:

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

Plugin [commands](/docs/command-line-interface.html#commands) are defined by the `commands` property. The keys are the name of the command and the values are the arguments to be passed to the plugin executable. These can contain dynamic references to [configuration](/docs/configuration.html) using the [Environment variable form](/docs/configuration.html#environment-variables) of the configuration option.

```yaml{3-7}
transformers:
- name: dbt
  executable: dbt
  commands:
    seed: seed --project-dir $DBT_PROJECT_DIR --profile $DBT_PROFILE --target $DBT_TARGET --select $DBT_MODEL
    snapshot: snapshot --project-dir $DBT_PROJECT_DIR --profile $DBT_PROFILE --target $DBT_TARGET --select $DBT_MODEL
```

Commands can optionally specify some documentation displayed when [listing commands](/docs/command-line-interface.html#commands). They can also optionally specify an alternative executable from the default one for the plugin.

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

### Schedules

Your project's pipeline schedules,
typically [created](/docs/orchestration.html#create-a-schedule)
using [`meltano schedule`](/docs/command-line-interface.html#schedule),
 are defined under the `schedules` property.

A schedule definition must have a `name`, `extractor`, `loader`, `transform` and `interval`:

```yaml
schedules:
- name: foo-to-bar
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: '@hourly'
```

[Pipeline-specific configuration](/docs/integration.html#pipeline-specific-configuration) can be specified using [environment variables](/docs/configuration.html#configuring-settings) in an `env` dictionary:

```yaml{7-9}
schedules:
- name: foo-to-bar
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: '@hourly'
  env:
    TAP_FOO_BAR: bar
    TAP_FOO_BAZ: baz
```

To learn more about pipeline schedules and orchestration, refer to the [Orchestration guide](/docs/orchestration.html).

### Multiple YAML Files

As your project grows, and your `meltano.yml` with it, you may wish to break your config into multiple `.yml` files and to store those subfiles in various places in your Project folder hierachy.

This can be done by creating new `.yml` files and adding them (directly or via a [glob pattern](https://en.wikipedia.org/wiki/Glob_(programming))) to the `include_paths` key of your `meltano.yml`:

```yaml
include_paths:
  - './subconfig_[0-9].yml'
  - './*/subconfig_[0-9].yml'
  - './*/**/subconfig_[0-9].yml'
```

Meltano will use these paths or patterns to collect the config from them for use in your Project. Although the creation of subfiles is manual, once created any elements within each subfile can be updated using the `meltano config` CLI. Adding new config elements places them in `meltano.yml`. We are working on ways to direct new config into specific subfiles ([#2985](https://gitlab.com/meltano/meltano/-/issues/2985)).

Currently supported elements in subfiles are [plugins](/docs/projects.html#plugins), [schedules](/docs/projects.html#plugins) and [environments](/docs/environments.html).

## `.gitignore`

A newly initialized project comes with a [`.gitignore` file](https://git-scm.com/docs/gitignore) to ensure that
environment-specific and potentially sensitive [configuration](/docs/configuration.html) stored inside the
[`.meltano` directory](#meltano-directory) and [`.env` file](#env) is not leaked accidentally.

All other files are recommended to be checked into the repository and shared between all users
and environments that may use the project.

## `.env`

Optionally, your project can contain a [`.env` file](https://github.com/theskumar/python-dotenv#usages) specifying
[environment variables](/docs/configuration.html#environment-variables)
used to [configure Meltano and its plugins](/docs/configuration.html#configuring-settings).

Typically, this file is used to store configuration that is environment-specific or sensitive,
and should not be stored in [`meltano.yml`](#meltano-yml-project-file) and checked into version control.

[`meltano config <plugin> set`](/docs/command-line-interface.html#config) will automatically store configuration in `meltano.yml` or `.env` as appropriate.

In a newly initialized project, this file will be included in [`.gitignore`](#gitignore) by default.

## `.meltano` directory

Meltano stores various files for internal use inside a `.meltano` directory inside your project.

These files are specific to the environment Meltano is running in, and should not be checked into version control.
In a newly initialized project, this directory will be included in [`.gitignore`](#gitignore) by default.

While you would usually not want to modify files in this directory directly, knowing what's in there can aid in debugging:

- `.meltano/meltano.db`: The default SQLite [system database](#system-database).
- `.meltano/logs/elt/<job_id>/<run_id>/elt.log`, e.g. `.meltano/logs/elt/gitlab-to-postgres/<UUID>/elt.log`: [`meltano elt`](/docs/command-line-interface.html#elt) output logs for the specified pipeline run.
- `.meltano/run/bin`: Symlink to the [`meltano` executable](/docs/command-line-interface.html) most recently used in this project.
- `.meltano/run/elt/<job_id>/<run_id>/`, e.g. `.meltano/run/elt/gitlab-to-postgres/<UUID>/`: Directory used by [`meltano elt`](/docs/command-line-interface.html#elt) to store pipeline-specific generated plugin config files, like an [extractor](/docs/plugins.html#extractors)'s `tap.config.json`, `tap.properties.json`, and `state.json`.
- `.meltano/run/<plugin name>/`, e.g. `.meltano/run/tap-gitlab/`: Directory used by [`meltano invoke`](/docs/command-line-interface.html#invoke) to store generated plugin config files.
- `.meltano/<plugin type>/<plugin name>/venv/`, e.g. `.meltano/extractors/tap-gitlab/venv/`: [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) directory that a plugin's [pip package](https://pip.pypa.io/en/stable/) was installed into by [`meltano add`](/docs/command-line-interface.html#add) or [`meltano install`](/docs/command-line-interface.html#install).

## System database

Meltano stores various types of metadata in a project-specific system database,
that takes the shape of a `meltano.db` SQLite database stored inside the [`.meltano` directory](#meltano-directory) by default.
Like all files stored in the `.meltano` directory, the system database is also environment-specific.

You can choose to use a different system database backend or configuration using the [`database_uri` setting](/docs/settings.html#database-uri).

While you would usually not want to modify the system database directly, knowing what's in there can aid in debugging:

- `job` table: One row for each [`meltano elt`](/docs/command-line-interface.html#elt) pipeline run, holding started/ended timestamps and [incremental replication state](/docs/integration.html#incremental-replication-state).
- `plugin_settings` table: [Plugin configuration](/docs/configuration.html#configuration-layers) set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/ui.html) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
- `user` table: Users for [Meltano UI](/docs/ui.html) created using [`meltano user add`](/docs/command-line-interface.html#user).
