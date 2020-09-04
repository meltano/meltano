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

### `metadata` extra

- Setting: `_metadata`, alias: `metadata`
- Environment variable: `<NAMESPACE>__METADATA`
- Default: `{}` (an empty object)

An extractor's `metadata` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
rules that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

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
meltano config <plugin> set _metadata <entity> <key> <value>
meltano config <plugin> set _metadata <entity> <attribute> <key> <value>

export <NAMESPACE>__METADATA='{"<entity>": {"<key>": "<value>", "<attribute>": {"<key>": "<value>"}}}'

# Once metadata has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <NAMESPACE>__METADATA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table replication-method INCREMENTAL
meltano config tap-postgres set _metadata some_table replication-key created_at
meltano config tap-postgres set _metadata some_table created_at is-replication-key true

export TAP_POSTGRES__METADATA_SOME_TABLE_REPLICATION_METHOD=FULL_TABLE
```

### `schema` extra

- Setting: `_schema`
- Environment variable: `<NAMESPACE>__SCHEMA`
- Default: `{}` (an empty object)

An extractor's `schema` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) override
rules that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

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
meltano config <plugin> set _schema <entity> <attribute> <schema description>
meltano config <plugin> set _schema <entity> <attribute> <key> <value>

export <NAMESPACE>__SCHEMA='{"<entity>": {"<attribute>": {"<key>": "<value>"}}}'

# Once schema descriptions have been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <NAMESPACE>__SCHEMA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_table created_at type '["string", "null"]'
meltano config tap-postgres set _metadata some_table created_at format date-time

export TAP_POSTGRES__SCHEMA_SOME_TABLE_CREATED_AT_FORMAT=date
```

### `select` extra

- Setting: `_select`
- Environment variable: `<NAMESPACE>__SELECT`
- Default: `["*.*"]`

An extractor's `select` [extra](/docs/configuration.html#plugin-extras) holds an array of [entity selection rules](/docs/command-line-interface.html#select)
that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

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
meltano config <plugin> set _select '["<entity>.<attribute>", ...]'

export <NAMESPACE>__SELECT='["<entity>.<attribute>", ...]'

meltano select <plugin> <entity> <attribute>

# For example:
meltano config tap-gitlab set _select '["project_members.*", "commits.*"]'

export TAP_GITLAB__SELECT='["project_members.*", "commits.*"]'

meltano select tap-gitlab project_members "*"
meltano select tap-gitlab commits "*"
```

### `select_filter` extra

- Setting: `_select_filter`
- Environment variable: `<NAMESPACE>__SELECT_FILTER`
- Default: `[]`

An extractor's `select_filter` [extra](/docs/configuration.html#plugin-extras) holds an array of [entity selection](#select-extra) filter rules
that are applied to the extractor's [discovered catalog file](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke),
after [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules are applied.

It can be used to only extract records for specific matching entities, or to extract records for all entities _except_ for those specified, by letting you apply filters on top of configured [entity selection rules](#select-extra).

Selection filter rules use entity identifiers that correspond to Singer stream `tap_stream_id` values. Rules indicating that an entity should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity identifiers to match multiple entities at once.

Entity names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

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
meltano config <plugin> set _select_filter '["<entity>", ...]'
meltano config <plugin> set _select_filter '["!<entity>", ...]'

export <NAMESPACE>__SELECT_FILTER='["<entity>", ...]'
export <NAMESPACE>__SELECT_FILTER='["!<entity>", ...]'

# For example:
meltano config tap-gitlab set _select_filter '["commits"]'
meltano config tap-gitlab set _select_filter '["!project_members"]'

export TAP_GITLAB__SELECT_FILTER='["commits"]'
export TAP_GITLAB__SELECT_FILTER='["!project_members"]'
```

## Loaders

Loaders are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for loading [extracted](#extractors) data into arbitrary data destinations: databases, SaaS APIs, or file formats.

Meltano supports [Singer targets](https://singer.io): executables that implement the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

To learn which loaders are [known to Meltano](/docs/contributor-guide.html#known-plugins) and supported out of the box, refer to the [Loaders page](/plugins/loaders/).

## Transforms

Transforms are [dbt packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) containing [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models),
that are used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).

Together with the [dbt](https://www.getdbt.com) [transformer](#transformers), they are responsible for transforming data that has been loaded into a database (data warehouse) into a different format, usually one more appropriate for [analysis](/docs/analysis.html).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the [dbt package Git repository](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages) referenced by its `pip_url`
will be added to your project's `transform/packages.yml` and the package will be enabled in `transform/dbt_project.yml`.

### `vars` extra

- Setting: `_vars`
- Environment variable: `<NAMESPACE>__VARS`
- Default: `{}` (an empty object)

A transform's `vars` [extra](/docs/configuration.html#plugin-extras) holds an object representing [dbt model variables](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-variables)
that can be referenced from a model using the [`var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/var).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add), this object will be used as the dbt model's `vars` object in `transform/dbt_project.yml`.

Because these variables are handled by dbt rather than Meltano, environment variables (including Meltano's [pipeline environment variables](/docs/integration.html#pipeline-environment-variables)) can be referenced using the [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) instead of `$VAR` or `${VAR}`.

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
meltano config <plugin> set _vars <key> <value>

export <NAMESPACE>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'
```

## Models

Models are [pip packages](https://pip.pypa.io/en/stable/) used by [Meltano UI](/docs/command-line-interface.html#ui) to aid in [data analysis](/docs/analysis.html).
They describe the schema of the data being analyzed and the ways different tables can be joined,
and are used to automatically generate SQL queries using a point-and-click interface.

## Dashboards

Dashboards are [pip packages](https://pip.pypa.io/en/stable/) bundling curated [Meltano UI](/docs/command-line-interface.html#ui) dashboards and reports.

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
- Environment variable: `<NAMESPACE>__UPDATE`
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
meltano config <plugin> set _update <path> <true/false>

export <NAMESPACE>__UPDATE='{"<path>": <true/false>}'

# For example:
meltano config --plugin-type=files dbt set _update transform/dbt_project.yml false

export DBT__UPDATE='{"transform/dbt_project.yml": false}'
```
