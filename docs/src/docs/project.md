---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Projects

<!-- The following is reproduced in docs/src/README.md#meltano-init -->

At the core of the Meltano experience is your Meltano project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/docs/integration.html) and [transformed](/docs/transforms.html),
how the pipelines should be [orchestrated](/docs/orchestration.html),
and how the various components should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init).

## `meltano.yml` project file

At a minimum, a Meltano project must contain a project file named `meltano.yml`,
which contains your project configuration and tells Meltano that a particular directory is a Meltano project.

The only required key is `version`, which currently always holds the value `1`.

### Configuration

At the root of `meltano.yml`, and usually at the top of the file, you will find project-specific configuration.

In a newly initialized project, only the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats)
will be set.

To learn which settings are available, refer to the [Settings reference](/docs/settings.html).

### Plugins

Definitions of [plugins](/docs/plugins.html) you've [added to your project](/docs/plugin-management.html#adding-extractors-and-loaders-to-your-project)
using [`meltano add`](/docs/command-line-interface.html#add)
are stored under the `plugins` key, nested under a key named after the plugin type (e.g. `extractors`, `loaders`).

At a minimum, a plugin definition must have a `name` and a `pip_url` (its [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument).

#### Discoverable plugin references

A plugin definition _without_ a `namespace` is a reference to a [discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same `name`:

```yaml{3-4}
plugins:
  extractors:
  - name: tap-gitlab
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
```

In the context of your project, these plugins inherit their metadata (`executable`, `capabilities`, and `settings`; see below) from the discoverable plugin definition.

##### Variants

If multiple [variants](/docs/plugins.html#variants) of a discoverable plugin are available, the specific variant that is used in the project is identified using the `variant` key:

```yaml{4}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
```

If no `variant` is specified, the _original_ variant supported by Meltano is used.
Note that this is not necessarily the _default_ variant that is recommended to new users and would be used if the plugin were newly added to the project.

Only a single variant of a plugin can be present in a project at a time, and that variant will be used whenever you refer to the plugin by name in a [CLI](/docs/command-line-interface.html) argument or [schedule definition](#schedules).

#### Custom plugin definitions

When a `namespace` is specified, we're dealing with a [custom plugin](/docs/plugins.html#custom-plugins) definition instead, and additional properties `executable`, `capabilities`, and `settings` are available:

```yaml{4,6-14}
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

#### Plugin configuration

A plugin's [configuration](/docs/configuration.html) is stored under a `config` key. Values for [plugin extras](/docs/configuration.html#plugin-extras) are stored among the plugin's other properties, outside of the `config` object:

```yaml{4-8}
extractors:
- name: tap-example
  pip_url: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

### Schedules

Definitions of [pipeline schedules you've created](/docs/orchestration.html#create-a-schedule)
using [`meltano schedule`](/docs/command-line-interface.html#schedule) are stored under the `schedules` key.

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

- `job` table: One row for each [`meltano elt`](/docs/command-line-interface.html#elt) pipeline run, holding started/ended timestamps and [pipeline state](/docs/integration.html#pipeline-state).
- `plugin_settings` table: [Plugin configuration](/docs/configuration.html#configuration-layers) set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/ui.html) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
- `user` table: Users for [Meltano UI](/docs/ui.html) created using [`meltano user add`](/docs/command-line-interface.html#user).
