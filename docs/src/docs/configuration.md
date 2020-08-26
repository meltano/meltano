---
metaTitle: Meltano project and plugin configuration
description: Meltano is responsible for managing the configuration of all of a project's plugins, including its extractors and loaders.
---

# Configuration

Meltano is responsible for managing the configuration of all of a project's plugins, including its extractors and loaders.
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

This means that you do not need to manually craft the
[`config.json` files](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#config-file) expected by Singer taps and targets,
because Meltano will generate them on the fly whenever an extractor or loader is used through [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If the plugin you'd like to use and configure is already [known to Meltano](/docs/contributor-guide.html#known-plugins) (that is, it shows up when you run [`meltano discover`](/docs/command-line-interface.html#discover)), Meltano already knows what settings it supports.
If you're [adding a custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins), on the other hand, you will be asked to provide the names of the supported configuration options yourself.

## Configuration layers

To determine the values of these settings, Meltano will look in 4 places, with each taking precedence over the next:

1. **Environment variables**, set through [your shell at `meltano elt` runtime](/docs/integration.html#pipeline-specific-configuration), a [`.env` file](https://github.com/theskumar/python-dotenv#usages) in your project directory, a [scheduled pipeline](/#orchestration)'s `env` dictionary in `meltano.yml`, or any other method. You can use `meltano config <plugin> list` to list the available variable names.
2. **Your project's `meltano.yml` file**, under the plugin's `config` key.
   - Inside values, [environment variables](/docs/integration.html#pipeline-environment-variables) can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
3. **Your project's [**system database**](/docs/settings.html#database-uri)**, which lives at `.meltano/meltano.db` by default and (among other things) stores configuration set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/command-line-interface.html#ui) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. **The default `value`s** set on the plugin's `settings` object in the global `discovery.yml` file (in the case of [known plugins](/docs/contributor-guide.html#known-plugins)) or your project's `meltano.yml` file (in the case of custom plugins). `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in your project's `meltano.yml` file and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, a (`.gitignore`d) `.env` file in your project directory, or the system database.

[`meltano config <plugin> set`](/docs/command-line-interface.html#config) will automatically store settings in `meltano.yml` or `.env` as appropriate.

## Custom settings

Meltano keeps track of the settings a plugin supports using [`settings` metadata](/docs/contributor-guide.html#connector-settings), and will list them all when you run [`meltano config <plugin> list`](/docs/command-line-interface.html#config).

If you've [added a custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins) to your project, you will have been asked provide the names of the supported configuration options yourself.
If the plugin was already [known to Meltano](/docs/contributor-guide.html#known-plugins) when you added it to your project, this metadata will already be known as well.

If a plugin supports a setting that is not yet known to Meltano (because it may have been added after the `settings` metadata was specified, for example),
you do not need to modify the `settings` metadata to be able to use it.

Instead, you can define a custom setting by adding the setting name (key) to your project's `config` object in `meltano.yml` with the desired value (or simply `null`), by manually editing the file or using `meltano config <plugin> set <key> <value>`:

```bash
meltano config tap-example set custom_setting value
```

```yaml{6}
extractors:
- name: tap-example
  pip_url: tap-example
  config:
    known_setting: value
    custom_setting: value
```

As long as the custom setting exists in `meltano.yml`, it will behave and can be interacted with just like any regular (known) setting. It will show up in `meltano config <plugin> list` and `meltano config <plugin>`, and the value that will be passed on to the plugin can be [overridden using an environment variable](/docs/integration.html#pipeline-specific-configuration):

```bash
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

## Plugin extras

Plugin extras are additional configuration options specific to the type of plugin (e.g. all extractors)
that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:
- [Extractors](/docs/plugins.html#extractors)
  - [`select`](/docs/plugins.html#select-extra)
  - [`metadata`](/docs/plugins.html#metadata-extra)
  - [`schema`](/docs/plugins.html#schema-extra)
- [Transforms](/docs/plugins.html#transforms)
  - [`vars`](/docs/plugins.html#vars-extra)
- [File bundles](/docs/plugins.html#file-bundles)
  - [`update`](/docs/plugins.html#update-extra)

The values of these extras are stored in `meltano.yml` among the plugin's other properties, _outside_ of the `config` object:

```yaml{7-8}
extractors:
- name: tap-example
  pip_url: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

These extras can be thought of and interacted with as a special kind of setting,
and [`meltano config`](/docs/command-line-interface.html#config) can be used to manage them:
[How to use: Plugin extras](/docs/command-line-interface.html#how-to-use-plugin-extras).
