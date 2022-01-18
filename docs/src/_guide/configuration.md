---
title: Meltano Configuration
description: Learn how to manage the configuration of your project's plugins.
layout: doc
weight: 3
---

Meltano is responsible for managing the configuration of all of a [project](/reference/project)'s [plugins](/reference/plugins).
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

Since this also goes for [extractors](/reference/plugins#extractors) and [loaders](/reference/plugins#loaders), you do not need to manually craft the
[`config.json` files](https://hub.meltano.com/singer/spec#config-files) expected by Singer taps and targets,
because Meltano will generate them on the fly whenever an extractor or loader is used through [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).

If the plugin you'd like to use and configure is [supported out of the box](/reference/plugins#discoverable-plugins) (that is, it shows up when you run [`meltano discover`](/reference/command-line-interface#discover)), Meltano already knows what settings it supports.
If you're adding a [custom plugin](/reference/plugins#custom-plugins), on the other hand, you will be asked to provide the names of the supported configuration options yourself.

You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list all available settings for a plugin with their names, [environment variables](#environment-variables), and current values. [`meltano config <plugin>`](/reference/command-line-interface#config) will print the current configuration in JSON format.

If supported by the plugin type, its configuration can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

Meltano itself can be configured as well. To learn more, refer to the [Settings Reference](/reference/settings).

## Configuration layers

To determine the values of settings, Meltano will look in 4 main places (and one optional one), with each taking precedence over the next:

1. [**Environment variables**](#configuring-settings), set through [your shell at `meltano elt` runtime](/tutorials/integration#pipeline-specific-configuration), your project's [`.env` file](/reference/project#env), a [scheduled pipeline's `env` dictionary](/reference/project#schedules), or any other method.
   - You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list the available variable names, which typically have the format `<PLUGIN_NAME>_<SETTING_NAME>`.
2. **Your [`meltano.yml` project file](/reference/project#meltano-yml-project-file)**, under the plugin's `config` key.
   - Inside values, [environment variables can be referenced](#expansion-in-setting-values) as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
   - You can use [Meltano Environments](/reference/environments) to manage different configurations depending on your testing and deployment strategy.
3. **Your project's [**system database**](/reference/project#system-database)**, which (among other things) stores configuration set using [`meltano config <plugin> set`](/reference/command-line-interface#config) or [the UI](/reference/ui) when the project is [deployed as read-only](/reference/settings#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. _If the plugin [inherits from another plugin](/reference/plugins#plugin-inheritance) in your project_: **The parent plugin's own configuration**
5. **The default `value`s** set in the plugin's [`settings` metadata](/reference/settings).
   - Definitions of [discoverable plugins](/reference/plugins#discoverable-plugins) can be found in the [`discovery.yml` manifest](/getting-started/contributor-guide#discoverable-plugins).
   - [Custom plugin definitions](/reference/project#plugins) can be found in your [`meltano.yml` project file](/reference/project#meltano-yml-project-file).
   - `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in `meltano.yml` and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, `.env`, or the system database.

[`meltano config <plugin> set`](/reference/command-line-interface#config) will automatically store configuration in `meltano.yml` or `.env` as appropriate.

## Environment variables

When you run an executable on your system, [environment variables](https://en.wikipedia.org/wiki/Environment_variable)
can be used to pass along arbitrary key-value data to the new process.

Meltano [reads settings from environment variables](#configuring-settings) when you run the [`meltano` command](/reference/command-line-interface),
and populates them when it [evaluates plugin configuration](#expansion-in-setting-values)
and [invokes plugin executables](#accessing-from-plugins).

### Configuring settings

As mentioned under [Configuration layers](#configuration-layers), Meltano will look at the environment variables it was executed with
and those specified in your project's [`.env` file](/reference/project#env)
to determine the values of [its own settings](/reference/settings) and those of its plugins.

Any setting can be configured by specifying an environment variable named `<PLUGIN_NAME>_<SETTING_NAME>`, with characters other than alphanumeric (`A-Z`, `0-9`) and underscores (`_`) replaced with underscores, e.g. `TAP_GITLAB_API_URL` for extractor `tap-gitlab`'s `api_url` setting:

```bash
export <PLUGIN_NAME>_<SETTING_NAME>=<value>

# For example:
export TAP_GITLAB_API_URL=https://gitlab.example.com
```

Plugins can also specify alternative variables (aliases) for their settings, to match existing usage or variables expected by plugin executables. You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list all available settings for a plugin along with their variables, in order of precedence.

Since environment variable values are always strings, Meltano will cast values to the appropriate type before passing them on to the plugin.

To verify that any environment variables you've set will be picked up by Meltano as you intended, you can test them with [`meltano config <plugin>`](/reference/command-line-interface#config) before running [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).

To learn how to use environment variables to specify pipeline-specific configuration, refer to the [Data Integration (EL) guide](/tutorials/integration#pipeline-specific-configuration).

### Expansion in setting values

Inside the values of settings in your [`meltano.yml` project file](/reference/project#meltano-yml-project-file),
environment variables can be referenced to dynamically adapt a plugin's configuration to the environment it is run in,
specific properties of your project, or the plugins it is run with inside a
[`meltano elt`](/reference/command-line-interface#elt) pipeline.

#### Available environment variables

The following variables can be referenced from any setting:

- Those specified in the execution environment
- Those set in your project's [`.env` file](/reference/project#env)
- `MELTANO_PROJECT_ROOT`: Absolute path to the current [project](/reference/project) directory, e.g. `/home/meltano-projects/demo-project`

Additionally, the following variables can be referenced from plugin settings (as opposed to [Meltano settings](/reference/settings)):

- `MELTANO_<SETTING_NAME>`: Variables describing [Meltano's current configuration](/reference/settings), discoverable using [`meltano config --format=env meltano`](/reference/command-line-interface#config)
- `MELTANO_<PLUGIN_TYPE>_NAME`: The plugin's `name`, e.g. `MELTANO_EXTRACTOR_NAME` as `tap-gitlab` for extractor `tap-gitlab`
- `MELTANO_<PLUGIN_TYPE>_NAMESPACE`: The plugin's `namespace`, e.g. `MELTANO_EXTRACTOR_NAMESPACE` as `tap_gitlab` for extractor `tap-gitlab`

When running a [`meltano elt`](/reference/command-line-interface#elt) pipeline, additional [pipeline environment variables](/tutorials/integration#pipeline-environment-variables)
are available to loaders and transformers that describe the extractor and loader they are run with.
When a plugin is invoked outside the context of a pipeline, these variables will be unset and any references to them will expand to empty strings.

Inside the values of [plugin extras](#plugin-extras), additional variables describing the plugin's current configuration are available,
as discoverable using [`meltano config --format=env <plugin>`](/reference/command-line-interface#config).
Generic `MELTANO_<PLUGIN_TYPE_VERB>_<SETTING_NAME>` variables can be used when the plugin name isn't known, e.g. `MELTANO_LOAD_SCHEMA` for a loader's `schema` setting.

#### How to use

Inside the plugin `config` objects in your [`meltano.yml` project file](/reference/project#meltano-yml-project-file),
these variables can be referenced using standard variable expansion syntax, i.e. `$VAR` (as a single word) or `${VAR}` (inside a word):

```yaml{4-7}
extractors:
- name: tap-example
  config:
    simple_setting: $MELTANO_EXTRACTOR_NAME
    multiple_words: $MELTANO_EXTRACTOR_NAMESPACE foo
    part_of_a_path: $MELTANO_PROJECT_ROOT/example.txt
    inside_a_word: ${MELTANO_EXTRACTOR_NAMESPACE}_foo
```

### Accessing from plugins

When Meltano invokes a plugin's executable as part of [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke), it populates the environment with the same [variables that can be referenced from settings](#available-environment-variables), as well as those describing the plugin's current configuration (including [extras](#plugin-extras)), as discoverable using [`meltano config --format=env <plugin>`](/reference/command-line-interface#config).

These can then be accessed from inside the plugin using the mechanism provided by the standard library, e.g. Python's [`os.environ`](https://docs.python.org/3/library/os.html#os.environ).

## Multiple plugin configurations

Every [plugin in your project](/reference/plugins#project-plugins) has its own configuration,
but you can use [plugin inheritance](/reference/plugins#plugin-inheritance) to define multiple plugins
that use the same package but still have their own configuration:

```yml{8-18}
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

In this example, `tap-ga--view-foo` and `tap-ga--view-bar` are separate plugins that
inherit their [base plugin description](/reference/plugins#project-plugins) (describing the package)
and configuration (where not overridden) from `tap-google-analytics`,
which itself [shadows](/reference/project#shadowing-plugin-definitions) the
[discoverable plugin](/reference/plugins#discoverable-plugins) with the same name.

If there is no need for the different plugins to inherit any common configuration,
they can [directly inherit](/reference/plugin-management#explicit-inheritance) from the
[discoverable plugin](/reference/plugins#discoverable-plugins) instead, without an intermediary plugin:

```yml
plugins:
  extractors:
  - name: tap-postgres--billing
    inherit_from: tap-postgres
    config:
      host: one.postgres.example.com
      user: billing_user
      dbname: billing_db
  - name: tap-postgres--events
    inherit_from: tap-postgres
    config:
      host: two.postgres.example.com
      user: events_user
      dbname: events_db
```

To configure `tap-postgres`'s `password` setting, you would typically set the `TAP_POSTGRES_PASSWORD` [environment variable](#configuring-settings),
but that will not work here as it would not be clear which plugin the password was intended for.

Instead, as [`meltano config <name> list`](/reference/command-line-interface#config) would tell you,
both plugins get their own unique environment variables with prefixes derived from their names:
`TAP_POSTGRES__BILLING_PASSWORD` and `TAP_POSTGRES__EVENTS_PASSWORD`.

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/reference/plugin-management#plugin-inheritance).

## Custom settings

Meltano keeps track of the settings a plugin supports using [`settings` metadata](/reference/settings), and will list them all when you run [`meltano config <plugin> list`](/reference/command-line-interface#config).

If you've added a [discoverable plugin](/reference/plugins#discoverable-plugins) to your project, this metadata will already be known to Meltano.
If we're dealing with a [custom plugin](/reference/plugins#custom-plugins) instead, you will have been asked to provide the names of the supported configuration options yourself.

If a plugin supports a setting that is not yet known to Meltano (because it may have been added after the `settings` metadata was specified, for example),
you do not need to modify the `settings` metadata to be able to use it.

Instead, you can define a custom setting by adding the setting name (key) to your plugin's `config` object in your [`meltano.yml` project file](/reference/project#meltano-yml-project-file) with the desired value (or simply `null`), by manually editing the file or using `meltano config <plugin> set <key> <value>`:

```bash
meltano config tap-example set custom_setting value
```

```yaml{5}
extractors:
- name: tap-example
  config:
    known_setting: value
    custom_setting: value
```

As long as the custom setting exists in `meltano.yml`, it will behave and can be interacted with just like any regular (known) setting. It will show up in `meltano config <plugin> list` and `meltano config <plugin>`, and the value that will be passed on to the plugin can be [overridden using an environment variable](/reference/configuration#configuring-settings):

```bash
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

## Plugin extras

Plugin extras are additional configuration options specific to the type of plugin (e.g. all extractors)
that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:
- [Extractors](/reference/plugins#extractors)
  - [`catalog`](/reference/plugins#catalog-extra)
  - [`load_schema`](/reference/plugins#load-schema-extra)
  - [`metadata`](/reference/plugins#metadata-extra)
  - [`schema`](/reference/plugins#schema-extra)
  - [`select`](/reference/plugins#select-extra)
  - [`select_filter`](/reference/plugins#select-filter-extra)
  - [`state`](/reference/plugins#state-extra)
- [Loaders](/reference/plugins#loaders)
  - [`dialect`](/reference/plugins#dialect-extra)
  - [`target_schema`](/reference/plugins#target-schema-extra)
- [Transforms](/reference/plugins#transforms)
  - [`package_name`](/reference/plugins#package-name-extra)
  - [`vars`](/reference/plugins#vars-extra)
- [File bundles](/reference/plugins#file-bundles)
  - [`update`](/reference/plugins#update-extra)

The values of these extras are stored in your [`meltano.yml` project file](/reference/project#meltano-yml-project-file) among the plugin's other properties, _outside_ of the `config` object:

```yaml{6-7}
extractors:
- name: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

These extras can be thought of and interacted with as a special kind of setting,
and [environment variables](#configuring-settings) and
[`meltano config`](/reference/command-line-interface#config) can be used to manage them:
[How to use: Plugin extras](/reference/command-line-interface#how-to-use-plugin-extras).

## Configuration testing

The configuration of a plugin can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

<div class="notification is-danger">
  <p>Configuration testing is only supported for <a href="/reference/plugins#extractors">extractor</a> plugins currently.</p>
</div>

## Meltano UI

While Meltano is optimized for usage through the [`meltano` CLI](/reference/command-line-interface)
and direct changes to the [`meltano.yml` project file](/reference/project#meltano-yml-project-file),
basic plugin configuration functionality is also available in [the UI](/reference/ui#extractor-configuration).
