---
description: Environments allow data teams to manage different sets of configurations for extractors, loaders and plugins.
---

# Environments

As part of Meltano's vision to enable data teams to operate with best practices, __Environments__ allows
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
```

## Inheritance

Environments are most powerful when [inheriting](/docs/plugins.html#plugin-inheritance) from a base plugin definition. 
Configuration that is set in an environment can be used to add or override configuration set in the base plugin configuration. 
This enables reuse of configuration common to multiple environments while making it easy to switch configuratino for a specific environment. 

## Activation

To use an environment, you can pass the option `--environment=<ENV>` to the CLI command, or set the `MELTANO_ENVIRONMENT=<ENV>` variable.

```shell
# Using the CLI option
meltano --environment=dev elt tap-github target-sqlite

# Using env vars
export MELTANO_ENVIRONMENT=dev
meltano elt tap-github target-sqlite
```

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

### [`config`](/docs/command-line-interface#config)

To add, update or remove plugin configuration from an environment defined in `meltano.yml`:

```shell
meltano --environment=<ENVIRONMENT> config <plugin>
```

### [`elt`](/docs/command-line-interface#elt)

To run an ELT pipeline with configuration taken preferably from an Environment:

```shell
meltano --environment=<ENVIRONMENT> elt <extractor> <loader>
```

### [`invoke`](/docs/command-line-interface#invoke)

Invoke a plugin pipeline with configuration taken preferably from an Environment:

```shell
meltano --environment=<ENVIRONMENT> invoke <plugin>
```

### [`select`](/docs/command-line-interface#select)

Manage select patterns for an extractor within an Environment:

```shell
meltano --environment=<ENVIRONMENT> select <tap_name>
```

## Incremental adoption

__Environments__ promote _incremental_ adoption. You can continue using Meltano the way you've been doing it so far,
and leverage environments whenever you need to starting switching between different sets of configurations.
