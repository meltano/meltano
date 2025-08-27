---
title: Manage Configuration
description: Learn how to manage the configuration of your project's plugins.
layout: doc
sidebar_position: 3
---

Meltano is responsible for managing the configuration of all of a [project](/concepts/project)'s [plugins](/concepts/plugins).
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

Since this also goes for [extractors](/concepts/plugins#extractors) and [loaders](/concepts/plugins#loaders), you do not need to manually craft the
[`config.json` files](https://hub.meltano.com/singer/spec#config-files) expected by Singer taps and targets,
because Meltano will generate them on the fly whenever an extractor or loader is used through [`meltano run`](/reference/command-line-interface#run) or [`meltano invoke`](/reference/command-line-interface#invoke).

If the plugin you'd like to use and configure is [supported out of the box](/concepts/plugins#discoverable-plugins), Meltano already knows what settings it supports.
If you're adding a [custom plugin](/concepts/plugins#custom-plugins), on the other hand, you will be asked to provide the names of the supported configuration options yourself.

You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list all available settings for a plugin with their names, [environment variables](#environment-variables), and current values. [`meltano config <plugin>`](/reference/command-line-interface#config) will print the current configuration in JSON format.

If supported by the plugin type, its configuration can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

Meltano itself can be configured as well. To learn more, refer to the [Settings Reference](/reference/settings).

## Configuration layers

To determine the values of settings, Meltano will look in 4 main places (and one optional one), with each taking precedence over the next:

1. [**Environment variables**](#configuring-settings), set through [your shell at `meltano run` runtime](/guide/integration#pipeline-specific-configuration), your project's [`.env` file](/concepts/project#env), a [scheduled pipeline's `env` dictionary](/concepts/project#schedules), or any other method.
   - You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list the available variable names, which typically have the format `<PLUGIN_NAME>_<SETTING_NAME>`.
2. **Your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file)**, under the plugin's `config` key.
   - Inside values, [environment variables can be referenced](#expansion-in-setting-values) as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
   - You can use [Meltano Environments](/concepts/environments) to manage different configurations depending on your testing and deployment strategy. If values for plugin settings are provided in both the top-level plugin configuration _and_ the environment-level plugin configuration, the value at the environment level will take precedence.
3. **Your project's [system database](/concepts/project#system-database)**, which (among other things) stores configuration set using [`meltano config <plugin> set`](/reference/command-line-interface#config) when the project is [deployed as read-only](/reference/settings#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. _If the plugin [inherits from another plugin](/concepts/plugins#plugin-inheritance) in your project_: **The parent plugin's own configuration**
5. **The default `value`s** set in the plugin's [`settings` metadata](/reference/settings).
   - Definitions of [discoverable plugins](/concepts/plugins#discoverable-plugins) can be found on [Meltano Hub](/contribute/plugins#discoverable-plugins).
   - [Custom plugin definitions](/concepts/project#plugins) can be found in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file).
   - `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in `meltano.yml` and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, `.env`, or the system database.

[`meltano config <plugin> set`](/reference/command-line-interface#config) will automatically store configuration in `meltano.yml` or `.env` as appropriate.

### Overriding discoverable plugin properties

Starting with Meltano [`2.0`](/guide/v2-migration), you can override the properties of discoverable plugins, such as their [`capabilities`](/contribute/plugins#how-to-test-a-tap) and `settings_group_validation`, and extend their default [`settings`](/reference/settings):

```yaml
plugins:
  extractors:
  - name: tap-example
    variant: meltanolabs
    capabilities:  # This will override the capabilities declared in the lockfile
    - state
    - discover
    - catalog
    settings:  # These will be appended to the settings declared in the lockfile
    - name: my-new-setting
      kind: object
      value:
        key: value
```

All overrides replace the values stored in the [lockfile](/concepts/plugins#lock-artifacts), except for `settings`, which extend the base definitions. If there is a collision on name, then the setting is taken from the override definition in `meltano.yml` and used at runtime, while the token setting definition in the lockfile is discarded.

## Environment variables

When you run an executable on your system, [environment variables](https://en.wikipedia.org/wiki/Environment_variable)
can be used to pass along arbitrary key-value data to the new process.

Meltano [reads settings from environment variables](#configuring-settings) when you run the [`meltano` command](/reference/command-line-interface),
and populates them when it [evaluates plugin configuration](#expansion-in-setting-values)
and [invokes plugin executables](#accessing-from-plugins).
Meltano also supports specifying environment variables under the `env:` keys of `meltano.yml`, a Meltano Environment, or on the Plugin.

### Specifying environment variables

In addition to the terminal environment and the `.env ` file, Meltano supports the specification of environment variables at the following configuration levels:

```yaml
env:
  # root level env
  MY_ENV_VAR: top_level_env_var
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    env:
      # root level plugin env
      MY_ENV_VAR: plugin_level_env_var
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
environments:
- name: dev
  env:
    # environment level env
    MY_ENV_VAR: environment_level_env_var
  config:
    plugins:
      extractors:
        - name: tap-google-analytics
          variant: meltano
          env:
            # environment level plugin env
            MY_ENV_VAR: environment_level_plugin_env_var
schedules:
- name: daily-google-analytics-load
  interval: '@daily'
  extractor: tap-google-analytics
  loader: target-postgres
  transform: skip
  start_date: 2024-08-24 00:00:00
  env:
    SCHEDULE_SPECIFIC_ENV_VAR: schedule_specific_value
```

Environment levels within `meltano.yml` resolve in order of precedence (within a plugins context):

```yaml
- environment level plugin env # highest
- environment level env
- root level plugin env
- root level env
- schedule level env
- .env file
- terminal env # lowest
```

:::info

  <p>
  We are considering adding support for the <code>env</code> key to <a href="/concepts/project#jobs">jobs</a> as well as updating the precedence order when we do.
  We'd love to hear your thoughts in the <a href="https://github.com/meltano/meltano/issues/6386">GitHub issue</a> about this possible change!
  </p>
:::

This allows you to override environment variables per plugin and per environment, as needed for your use case.

#### Environment variable expansion

Environment variable values within a given layer of your `meltano.yml` can inherit values from other layers.
For example, if your terminal environment has the environment variable `TERMINAL_ENVIRONMENT_VARIABLE` set to the value `1` and you then add the following to your `meltano.yml`

```yaml
environments:
  - name: dev
    env:
      INHERITED: ${TERMINAL_ENVIRONMENT_VARIABLE}2
```

then the environment variable `INHERITED` would be expanded to have the value of `12` in your `dev` environment.

Environment variables are inherited across layers in the following order, where environment variable values at each level are expanded using values from the layers above it.

```
- terminal env and .env
- root-level env in meltano.yml
- active environment env
- root-level plugin-level env
- active environment-level plugin-level env
```

The following example illustrates how values are expanded:

```yaml
env:
  # Level 2: top-level `env:`
  # Inherits from terminal context
  LEVEL_NUM: "2"                  #  '2'
  STACKED: "${STACKED}2"          # '12'
plugins:
  extractors:
    - name: tap-foobar
      env:
        # Level 4: plugin-level `env:`
        # Inherits from a environment-level `env:` if an environment is active
        # Inherits directly from top-level `env:` if no environment is active
        LEVEL_NUM: "4"            #    '4'
        STACKED: "${STACKED}4"    # '1234'
environments:
  - name: prod
    env:
      # Level 3: environment-level `env:`
      # Inherits from top-level `env:`
      LEVEL_NUM: "3"              #   '3'
      STACKED: "${STACKED}3"      # '123'
    config:
      plugins:
        extractors:
          - name: tap-foobar
            env:
              # Level 5: environment-level plugin `env:`
              # Inherits from (global) plugin-level `env:`
              LEVEL_NUM: "5"          #     '5'
              STACKED: "${STACKED}5"  # '12345'

```

Note that the resolution and inheritance behavior of environment variables set via `env` keys in your `meltano.yml` differ from the [resolution and inheritance behavior of `config` or `settings` keys](/guide/configuration#configuration-layers).

Because settings and environment variable behavior can become complex when set in multiple places, the [`meltano invoke` command](/reference/command-line-interface#invoke) provides a `--print-var` option which allows you to easily inspect what value is being supplied for a given environment variable within your plugin's invocation environment at runtime.

##### Environment variable expansion within `pip_url`

In addition to affecting the environment variables at runtime, and the `config`/`settings` values, environment variables can be expanded within the value of a plugin's `pip_url`. The environment variable inheritance shown above applies to environment variables expanded within the value of `pip_url`.

This can be useful for using a different `pip_url` for different environments (e.g. to change which git branch of a plugin repository is used):

```yaml
pip_url: "git+https://github.com/MeltanoLabs/tap-github.git@${TAP_GITHUB_GIT_REV}"
```

Another use for this is to supply credentials for a private Python package index:

```yaml
pip_url: "https://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@nexus.example.com/simple"
```

### Configuring settings

As mentioned under [Configuration layers](#configuration-layers), Meltano will look at the environment variables it was executed with
and those specified in your project's [`.env` file](/concepts/project#env)
to determine the values of [its own settings](/reference/settings) and those of its plugins.

Any setting can be configured by specifying an environment variable named `<PLUGIN_NAME>_<SETTING_NAME>`, with characters other than alphanumeric (`A-Z`, `0-9`) and underscores (`_`) replaced with underscores, e.g. `TAP_GITLAB_API_URL` for extractor `tap-gitlab`'s `api_url` setting:

```bash
export <PLUGIN_NAME>_<SETTING_NAME>=<value>

# For example:
export TAP_GITLAB_API_URL=https://gitlab.example.com
```

Plugins can also specify alternative variables ([aliases](#aliases) for their settings, to match existing usage or variables expected by plugin executables. You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list all available settings for a plugin along with their variables, in order of precedence.

Since environment variable values are always strings, Meltano will cast values to the appropriate type before passing them on to the plugin.

To verify that any environment variables you've set will be picked up by Meltano as you intended, you can test them with [`meltano config <plugin>`](/reference/command-line-interface#config) before running [`meltano run`](/reference/command-line-interface#run) or [`meltano invoke`](/reference/command-line-interface#invoke).

To learn how to use environment variables to specify pipeline-specific configuration, refer to the [Data Integration (EL) guide](/guide/integration#pipeline-specific-configuration).

#### Settings Aliases

Aliases allow for configuration values to be set via one of multiple keys.
Environment variable aliases are listed next to the canonical names for the variable in the output of the [`meltano config <plugin> list`](/reference/command-line-interface#config) command.
They can be defined via the `aliases` key in a custom plugin's `settings` configuration.
For example, the following defines a `my_custom_username` setting with aliases `custom_tap_username` and `username`:

```yaml
# meltano.yml
---
plugins:
  extractors:
  - name: my-custom-tap
    namespace: my_custom_tap
    pip_url: git+https://github.com/my-organization/my-custom-tap.git
    executable: my-custom-tap
    capabilities:
    - discover
    - catalog
    settings:
    - name: password
      kind: string
      sensitive: true
    - name: my_custom_tap_username
      aliases: [custom_tap_username, username]
```

Within a given configuration layer, a setting can be set via only a single name, whether that name is its canonical name or one of its aliases.
So given the custom extractor defined above, the `my_custom_tap_username` setting could be set via the `MY_CUSTOM_TAP_MY_CUSTOM_TAP_USERNAME` environment variable or either the `MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME` or `MY_CUSTOM_TAP_USERNAME` variables.

But if more than one of these variables is set in the terminal environment, then an exception will be raised--even if all the relevant environment variables have the same value.

The configuration setting could also be set via the [`meltano config set`](/reference/command-line-interface#config) by setting either the canonical name or any of its aliases. Again using the custom extractor defined above as an example, the `my_custom_tap_username` could be set by any of the following commands:

```bash
# The canonical name
meltano config my-custom-tap set my_custom_tap_username some_value

# Alias 1
meltano config my-custom-tap set custom_tap_username some_value

# Alias 2
meltano config my-custom-tap set username some_value
```

To see what name or alias a setting's value is being derived from, you can run `meltano config <plugin-name> list`:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ meltano config my-custom-tap list
2024-06-22T10:00:00Z [info     ] Environment 'dev' is active
password [env: MY_CUSTOM_TAP_PASSWORD] current value: (redacted) (from the MY_CUSTOM_TAP_PASSWORD variable in `.env`)
my_custom_tap_username [env: MY_CUSTOM_TAP_MY_CUSTOM_TAP_USERNAME, MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME, MY_CUSTOM_TAP_USERNAME] current value: 'some_username' (from the MY_CUSTOM_TAP_USERNAME variable in the environment)
```

If a setting's value is being set via multiple environment variables, the resulting error message will list the environment variables where it is being set:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ export MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME=some_username
$ meltano config my-custom-tap
Setting value set via multiple environment variables: ['MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME', 'MY_CUSTOM_TAP_USERNAME']
```

If the values for the multiple environment variables differ, the error message will also list what the values are:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ export MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME=some_other_username
$ meltano config my-custom-tap
Conflicting values for setting found in: ['MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME', 'MY_CUSTOM_TAP_USERNAME']
```

### Expansion in setting values

Inside the values of settings in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file), environment variables can be referenced to dynamically adapt a plugin's configuration to the environment it is run in, specific properties of your project, or the plugins it is run with inside a [`meltano run`](/reference/command-line-interface#run) pipeline.

#### Available plugin environment variables

The following variables can be referenced from any setting:

- Those specified in the execution environment
- Those set in your project's [`.env` file](/concepts/project#env)
- `MELTANO_PROJECT_ROOT`: Absolute path to the current [project](/concepts/project) directory, e.g. `/home/meltano-projects/demo-project`

Additionally, the following variables can be referenced from plugin settings (as opposed to [Meltano settings](/reference/settings)):

- `MELTANO_<SETTING_NAME>`: Variables describing [Meltano's current configuration](/reference/settings), discoverable using [`meltano config --format=env meltano`](/reference/command-line-interface#config)
- `MELTANO_<PLUGIN_TYPE>_NAME`: The plugin's `name`, e.g. `MELTANO_EXTRACTOR_NAME` as `tap-gitlab` for extractor `tap-gitlab`
- `MELTANO_<PLUGIN_TYPE>_NAMESPACE`: The plugin's `namespace`, e.g. `MELTANO_EXTRACTOR_NAMESPACE` as `tap_gitlab` for extractor `tap-gitlab`

When running a [`meltano el`](/reference/command-line-interface#el) pipeline, additional [pipeline environment variables](/guide/integration#pipeline-environment-variables)
are available to loaders and transformers that describe the extractor and loader they are run with.
When a plugin is invoked outside the context of a pipeline, these variables will be unset and any references to them will expand to empty strings.

Inside the values of [plugin extras](#plugin-extras), additional variables describing the plugin's current configuration are available,
as discoverable using [`meltano config --format=env <plugin>`](/reference/command-line-interface#config).
Generic `MELTANO_<PLUGIN_TYPE_VERB>_<SETTING_NAME>` variables can be used when the plugin name isn't known, e.g. `MELTANO_LOAD_SCHEMA` for a loader's `schema` setting.

#### How to use

Inside the plugin `config` objects in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file),
these variables can be referenced using standard variable expansion syntax, i.e. `$VAR` (as a single word) or `${VAR}` (inside a word):

```yaml
extractors:
- name: tap-example
  config:
    simple_setting: $MELTANO_EXTRACTOR_NAME
    multiple_words: $MELTANO_EXTRACTOR_NAMESPACE foo
    part_of_a_path: $MELTANO_PROJECT_ROOT/example.txt
    inside_a_word: ${MELTANO_EXTRACTOR_NAMESPACE}_foo
```

:::tip
<p>Values with a <code>%5C</code> character that are not intended to be expanded should be escaped with a backslash (<code>%24</code>), e.g. <code>%5C%24VAR</code>:</p>

```yaml
extractors:
- name: tap-example
  config:
    special_character_setting: MY_$VAR
```
:::

### Accessing from plugins

When Meltano invokes a plugin's executable as part of [`meltano run`](/reference/command-line-interface#run) or [`meltano invoke`](/reference/command-line-interface#invoke), it populates the environment with the same [variables that can be referenced from settings](#available-environment-variables), as well as those describing the plugin's current configuration (including [extras](#plugin-extras)), as discoverable using [`meltano config --format=env <plugin>`](/reference/command-line-interface#config).

These can then be accessed from inside the plugin using the mechanism provided by the standard library, e.g. Python's [`os.environ`](https://docs.python.org/3/library/os.html#os.environ).

Within a [Meltano environment](/concepts/environments) environment variables can be specified using the `env` key:

```yml
environments:
- name: dev
  env:
    AN_ENVIRONMENT_VARIABLE: dev
```

Any plugins run in that Meltano environment will then have the provided environment variables populated into the plugin's environment.

## Multiple plugin configurations

Every [plugin in your project](/concepts/plugins#project-plugins) has its own configuration,
but you can use [plugin inheritance](/concepts/plugins#plugin-inheritance) to define multiple plugins
that use the same package but still have their own configuration:

```yml
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: "2020-10-01T00:00:00Z"
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: "2020-12-01T00:00:00Z" # `start_date` is overridden
      view_id: 789012
```

In this example, `tap-ga--view-foo` and `tap-ga--view-bar` are separate plugins that
inherit their [base plugin description](/concepts/plugins#project-plugins) (describing the package)
and configuration (where not overridden) from `tap-google-analytics`,
which itself [shadows](/concepts/project#shadowing-plugin-definitions) the
[discoverable plugin](/concepts/plugins#discoverable-plugins) with the same name.

If there is no need for the different plugins to inherit any common configuration,
they can [directly inherit](/guide/plugin-management#explicit-inheritance) from the
[discoverable plugin](/concepts/plugins#discoverable-plugins) instead, without an intermediary plugin:

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

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#plugin-inheritance).

## Custom settings

Meltano keeps track of the settings a plugin supports using [`settings` metadata](/reference/settings), and will list them all when you run [`meltano config <plugin> list`](/reference/command-line-interface#config).

If you've added a [discoverable plugin](/concepts/plugins#discoverable-plugins) to your project, this metadata will already be known to Meltano.
If we're dealing with a [custom plugin](/concepts/plugins#custom-plugins) instead, you will have been asked to provide the names of the supported configuration options yourself.

If a plugin supports a setting that is not yet known to Meltano (because it may have been added after the `settings` metadata was specified, for example),
you do not need to modify the `settings` metadata to be able to use it.

Instead, you can define a custom setting by adding the setting name (key) to your plugin's `config` object in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) with the desired value (or simply `null`), by manually editing the file or using `meltano config <plugin> set <key> <value>`:

```bash
meltano config tap-example set custom_setting value
```

```yaml
extractors:
- name: tap-example
  config:
    known_setting: value
    custom_setting: value
```

As long as the custom setting exists in `meltano.yml`, it will behave and can be interacted with just like any regular (known) setting. It will show up in `meltano config <plugin> list` and `meltano config <plugin>`, and the value that will be passed on to the plugin can be [overridden using an environment variable](/guide/configuration#configuring-settings):

```bash
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

## Plugin extras

Plugin extras are additional configuration options specific to the type of plugin (e.g. all extractors)
that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:

- [Extractors](/concepts/plugins#extractors)
  - [`catalog`](/concepts/plugins#catalog-extra)
  - [`load_schema`](/concepts/plugins#load-schema-extra)
  - [`metadata`](/concepts/plugins#metadata-extra)
  - [`schema`](/concepts/plugins#schema-extra)
  - [`select`](/concepts/plugins#select-extra)
  - [`select_filter`](/concepts/plugins#select-filter-extra)
  - [`state`](/concepts/plugins#state-extra)
- [Loaders](/concepts/plugins#loaders)
  - [`dialect`](/concepts/plugins#dialect-extra)
- [Transforms](/concepts/plugins#transforms)
  - [`package_name`](/concepts/plugins#package-name-extra)
  - [`vars`](/concepts/plugins#vars-extra)
- [File bundles](/concepts/plugins#file-bundles)
  - [`update`](/concepts/plugins#update-extra)

The values of these extras are stored in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) among the plugin's other properties, _outside_ of the `config` object:

```yaml
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

:::danger

  <p>Configuration testing is only supported for <a href="/concepts/plugins#extractors">extractor</a> plugins currently.</p>
:::
