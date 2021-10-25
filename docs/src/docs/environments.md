---
description: Environments allow data teams to manage different sets of configurations for extractors, loaders and plugins.
---

# Environments - DRAFT

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

## Incremental adoption

__Environments__ promote _incremental_ adoption. You can continue using Meltano the way you've been doing it so far,
and leverage environments whenever you need to starting switching between different sets of configurations.
