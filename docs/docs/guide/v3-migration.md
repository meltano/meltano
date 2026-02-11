---
title: Meltano 3.0 Migration Guide
description: Migrate existing "v2" projects to the latest version of Meltano
layout: doc
sidebar_position: 21
---

The following list includes all recommended migration tasks as well as breaking changes in Meltano version `3.0.0`.

## Recommended

## Changed

### Using Postgres as a backend now requires installing Meltano with extra components

If you are already using Postgres as a backend, odds are you rely on Meltano's dependency on `psycopg2`, so you will need to install Meltano with the `psycopg2` extra:

```bash
pipx install "meltano[psycopg2]"
```

If you are setting a Postgres backend for the first time, it's recommended to instead use the `postgres` extra and use the `postgresql+psycopg` URI scheme:

```bash
pipx install "meltano[postgres]"
meltano config meltano set database_uri postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
```

### Plugin lock files are now always required

Plugin [lock files](/concepts/plugins#lock-artifacts) are now always required.

Before this, Meltano fell back to retrieving the plugin definition from Meltano Hub if the lock file was missing. This behavior caused issues when lock files were not deployed to production and Meltano Hub was unavailable because of network restrictions.

#### Migration steps

1. Enable the `ff.plugin_locks_required` feature flag:

```bash
meltano config meltano set ff.plugin_locks_required true
```

2. Test that your project still works as expected. For example, by installing all plugins:

```bash
meltano install
```

3. Generate all lock files for your project:

```bash
meltano lock
```

4. (Optional) Remove the `ff.plugin_locks_required` feature flag after upgrading to Meltano v3, since it has no effect in Meltano v3.

:::tip
<p>For <a href="/guide/plugin-management/#custom-plugins">custom plugins</a>, you might need to add a <code>namespace</code> to the plugin definition.</p>
:::

## Removed

### Target extra setting `target_schema`

In line with the deprecation of the [`meltano elt`](/reference/command-line-interface#elt) command in favor of [`meltano el`](/reference/command-line-interface#el), the `target_schema` extra setting of [loaders](/concepts/plugins#loaders) has been removed.

This should impact very few users, as the `target_schema` extra setting was only used by the [`dbt` transformer](/concepts/plugins#transformers), which has been deprecated in favor of [adapter-specific dbt utilities](/guide/migrate-an-existing-dbt-project/#add-dbt-transformer).

#### Migration steps

1. In the configuration for the `dbt` transformer plugin, set the `source_schema` value to the appropriate environment variable for your target (e.g. [`$MELTANO_LOAD__DEFAULT_TARGET_SCHEMA`](https://hub.meltano.com/loaders/target-postgres#default_target_schema-setting) for Postgres).

### The Meltano UI

Before Meltano `v3.0.0`, Meltano included a web-UI that could be hosted by running `meltano ui`. In Meltano `v2.12.0`, this UI was deprecated. In Meltano `v3.0.0`, this UI has been removed. Everything that was possible through the UI is possible without it via the CLI, or by directly editing `meltano.yml`.
