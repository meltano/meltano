---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Project Structure

## `meltano.yml` project file

The only required property is `version`, which currently always holds the value `1`.

### Configuration

At the root of `meltano.yml`, and usually at the top of the file, you will find project-specific configuration.

In a newly initialized project, only the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats)
will be set.

To learn which settings are available, refer to the [Settings reference](/docs/settings.html).

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
- `.meltano/run/elt/<job_id>/<run_id>/`, e.g. `.meltano/run/elt/gitlab-to-postgres/<UUID>/`: Directory used by [`meltano elt`](/docs/command-line-interface.html#elt) to store pipeline-specific generated plugin config files, like an [extractor](/docs/plugin-structure.html#extractors)'s `tap.config.json`, `tap.properties.json`, and `state.json`.
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
