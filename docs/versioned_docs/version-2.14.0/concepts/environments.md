---
title: Environments
description: Environments allow data teams to manage different sets of configurations for extractors, loaders and plugins.
layout: doc
weight: 3
---

As part of Meltano's vision to enable data teams to operate with best practices, **Environments** allows
you to define custom layers of configuration within your project. That way, You can run the same commands against multiple environments,
by passing a single environment variable or CLI option.

This reduces the number of environment variables you need to set (and switch between), and at the same time,
eliminates the need for managing and toggling between multiple `.env` files.

A set of environment definitions looks like this within `meltano.yml`:

```yaml
environments:
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-github
            config:
              organizations: [Meltano]
            select: ["*.*"]
        loaders:
          - name: target-snowflake
            config:
              dbname: prod
              warehouse: prod_wh
              batch_size_rows: 100000
    env:
      SOME_PROD_ONLY_SETTING: abc
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-github
            config:
              organizations: [MeltanoLabs]
            select: ["repositories.*"]
        loaders:
          - name: target-snowflake
            config:
              dbname: dev
              warehouse: dev_wh
              batch_size_rows: 1000
    state_id_suffix: ${CUSTOM_SUFFIX}
```

<div class="notification is-info">
  <p><strong>Environments vs Python Virtual Environments</strong></p>
  <p>For installable Python plugins (i.e. those with a <a href="project#plugins"><code>pip_url</code></a> property) configured across multiple Environments, the same Python virtual environment and executable are reused.</p>
  <p>To install different versions of the same plugin, you can use <a href="plugins#plugin-inheritance">plugin inheritance</a> and set a different <code>pip_url</code> in the inherited plugin.</p>
</div>

## Inheritance

Environments are most powerful when [inheriting](plugins#plugin-inheritance) from a base plugin definition.
Configuration that is set in an environment can be used to add or override configuration set in the base plugin configuration.
This enables reuse of configuration common to multiple environments while making it easy to switch configuration for a specific environment.

## The `env` mapping

An Environment can define an `env` mapping that will be injected into the plugin(s) environment at runtime.
Only project-set environment variables referenced in the env mapping will be expanded appropriately.
That is, `MELTANO_PROJECT_ROOT`, `MELTANO_SYS_DIR_ROOT` and `MELTANO_ENVIRONMENT`.

In the below example, the `$MELTANO_PROJECT_ROOT/path/to/a/file.json` value will properly read the `$MELTANO_PROJECT_ROOT`
environment variable and inject the full value as `$MY_ENV_VAR` into the environment.

```yaml
environments:
  - name: dev
    env:
      MY_ENV_VAR: $MELTANO_PROJECT_ROOT/path/to/a/file.json
```

## State ID Suffix

Environments can also define a `state_id_suffix` - a custom suffix used in the generation of a state ID for each extractor/loader pair passed to [`meltano run`](/reference/command-line-interface#run).
The suffix is appended to the generated ID with a colon prefix: `:<state_id_suffix>`.

The full ID when a suffix is present is `<environment_name>:<tap_name>-to-<target_name>:<state_id_suffix>`.

`state_id_suffix` supports interpolation of environment variables to allow for dynamic state IDs (e.g. unique state for multiple `meltano run` invocations using the same environment and EL pair(s)).

## Activation

To use an environment, you can pass the option `--environment=<ENV>` to the CLI command, or set the `MELTANO_ENVIRONMENT=<ENV>` variable.

```shell
# Using the CLI option
meltano --environment=dev elt tap-github target-sqlite

# Using env vars
export MELTANO_ENVIRONMENT=dev
meltano elt tap-github target-sqlite
```

Once activated, Plugins and other processes invoked by Meltano can access the current environment via the `MELTANO_ENVIRONMENT` environment variable available in every Plugins execution environment.
If no environment is active, the `MELTANO_ENVIRONMENT` is populated with an empty string.

### Default Environments

If you have an environment that you'd like to use by default without having to pass the `--environment=<ENV>` option or set the `MELTANO_ENVIRONMENT=<ENV>` variable you can set it as the `default_environment` in your `meltano.yml`.

```yaml
default_environment: <ENV>
```

Note that the default environment does not apply to the [`meltano config`](/reference/command-line-interface#using-config-with-environments) command.
Default environments are intended for execution related work and not configuration.

## Example

When activating an environment, you will observe different configurations are injected by Meltano
whenever you invoke an operation in the command line:

```console
$ meltano --environment=prod config target-snowflake
{
  "dbname": "prod",
  "warehouse": "prod_wh",
  "batch_size_rows": 100000
}
```

```console
$ meltano --environment=dev config target-snowflake
{
  "dbname": "dev",
  "warehouse": "dev_wh",
  "batch_size_rows": 1000
}
```

## Commands with support for `--environment`

See the [CLI Reference](/reference/command-line-interface#environment).
