---
description: Learn how to manage the configuration of your project's plugins.
---

# Configuration

Meltano is responsible for managing the configuration of all of a [project](/docs/project.html)'s [plugins](/docs/plugins.html).
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

Since this also goes for [extractors](/docs/plugins.html#extractors) and [loaders](/docs/plugins.html#loaders), you do not need to manually craft the
[`config.json` files](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#config-file) expected by Singer taps and targets,
because Meltano will generate them on the fly whenever an extractor or loader is used through [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If the plugin you'd like to use and configure is [supported out of the box](/docs/plugins.html#discoverable-plugins) (that is, it shows up when you run [`meltano discover`](/docs/command-line-interface.html#discover)), Meltano already knows what settings it supports.
If you're adding a [custom plugin](/docs/plugins.html#custom-plugins), on the other hand, you will be asked to provide the names of the supported configuration options yourself.

You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list all available settings for a plugin with their names, [environment variables](#environment-variables), and current values. [`meltano config <plugin>`](/docs/command-line-interface.html#config) will print the current configuration in JSON format.

Meltano itself can be configured as well. To learn more, refer to the [Settings Reference](/docs/settings.html).

## Configuration layers

To determine the values of settings, Meltano will look in 4 main places (and one optional one), with each taking precedence over the next:

1. [**Environment variables**](#configuring-settings), set through [your shell at `meltano elt` runtime](/docs/integration.html#pipeline-specific-configuration), your project's [`.env` file](/docs/project.html#env), a [scheduled pipeline's `env` dictionary](/docs/project.html#schedules), or any other method.
   - You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list the available variable names, which typically have the format `<PLUGIN_NAME>_<SETTING_NAME>`.
2. **Your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file)**, under the plugin's `config` key.
   - Inside values, [environment variables can be referenced](#expansion-in-setting-values) as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
3. **Your project's [**system database**](/docs/project.html#system-database)**, which (among other things) stores configuration set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/ui.html) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. _If the plugin [inherits from another plugin](/docs/plugins.html#plugin-inheritance) in your project_: **The parent plugin's own configuration**
5. **The default `value`s** set in the plugin's [`settings` metadata](/docs/contributor-guide.html#connector-settings).
   - Definitions of [discoverable plugins](/docs/plugins.html#discoverable-plugins) can be found in the [`discovery.yml` manifest](/docs/contributor-guide.html#discoverable-plugins).
   - [Custom plugin definitions](/docs/project.html#plugins) can be found in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).
   - `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in `meltano.yml` and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, `.env`, or the system database.

[`meltano config <plugin> set`](/docs/command-line-interface.html#config) will automatically store configuration in `meltano.yml` or `.env` as appropriate.

## Environment variables

When you run an executable on your system, [environment variables](https://en.wikipedia.org/wiki/Environment_variable)
can be used to pass along arbitrary key-value data to the new process.

Meltano [reads settings from environment variables](#configuring-settings) when you run the [`meltano` command](/docs/command-line-interface.html),
and populates them when it [evaluates plugin configuration](#expansion-in-setting-values)
and [invokes plugin executables](#accessing-from-plugins).

### Configuring settings

As mentioned under [Configuration layers](#configuration-layers), Meltano will look at the environment variables it was executed with
and those specified in your project's [`.env` file](/docs/project.html#env)
to determine the values of [its own settings](/docs/settings.md) and those of its plugins.

Any setting can be configured by specifying an environment variable named `<PLUGIN_NAME>_<SETTING_NAME>`, with characters other than alphanumeric (`A-Z`, `0-9`) and underscores (`_`) replaced with underscores, e.g. `TAP_GITLAB_API_URL` for extractor `tap-gitlab`'s `api_url` setting:

```bash
export <PLUGIN_NAME>_<SETTING_NAME>=<value>

# For example:
export TAP_GITLAB_API_URL=https://gitlab.example.com
```

Plugins can also specify alternative variables (aliases) for their settings, to match existing usage or variables expected by plugin executables. You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list all available settings for a plugin along with their variables, in order of precedence.

Since environment variable values are always strings, Meltano will cast values to the appropriate type before passing them on to the plugin.

To verify that any environment variables you've set will be picked up by Meltano as you intended, you can test them with [`meltano config <plugin>`](/docs/command-line-interface.html#config) before running [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

To learn how to use environment variables to specify pipeline-specific configuration, refer to the [Data Integration (EL) guide](/docs/integration.html#pipeline-specific-configuration).

### Expansion in setting values

Inside the values of settings in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
environment variables can be referenced to dynamically adapt a plugin's configuration to the environment it is run in,
specific properties of your project, or the plugins it is run with inside a
[`meltano elt`](/docs/command-line-interface.html#elt) pipeline.

#### Available environment variables

The following variables can be referenced from any setting:

- Those specified in the execution environment
- Those set in your project's [`.env` file](/docs/project.html#env)
- `MELTANO_PROJECT_ROOT`: Absolute path to the current [project](/docs/project.html) directory, e.g. `/home/meltano-projects/demo-project`

Additionally, the following variables can be referenced from plugin settings (as opposed to [Meltano settings](/docs/settings.html)):

- `MELTANO_<SETTING_NAME>`: Variables describing [Meltano's current configuration](/docs/settings.html), discoverable using [`meltano config --format=env meltano`](/docs/command-line-interface.html#config)
- `MELTANO_<PLUGIN_TYPE>_NAME`: The plugin's `name`, e.g. `MELTANO_EXTRACTOR_NAME` as `tap-gitlab` for extractor `tap-gitlab`
- `MELTANO_<PLUGIN_TYPE>_NAMESPACE`: The plugin's `namespace`, e.g. `MELTANO_EXTRACTOR_NAMESPACE` as `tap_gitlab` for extractor `tap-gitlab`

When running a [`meltano elt`](/docs/command-line-interface.html#elt) pipeline, additional [pipeline environment variables](/docs/integration.html#pipeline-environment-variables)
are available to loaders and transformers that describe the extractor and loader they are run with.
When a plugin is invoked outside the context of a pipeline, these variables will be unset and any references to them will expand to empty strings.

Inside the values of [plugin extras](#plugin-extras), additional variables describing the plugin's current configuration are available,
as discoverable using [`meltano config --format=env <plugin>`](/docs/command-line-interface.html#config).
Generic `MELTANO_<PLUGIN_TYPE_VERB>_<SETTING_NAME>` variables can be used when the plugin name isn't known, e.g. `MELTANO_LOAD_SCHEMA` for a loader's `schema` setting.

#### How to use

Inside the plugin `config` objects in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
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

When Meltano invokes a plugin's executable as part of [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke), it populates the environment with the same [variables that can be referenced from settings](#available-environment-variables), as well as those describing the plugin's current configuration (including [extras](#plugin-extras)), as discoverable using [`meltano config --format=env <plugin>`](/docs/command-line-interface.html#config).

These can then be accessed from inside the plugin using the mechanism provided by the standard library, e.g. Python's [`os.environ`](https://docs.python.org/3/library/os.html#os.environ).

## Multiple plugin configurations

Every [plugin in your project](/docs/plugins.html#project-plugins) has its own configuration,
but you can use [plugin inheritance](/docs/plugins.html#plugin-inheritance) to define multiple plugins
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
inherit their [base plugin description](/docs/plugins.html#project-plugins) (describing the package)
and configuration (where not overridden) from `tap-google-analytics`,
which itself [shadows](/docs/project.html#shadowing-plugin-definitions) the
[discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same name.

If there is no need for the different plugins to inherit any common configuration,
they can [directly inherit](/docs/plugin-management.html#explicit-inheritance) from the
[discoverable plugin](/docs/plugins.html#discoverable-plugins) instead, without an intermediary plugin:

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

Instead, as [`meltano config <name> list`](/docs/command-line-interface.html#config) would tell you,
both plugins get their own unique environment variables with prefixes derived from their names:
`TAP_POSTGRES__BILLING_PASSWORD` and `TAP_POSTGRES__EVENTS_PASSWORD`.

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#plugin-inheritance).

## Custom settings

Meltano keeps track of the settings a plugin supports using [`settings` metadata](/docs/contributor-guide.html#connector-settings), and will list them all when you run [`meltano config <plugin> list`](/docs/command-line-interface.html#config).

If you've added a [discoverable plugin](/docs/plugins.html#discoverable-plugins) to your project, this metadata will already be known to Meltano.
If we're dealing with a [custom plugin](/docs/plugins.html#custom-plugins) instead, you will have been asked to provide the names of the supported configuration options yourself.

If a plugin supports a setting that is not yet known to Meltano (because it may have been added after the `settings` metadata was specified, for example),
you do not need to modify the `settings` metadata to be able to use it.

Instead, you can define a custom setting by adding the setting name (key) to your plugin's `config` object in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) with the desired value (or simply `null`), by manually editing the file or using `meltano config <plugin> set <key> <value>`:

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

As long as the custom setting exists in `meltano.yml`, it will behave and can be interacted with just like any regular (known) setting. It will show up in `meltano config <plugin> list` and `meltano config <plugin>`, and the value that will be passed on to the plugin can be [overridden using an environment variable](/docs/configuration.html#configuring-settings):

```bash
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

## Plugin extras

Plugin extras are additional configuration options specific to the type of plugin (e.g. all extractors)
that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:
- [Extractors](/docs/plugins.html#extractors)
  - [`catalog`](/docs/plugins.html#catalog-extra)
  - [`load_schema`](/docs/plugins.html#load-schema-extra)
  - [`metadata`](/docs/plugins.html#metadata-extra)
  - [`schema`](/docs/plugins.html#schema-extra)
  - [`select`](/docs/plugins.html#select-extra)
  - [`select_filter`](/docs/plugins.html#select-filter-extra)
  - [`state`](/docs/plugins.html#state-extra)
- [Loaders](/docs/plugins.html#loaders)
  - [`dialect`](/docs/plugins.html#dialect-extra)
  - [`target_schema`](/docs/plugins.html#target-schema-extra)
- [Transforms](/docs/plugins.html#transforms)
  - [`package_name`](/docs/plugins.html#package-name-extra)
  - [`vars`](/docs/plugins.html#vars-extra)
- [File bundles](/docs/plugins.html#file-bundles)
  - [`update`](/docs/plugins.html#update-extra)

The values of these extras are stored in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) among the plugin's other properties, _outside_ of the `config` object:

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
[`meltano config`](/docs/command-line-interface.html#config) can be used to manage them:
[How to use: Plugin extras](/docs/command-line-interface.html#how-to-use-plugin-extras).

## Meltano UI

While Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
basic plugin configuration functionality is also available in [the UI](/docs/ui.html#extractor-configuration).
