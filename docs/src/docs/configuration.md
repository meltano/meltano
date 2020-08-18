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

1. **Environment variables**, set through [your shell at `meltano elt` runtime](/docs/command-line-interface.html#pipeline-specific-configuration), a [`.env` file](https://github.com/theskumar/python-dotenv#usages) in your project directory, a [scheduled pipeline](/#orchestration)'s `env` dictionary in `meltano.yml`, or any other method. You can use `meltano config <plugin> list` to list the available variable names.
2. **Your project's `meltano.yml` file**, under the plugin's `config` key.
   - Inside values, [environment variables](#pipeline-environment-variables) can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Note that configuration for Meltano itself is stored at the root level of `meltano.yml`.
3. **Your project's [**system database**](/docs/settings.html#database-uri)**, which lives at `.meltano/meltano.db` by default and (among other things) stores configuration set using [`meltano config <plugin> set`](/docs/command-line-interface.html#config) or [the UI](/docs/command-line-interface.html#ui) when the project is [deployed as read-only](/docs/settings.html#project-readonly).
   - Note that configuration for Meltano itself cannot be stored in the system database.
4. **The default `value`s** set on the plugin's `settings` object in the global `discovery.yml` file (in the case of [known plugins](/docs/contributor-guide.html#known-plugins)) or your project's `meltano.yml` file (in the case of custom plugins). `meltano config <plugin> list` will list the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in your project's `meltano.yml` file and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, a (`.gitignore`d) `.env` file in your project directory, or the system database.

[`meltano config <plugin> set`](/docs/command-line-interface.html#config) will automatically store settings in `meltano.yml` or `.env` as appropriate.
