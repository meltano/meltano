---
description: A Meltano project's primary components are its plugins, that implement the various details of your ELT pipelines.
---

# Plugins

A [Meltano project](/docs/project.html)'s primary components are its plugins,
that implement the various details of your ELT pipelines.

Meltano knows the following types of plugins:

- [Extractors](#extractors)
- [Loaders](#loaders)
- [Transforms](#transforms)
- [Models](#models)
- [Dashboards](#dashboards)
- [Orchestrators](#orchestrators)
- [Transformers](#transformers)
- [File bundles](#file-bundles)

To learn how to manage your project's plugins, refer to the [Plugin Management guide](/docs/plugin-management.html).

## Extractors

Extractors are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for pulling data out of arbitrary data sources: databases, SaaS APIs, or file formats.

Meltano supports [Singer taps](https://singer.io): executables that implement the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

To learn which extractors are [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box, refer to the [Extractors page](/plugins/extractors/).

### `catalog` extra

- Setting: `_catalog`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__CATALOG`, e.g. `TAP_GITLAB__CATALOG`
- [`meltano elt`](/docs/command-line-interface.html#elt) CLI option: `--catalog`
- Default: None

An extractor's `catalog` [extra](/docs/configuration.html#plugin-extras) holds a path to a [catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#the-catalog) (relative to the [project directory](/docs/project.html)) to be provided to the extractor
when it is run in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md) using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If a catalog path is not set, the catalog will be [generated on the fly](/docs/integration.html#extractor-catalog-generation)
by running the extractor in [discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md) and applying the [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules to the discovered file.

[Selection filter rules](#select-filter-extra) are always applied to manually provided catalogs as well as discovered ones.

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
a catalog file is typically provided using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--catalog` option.

#### How to use

##### In `meltano.yml`

```yaml{4}
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  catalog: extract/tap-gitlab.catalog.json
```

##### On the command line

```bash
meltano config <extractor> set _catalog <path>

export <EXTRACTOR>__CATALOG=<path>

meltano elt <extractor> <loader> --catalog <path>

# For example:
meltano config tap-gitlab set _catalog extract/tap-gitlab.catalog.json

export TAP_GITLAB__CATALOG=extract/tap-gitlab.catalog.json

meltano elt tap-gitlab target-jsonl --catalog extract/tap-gitlab.catalog.json
```

### `load_schema` extra

- Setting: `_load_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__LOAD_SCHEMA`, e.g. `TAP_GITLAB__LOAD_SCHEMA`
- Default: `$MELTANO_EXTRACTOR_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the extractor's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

An extractor's `load_schema` [extra](/docs/configuration.html#plugin-extras)
holds the name of the database schema extracted data should be loaded into,
when this extractor is used in a pipeline with a [loader](#loaders) for a database that supports schemas, like [PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html) or [Snowflake](https://docs.snowflake.com/en/sql-reference/ddl-database.html).

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a loader's configuration using the `MELTANO_EXTRACT__LOAD_SCHEMA`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is used as the default value for the [`target-postgres`](/plugins/loaders/postgres.html) and [`target-snowflake`](/plugins/loaders/snowflake.html) `schema` settings.

#### How to use

##### In `meltano.yml`

```yaml{4}
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  load_schema: gitlab_data
```

##### On the command line

```bash
meltano config <extractor> set _load_schema <schema>

export <EXTRACTOR>__LOAD_SCHEMA=<schema>

# For example:
meltano config tap-gitlab set _load_schema gitlab_data

export TAP_GITLAB__LOAD_SCHEMA=gitlab_data
```

### `metadata` extra

- Setting: `_metadata`, alias: `metadata`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__METADATA`, e.g. `TAP_GITLAB__METADATA`
- Default: `{}` (an empty object)

An extractor's `metadata` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
rules that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

Stream (entity) metadata `<key>: <value>` pairs (e.g. `{"replication-method": "INCREMENTAL"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<key>`.

Property (attribute) metadata `<key>: <value>` pairs (e.g. `{"is-replication-key": true}`) are nested under top-level entity identifiers and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

#### How to use

##### In `meltano.yml`

```yaml{4-9}
extractors:
- name: tap-postgres
  pip_url: tap-postgres
  metadata:
    some_table:
      replication-method: INCREMENTAL
      replication-key: created_at
      created_at:
        is-replication-key: true
```

##### On the command line

```bash
meltano config <extractor> set _metadata <entity> <key> <value>
meltano config <extractor> set _metadata <entity> <attribute> <key> <value>

export <EXTRACTOR>__METADATA='{"<entity>": {"<key>": "<value>", "<attribute>": {"<key>": "<value>"}}}'

# Once metadata has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <EXTRACTOR>__METADATA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table replication-method INCREMENTAL
meltano config tap-postgres set _metadata some_table replication-key created_at
meltano config tap-postgres set _metadata some_table created_at is-replication-key true

export TAP_POSTGRES__METADATA_SOME_TABLE_REPLICATION_METHOD=FULL_TABLE
```

### `schema` extra

- Setting: `_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__SCHEMA`, e.g. `TAP_GITLAB__SCHEMA`
- Default: `{}` (an empty object)

An extractor's `schema` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) override
rules that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

[JSON Schema](https://json-schema.org/) descriptions for specific properties (attributes) (e.g. `{"type": ["string", "null"], "format": "date-time"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values, and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_schema.<entity>.<attribute>` and `_schema.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

If a schema is specified for a property that does not yet exist in the discovered stream's schema, the property (and its schema) will be added to the catalog.
This allows you to define a full schema for taps such as [`tap-dynamo-db`](https://github.com/singer-io/tap-dynamodb) that do not themselves have the ability to discover the schema of their streams.

#### How to use

##### In `meltano.yml`

```yaml{4-8}
extractors:
- name: tap-postgres
  pip_url: tap-postgres
  schema:
    some_table:
      created_at:
        type: ["string", "null"]
        format: date-time
```

##### On the command line

```bash
meltano config <extractor> set _schema <entity> <attribute> <schema description>
meltano config <extractor> set _schema <entity> <attribute> <key> <value>

export <EXTRACTOR>__SCHEMA='{"<entity>": {"<attribute>": {"<key>": "<value>"}}}'

# Once schema descriptions have been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <EXTRACTOR>__SCHEMA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table created_at type '["string", "null"]'
meltano config tap-postgres set _metadata some_table created_at format date-time

export TAP_POSTGRES__SCHEMA_SOME_TABLE_CREATED_AT_FORMAT=date
```

### `select` extra

- Setting: `_select`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__SELECT`, e.g. `TAP_GITLAB__SELECT`
- Default: `["*.*"]`

An extractor's `select` [extra](/docs/configuration.html#plugin-extras) holds an array of [entity selection rules](/docs/command-line-interface.html#select)
that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

A selection rule is comprised of an entity identifier that corresponds to a Singer stream's `tap_stream_id` value, and an attribute identifier that that corresponds to a Singer stream property name, separated by a period (`.`). Rules indicating that an entity or attribute should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
selection rules are typically specified using [`meltano select`](/docs/command-line-interface.html#select).

#### How to use

##### In `meltano.yml`

```yaml{4-6}
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  select:
  - project_members.*
  - commits.*
```

##### On the command line

```bash
meltano config <extractor> set _select '["<entity>.<attribute>", ...]'

export <EXTRACTOR>__SELECT='["<entity>.<attribute>", ...]'

meltano select <extractor> <entity> <attribute>

# For example:
meltano config tap-gitlab set _select '["project_members.*", "commits.*"]'

export TAP_GITLAB__SELECT='["project_members.*", "commits.*"]'

meltano select tap-gitlab project_members "*"
meltano select tap-gitlab commits "*"
```

### `select_filter` extra

- Setting: `_select_filter`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__SELECT_FILTER`, e.g. `TAP_GITLAB__SELECT_FILTER`
- [`meltano elt`](/docs/command-line-interface.html#elt) CLI options: `--select` and `--exclude`
- Default: `[]`

An extractor's `select_filter` [extra](/docs/configuration.html#plugin-extras) holds an array of [entity selection](#select-extra) filter rules
that are applied to the extractor's [discovered](/docs/integration.html#extractor-catalog-generation) or [provided](#catalog-extra) catalog file
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke),
after [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules are applied.

It can be used to only extract records for specific matching entities, or to extract records for all entities _except_ for those specified, by letting you apply filters on top of configured [entity selection rules](#select-extra).

Selection filter rules use entity identifiers that correspond to Singer stream `tap_stream_id` values. Rules indicating that an entity should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity identifiers to match multiple entities at once.

Entity names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
selection filers are typically specified using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--select` and `--exclude` options.

#### How to use

##### In `meltano.yml`

```yaml{7-8}
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  select:
  - project_members.*
  - commits.*
  select_filter:
  - commits
```

##### On the command line

```bash
meltano config <extractor> set _select_filter '["<entity>", ...]'
meltano config <extractor> set _select_filter '["!<entity>", ...]'

export <EXTRACTOR>__SELECT_FILTER='["<entity>", ...]'
export <EXTRACTOR>__SELECT_FILTER='["!<entity>", ...]'

meltano elt <extractor> <loader> --select <entity>
meltano elt <extractor> <loader> --exclude <entity>

# For example:
meltano config tap-gitlab set _select_filter '["commits"]'
meltano config tap-gitlab set _select_filter '["!project_members"]'

export TAP_GITLAB__SELECT_FILTER='["commits"]'
export TAP_GITLAB__SELECT_FILTER='["!project_members"]'

meltano elt tap-gitlab target-jsonl --select commits
meltano elt tap-gitlab target-jsonl --exclude project_members
```

### `state` extra

- Setting: `_state`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__STATE`, e.g. `TAP_GITLAB__STATE`
- [`meltano elt`](/docs/command-line-interface.html#elt) CLI option: `--state`
- Default: None

An extractor's `state` [extra](/docs/configuration.html#plugin-extras) holds a path to a [state file](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file) (relative to the [project directory](/docs/project.html)) to be provided to the extractor
when it is run as part of a pipeline using [`meltano elt`](/docs/command-line-interface.html#elt).

If a state path is not set, the state will be [looked up automatically](/docs/integration.html#pipeline-state) based on the ELT run's Job ID.

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
a state file is typically provided using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--state` option.

#### How to use

##### In `meltano.yml`

```yaml{4}
extractors:
- name: tap-gitlab
  pip_url: tap-gitlab
  state: extract/tap-gitlab.state.json
```

##### On the command line

```bash
meltano config <extractor> set _state <path>

export <EXTRACTOR>__STATE=<path>

meltano elt <extractor> <loader> --state <path>

# For example:
meltano config tap-gitlab set _state extract/tap-gitlab.state.json

export TAP_GITLAB__STATE=extract/tap-gitlab.state.json

meltano elt tap-gitlab target-jsonl --state extract/tap-gitlab.state.json
```

## Loaders

Loaders are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for loading [extracted](#extractors) data into arbitrary data destinations: databases, SaaS APIs, or file formats.

Meltano supports [Singer targets](https://singer.io): executables that implement the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

To learn which loaders are [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box, refer to the [Loaders page](/plugins/loaders/).

### `dialect` extra

- Setting: `_dialect`
- [Environment variable](/docs/configuration.html#configuring-settings): `<LOADER>__DIALECT`, e.g. `TARGET_POSTGRES__DIALECT`
- Default: `$MELTANO_LOADER_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the loader's `namespace`, e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`

A loader's `dialect` [extra](/docs/configuration.html#plugin-extras)
holds the name of the dialect of the target database, so that
[transformers](#transformers) in the same pipeline and [Meltano UI](/docs/ui.html)'s [Analysis feature](/docs/analysis.html)
can determine the type of database to connect to.

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_LOAD__DIALECT`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is used as the default value for `dbt`'s `target` setting, and should therefore correspond to a target name in `transform/profile/profiles.yml`.

#### How to use

##### In `meltano.yml`

```yaml{4}
loaders:
- name: target-example-db
  pip_url: target-example-db
  dialect: example-db
```

##### On the command line

```bash
meltano config <loader> set _dialect <dialect>

export <LOADER>__DIALECT=<dialect>

# For example:
meltano config target-example-db set _dialect example-db

export TARGET_EXAMPLE_DB__DIALECT=example-db
```

### `target_schema` extra

- Setting: `_target_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `<LOADER>__TARGET_SCHEMA`, e.g. `TARGET_POSTGRES__TARGET_SCHEMA`
- Default: `$MELTANO_LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the loader's `schema` setting

A loader's `target_schema` [extra](/docs/configuration.html#plugin-extras)
holds the name of the database schema the loader has been configured to load data into (assuming the destination supports schemas), so that
[transformers](#transformers) in the same pipeline and [Meltano UI](/docs/ui.html)'s [Analysis feature](/docs/analysis.html)
can determine the database schema to load data from.

The value of this extra is usually not set explicitly, since its should correspond to the value of the loader's own "target schema" setting.
If the name of this setting is not `schema`, its value [can be referenced](/docs/configuration.html#expansion-in-setting-values) from the extra's value using `$MELTANO_LOAD_<TARGET_SCHEMA_SETTING>`, e.g. `$MELTANO_LOAD_DESTINATION_SCHEMA` for setting `destination_schema`.

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_LOAD__TARGET_SCHEMA`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is used as the default value for `dbt`'s `source_schema` setting.

#### How to use

##### In `meltano.yml`

```yaml{6}
loaders:
- name: target-example-db
  pip_url: target-example-db
  settings:
  - name: destination_schema
  target_schema: $MELTANO_LOAD_DESTINATION_SCHEMA # Value of `destination_schema` setting
```

##### On the command line

```bash
meltano config <loader> set _target_schema <schema>

export <LOADER>__TARGET_SCHEMA=<schema>

# For example:
meltano config target-example-db set _target_schema '$MELTANO_LOAD_DESTINATION_SCHEMA'

# If the target schema cannot be determined dynamically using a setting reference:
meltano config target-example-db set _target_schema explicit_target_schema

export TARGET_EXAMPLE_DB__TARGET_SCHEMA=explicit_target_schema
```

## Transforms

Transforms are [dbt packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) containing [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models),
that are used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).

Together with the [dbt](https://www.getdbt.com) [transformer](#transformers), they are responsible for transforming data that has been loaded into a database (data warehouse) into a different format, usually one more appropriate for [analysis](/docs/analysis.html).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the [dbt package Git repository](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages) referenced by its `pip_url`
will be added to your project's `transform/packages.yml` and the package will be enabled in `transform/dbt_project.yml`.

### `package_name` extra

- Setting: `_package_name`
- [Environment variable](/docs/configuration.html#configuring-settings): `<TRANSFORM>__PACKAGE_NAME`, e.g. `TAP_GITLAB__PACKAGE_NAME`
- Default: `$MELTANO_TRANSFORM_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the transform's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

A transform's `package_name` [extra](/docs/configuration.html#plugin-extras)
holds the name of the dbt package's internal dbt project: the value of `name` in `dbt_project.yml`.

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add), this name will be added to the `models` dictionary in `transform/dbt_project.yml`.

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_TRANSFORM__PACKAGE_NAME`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is included in the default value for `dbt`'s `models` setting: `$MELTANO_TRANSFORM__PACKAGE_NAME $MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`.

#### How to use

##### In `meltano.yml`

```yaml{5}
transforms:
- name: dbt-facebook-ads
  namespace: tap_facebook
  pip_url: https://github.com/fishtown-analytics/facebook-ads
  package_name: facebook_ads
```

##### On the command line

```bash
meltano config <transform> set _package_name <name>

export <TRANSFORM>__PACKAGE_NAME=<name>

# For example:
meltano config dbt-facebook-ads set _package_name facebook_ads

export DBT_FACEBOOK_ADS__PACKGE_NAME=facebook_ads
```

### `vars` extra

- Setting: `_vars`
- [Environment variable](/docs/configuration.html#configuring-settings): `<TRANSFORM>__VARS`, e.g. `TAP_GITLAB__VARS`
- Default: `{}` (an empty object)

A transform's `vars` [extra](/docs/configuration.html#plugin-extras) holds an object representing [dbt model variables](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-variables)
that can be referenced from a model using the [`var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/var).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add), this object will be used as the dbt model's `vars` object in `transform/dbt_project.yml`.

Because these variables are handled by dbt rather than Meltano, [environment variables](/docs/configuration.html#expansion-in-setting-values) can be referenced using the [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) instead of `$VAR` or `${VAR}`.

#### How to use

##### In `meltano.yml`

```yaml{4-5}
transforms:
- name: tap-gitlab
  pip_url: dbt-tap-gitlab
  vars:
    schema: '{{ env_var(''DBT_SOURCE_SCHEMA'') }}'
```

##### On the command line

```bash
meltano config <transform> set _vars <key> <value>

export <TRANSFORM>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'
```

## Models

Models are [pip packages](https://pip.pypa.io/en/stable/) used by [Meltano UI](/docs/ui.html) to aid in [data analysis](/docs/analysis.html).
They describe the schema of the data being analyzed and the ways different tables can be joined,
and are used to automatically generate SQL queries using a point-and-click interface.

## Dashboards

Dashboards are [pip packages](https://pip.pypa.io/en/stable/) bundling curated [Meltano UI](/docs/ui.html) dashboards and reports.

When a dashboard is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled dashboards and reports will automatically be added to your project's `analyze` directory as well.

## Orchestrators

Orchestrators are [pip packages](https://pip.pypa.io/en/stable/) responsible for [orchestrating](/docs/orchestration.html) a project's [scheduled pipelines](/docs/command-line-interface.html#schedule).

Meltano supports [Apache Airflow](https://airflow.apache.org/) out of the box, but can be used with any tool capable of reading the output of [`meltano schedule list --format=json`](/docs/command-line-interface.html#schedule) and executing each pipeline's [`meltano elt`](/docs/command-line-interface.html#elt) command on a schedule.

When the `airflow` orchestrator is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

## Transformers

Transformers are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).
They are responsible for running [transforms](#transforms).

Meltano supports [dbt](https://www.getdbt.com) and its [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) out of the box.

When the `dbt` transformer is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

## File bundles

File bundles are [pip packages](https://pip.pypa.io/en/stable/) bundling files you may want in your Meltano project.

When a file bundle is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled files will automatically be added as well.
The file bundle itself will not be added to your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) unless it contains files that are
[managed by the file bundle](#update-extra) and to be updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run.

### `update` extra

- Setting: `_update`
- [Environment variable](/docs/configuration.html#configuring-settings): `<BUNDLE>__UPDATE`, e.g. `DBT__UPDATE`
- Default: `{}` (an empty object)

A file bundle's `update` [extra](/docs/configuration.html#plugin-extras) holds an object mapping file paths (of files inside the bundle, relative to the project root) to booleans.

When a file path's value is `True`, the file is considered to be managed by the file bundle and updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run.

#### How to use

##### In `meltano.yml`

```yaml{4-5}
files:
- name: dbt
  pip_url: files-dbt
  update:
    transform/dbt_project.yml: false
```

##### On the command line

```bash
meltano config <bundle> set _update <path> <true/false>

export <BUNDLE>__UPDATE='{"<path>": <true/false>}'

# For example:
meltano config --plugin-type=files dbt set _update transform/dbt_project.yml false

export DBT__UPDATE='{"transform/dbt_project.yml": false}'
```
