---
title: Plugins
description: Meltano takes a modular approach to data engineering and EL(T), where your project and pipelines are composed of plugins.
layout: doc
redirect_from:
  - /guide/analysis
weight: 2
---

Meltano takes a modular approach to data engineering in general and EL(T) in particular,
where your [project](project) and pipelines are composed of plugins of [different types](#types), most notably
[**extractors**](#extractors) ([Singer](https://singer.io) taps),
[**loaders**](#loaders) ([Singer](https://singer.io) targets),
[**transformers**](#transformers) ([dbt](https://www.getdbt.com) and [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)), and
[**orchestrators**](#orchestrators) (currently [Airflow](https://airflow.apache.org/), with [Dagster](https://dagster.io/) [in development](https://github.com/meltano/meltano/issues/2349)).

Meltano provides the glue to make these components work together smoothly and enables consistent [configuration](/guide/configuration) and [deployment](/guide/production).

To learn how to manage your project's plugins, refer to the [Plugin Management guide](/guide/plugin-management).

## Project Plugins

In order to use a given package as a plugin in a [project](project),
assuming it meets the requirements of the [plugin type](#types) in question, Meltano needs to know:

1. where to find the package, typically a [pip package](https://pip.pypa.io/en/stable/) identified by its name on [PyPI](https://pypi.org/), public or private Git repository URL, or local directory path,
2. what [settings](/guide/configuration) it supports
3. what [capabilities](/reference/plugin-definition-syntax#capabilities) it supports, and finally
4. what its [configuration](/guide/configuration) should be when invoked.

Together, a package's location (1) and the metadata (2) describing it in terms Meltano can understand make up the **base plugin description**.
In your project, **plugins** extend this description with a specific configuration (3) and a unique name.

This means that [different configurations](/guide/configuration#multiple-plugin-configurations) of the same package (base plugin)
would be represented in your project as separate plugins with their own unique names,
that can be thought of as differently initialized instances of the same class.
For example: extractors `tap-postgres--billing` and `tap-postgres--events` derived from base extractor [`tap-postgres`](https://hub.meltano.com/extractors/postgres.html),
or `tap-google-analytics--client-foo` and `tap-google-analytics--client-bar` derived from base extractor [`tap-google-analytics`](https://hub.meltano.com/extractors/google-analytics.html).

Each plugin in a project can either:

- inherit its base plugin description from a [discoverable plugin](#discoverable-plugins) that's supported out of the box,
- define its base plugin description explicitly, making it a [custom plugin](#custom-plugins), or
- [inherit](#plugin-inheritance) both base plugin description and configuration from another plugin in the project.

To learn how to add a plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#adding-a-plugin-to-your-project).

## Discoverable plugins

[Base plugin descriptions](#project-plugins) for many popular [extractors](#extractors) (Singer taps), [loaders](#loaders) (Singer targets),
and other plugins have already been collected by users and [contributed](/contribute/plugins#discoverable-plugins) to [Meltano Hub](https://hub.meltano.com),
making them supported out of the box.

To find discoverable plugins, run [`meltano discover`](/reference/command-line-interface#discover) or refer to the lists of [Extractors](https://hub.meltano.com/extractors/), [Loaders](https://hub.meltano.com/loaders/), etc.

To learn how to add a discoverable plugin to your project using a [shadowing plugin definition](project#shadowing-plugin-definitions) or [inheriting plugin definition](project#inheriting-plugin-definitions), refer to the [Plugin Management guide](/guide/plugin-management#discoverable-plugins).

### Variants

In the case of various popular data sources and destinations, multiple alternative implementations of Singer taps ([extractors](#extractors)) and targets ([loaders](#loaders)) exist,
some of which are forks of an original (canonical) version that evolved in their own direction, while others were developed independently from the start.

These different implementations and their repositories typically use the same name (`tap-<source>` or `target-<destination>`)
and may on the surface appear interchangeable, but often vary significantly in terms of exact behavior, quality, and supported settings.

In its [index of discoverable plugins](#discoverable-plugins), Meltano considers these different implementations different _variants_ of the same plugin,
that share a plugin name and other source/destination-specific details (like a logo and description),
but have their own implementation-specific variant name and metadata (like capabilities and settings).

Every discoverable plugin has a default variant that is known to work well and recommended for new users,
which will be added to your project unless you explicitly select a different one.
Users who already have experience with a different variant (or have specific reasons to prefer it) can explicitly choose to add it to their project instead of the default,
so that they get the same behavior and can use the same settings as before.
If the variant in question is not discoverable yet, it can be added as a [custom plugin](#custom-plugins).

When multiple variants of a discoverable plugin are available, [`meltano discover`](/reference/command-line-interface#discover) will list their names alongside the plugin name.

To learn how to add a non-default variant of a discoverable plugin to your project, refer to the [Plugin Management guide](/guide/plugin-management#variants).

## Custom plugins

If you'd like to use a package in your project whose [base plugin description](#project-plugins) isn't [discoverable](#discoverable-plugins) yet,
you'll need to collect and provide this metadata yourself.

To learn how to add a custom plugin to your project using a [custom plugin definition](project#custom-plugin-definitions), refer to the [Plugin Management guide](/guide/plugin-management#custom-plugins).

<div class="notification is-warning">
  <p>Once you've got the plugin working in your project, please consider <a href="/contribute/plugins#discoverable-plugins">contributing its description</a> to <a href="https://github.com/meltano/hub/issues/new">Meltano Hub</a> to make it discoverable and supported out of the box for new users!</p>
</div>

## Plugin Inheritance

If you'd like to use the same package (base plugin) in your project multiple times with [different configurations](/guide/configuration#multiple-plugin-configurations),
you can add a new plugin that inherits from an existing one.

The new plugin will inherit its parent's [base plugin description](#project-plugins) and [configuration](/guide/configuration) as if they were defaults,
which can then be overridden as appropriate.

For performance reasons, inherited plugins with an identical `pip_url` to their parent share the parents underlying python virtualenv.
If you would prefer to create a separate virtualenv for an inherited plugin, modify it's `pip_url` to be different to its parent.

To learn how to add an inheriting plugin to your project using an [inheriting plugin definition](project#inheriting-plugin-definitions), refer to the [Plugin Management guide](/guide/plugin-management#plugin-inheritance).

## Lock artifacts

When you add a plugin to your project using `meltano add`, the [discoverable plugin definition](#discoverable-plugins) of the plugin will be downloaded and added to your project under `plugins/<plugin_type>/<plugin_name>--<variant_name>.lock`. This will ensure that the plugin's definition will be stable and version-controlled.

Later invocations of the plugin will use this file to determine the settings, installation source, etc.

<div class="notification is-info">
  <p>Note that <a href="#custom-plugins">custom</a> and <a href="#plugin-inheritance">inherited</a> plugins
  do not get a lock file.
  </p>
</div>

## Types

Meltano supports the following types of plugins:

- [**Extractors**](#extractors) pull data out of arbitrary data sources.
- [**Mappers**](#mappers) perform stream map transforms on data between extractors and loaders.
- [**Loaders**](#loaders) load extracted data into arbitrary data destinations.
- [**Transforms**](#transforms) transform data that has been loaded into a database (data warehouse).
- [**Orchestrators**](#orchestrators) orchestrate a project's scheduled pipelines.
- [**Transformers**](#transformers) run transforms.
- [**File bundles**](#file-bundles) bundle files you may want in your project.
- [**Utilities**](#utilities) perform arbitrary tasks provided by [pip packages](https://pip.pypa.io/en/stable/) with executables.

### Extractors

Extractors are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/reference/command-line-interface#elt) as part of [data integration](/guide/integration).
They are responsible for pulling data out of arbitrary data sources: databases, SaaS APIs, or file formats.

Meltano supports [Singer taps](https://singer.io): executables that implement the [Singer specification](https://hub.meltano.com/singer/spec).

To learn which extractors are [discoverable](#discoverable-plugins) and supported out of the box, refer to the [Extractors page](https://hub.meltano.com/extractors/) or run [`meltano discover extractors`](/reference/command-line-interface#discover).

#### Extras

Extractors support the following [extras](/guide/configuration#plugin-extras):

- [`catalog`](#catalog-extra)
- [`load_schema`](#load-schema-extra)
- [`metadata`](#metadata-extra)
- [`schema`](#schema-extra)
- [`select`](#select-extra)
- [`select_filter`](#select-filter-extra)
- [`state`](#state-extra)

#### `catalog` extra

- Setting: `_catalog`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__CATALOG`, e.g. `TAP_GITLAB__CATALOG`
- [`meltano elt`](/reference/command-line-interface#elt) CLI option: `--catalog`
- Default: None

An extractor's `catalog` [extra](/guide/configuration#plugin-extras) holds a path to a [catalog file](https://hub.meltano.com/singer/spec#catalog-files) (relative to the [project directory](project)) to be provided to the extractor
when it is run in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md) using [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).

If a catalog path is not set, the catalog will be [generated on the fly](/guide/integration#extractor-catalog-generation)
by running the extractor in [discovery mode](https://hub.meltano.com/singer/spec#discovery-mode) and applying the [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules to the discovered file.

[Selection filter rules](#select-filter-extra) are always applied to manually provided catalogs as well as discovered ones.

While this extra can be managed using [`meltano config`](/reference/command-line-interface#config) or environment variables like any other setting,
a catalog file is typically provided using [`meltano elt`](/reference/command-line-interface#elt)'s `--catalog` option.

If the catalog does not seem to take effect, you may need to [validate the capabilities of the tap](/guide/integration#validate-tap-capabilities).

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  catalog: extract/tap-gitlab.catalog.json
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <extractor> set _catalog <path>

export <EXTRACTOR>__CATALOG=<path>

meltano elt <extractor> <loader> --catalog <path>

# For example:
meltano config tap-gitlab set _catalog extract/tap-gitlab.catalog.json

export TAP_GITLAB__CATALOG=extract/tap-gitlab.catalog.json

meltano elt tap-gitlab target-jsonl --catalog extract/tap-gitlab.catalog.json
```

#### <a name="load-schema-extra"></a>`load_schema` extra

- Setting: `_load_schema`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__LOAD_SCHEMA`, e.g. `TAP_GITLAB__LOAD_SCHEMA`
- Default: `$MELTANO_EXTRACTOR_NAMESPACE`, which [will expand to](/guide/configuration#expansion-in-setting-values) the extractor's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

An extractor's `load_schema` [extra](/guide/configuration#plugin-extras)
holds the name of the database schema extracted data should be loaded into,
when this extractor is used in a pipeline with a [loader](#loaders) for a database that supports schemas, like [PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html) or [Snowflake](https://docs.snowflake.com/en/sql-reference/ddl-database.html).

The value of this extra [can be referenced](/guide/configuration#expansion-in-setting-values) from a loader's configuration using the `MELTANO_EXTRACT__LOAD_SCHEMA`
[pipeline environment variable](/guide/integration#pipeline-environment-variables).
It is used as the default value for the [`target-postgres`](https://hub.meltano.com/loaders/postgres.html) and [`target-snowflake`](https://hub.meltano.com/loaders/snowflake.html) `schema` settings.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  load_schema: gitlab_data
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <extractor> set _load_schema <schema>

export <EXTRACTOR>__LOAD_SCHEMA=<schema>

# For example:
meltano config tap-gitlab set _load_schema gitlab_data

export TAP_GITLAB__LOAD_SCHEMA=gitlab_data
```

#### `metadata` extra

- Setting: `_metadata`, alias: `metadata`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__METADATA`, e.g. `TAP_GITLAB__METADATA`
- Default: `{}` (an empty object)

An extractor's `metadata` [extra](/guide/configuration#plugin-extras) holds an object describing
[Singer stream and property metadata](https://hub.meltano.com/singer/spec#metadata)
rules that are applied to the extractor's [discovered catalog file](https://hub.meltano.com/singer/spec#catalog-files)
when the extractor is run using [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

Stream (entity) metadata `<key>: <value>` pairs (e.g. `{"replication-method": "INCREMENTAL"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values.
These [nested properties](/reference/command-line-interface#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<key>`.

Property (attribute) metadata `<key>: <value>` pairs (e.g. `{"is-replication-key": true}`) are nested under top-level entity identifiers and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/reference/command-line-interface#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/reference/command-line-interface#select).

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3-8}
extractors:
- name: tap-postgres
  metadata:
    some_stream_id:
      replication-method: INCREMENTAL
      replication-key: created_at
      created_at:
        is-replication-key: true
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <extractor> set _metadata <entity> <key> <value>
meltano config <extractor> set _metadata <entity> <attribute> <key> <value>

export <EXTRACTOR>__METADATA='{"<entity>": {"<key>": "<value>", "<attribute>": {"<key>": "<value>"}}}'

# Once metadata has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <EXTRACTOR>__METADATA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_stream_id replication-method INCREMENTAL
meltano config tap-postgres set _metadata some_stream_id replication-key created_at
meltano config tap-postgres set _metadata some_stream_id created_at is-replication-key true

export TAP_POSTGRES__METADATA_SOME_STREAM_ID_REPLICATION_METHOD=FULL_TABLE
```

#### `schema` extra

- Setting: `_schema`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__SCHEMA`, e.g. `TAP_GITLAB__SCHEMA`
- Default: `{}` (an empty object)

An extractor's `schema` [extra](/guide/configuration#plugin-extras) holds an object describing
[Singer stream schema](https://hub.meltano.com/singer/spec#schemas) override
rules that are applied to the extractor's [discovered catalog file](https://hub.meltano.com/singer/spec#catalog-files)
when the extractor is run using [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

[JSON Schema](https://json-schema.org/) descriptions for specific properties (attributes) (e.g. `{"type": ["string", "null"], "format": "date-time"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values, and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/reference/command-line-interface#nested-properties) can also be thought of and interacted with as settings named `_schema.<entity>.<attribute>` and `_schema.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/reference/command-line-interface#select).

If a schema is specified for a property that does not yet exist in the discovered stream's schema, the property (and its schema) will be added to the catalog.
This allows you to define a full schema for taps such as [`tap-dynamodb`](https://github.com/singer-io/tap-dynamodb) that do not themselves have the ability to discover the schema of their streams.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3-7}
extractors:
- name: tap-postgres
  schema:
    some_stream_id:
      created_at:
        type: ["string", "null"]
        format: date-time
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <extractor> set _schema <entity> <attribute> <schema description>
meltano config <extractor> set _schema <entity> <attribute> <key> <value>

export <EXTRACTOR>__SCHEMA='{"<entity>": {"<attribute>": {"<key>": "<value>"}}}'

# Once schema descriptions have been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export <EXTRACTOR>__SCHEMA_<ENTITY>_<ATTRIBUTE>_<KEY>=<value>

# For example:
meltano config tap-postgres set _metadata some_stream_id created_at type '["string", "null"]'
meltano config tap-postgres set _metadata some_stream_id created_at format date-time

export TAP_POSTGRES__SCHEMA_SOME_STREAM_ID_CREATED_AT_FORMAT=date
```

#### `select` extra

- Setting: `_select`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__SELECT`, e.g. `TAP_GITLAB__SELECT`
- Default: `["*.*"]`

An extractor's `select` [extra](/guide/configuration#plugin-extras) holds an array of [entity selection rules](/reference/command-line-interface#select)
that are applied to the extractor's [discovered catalog file](https://hub.meltano.com/singer/spec#catalog-files)
when the extractor is run using [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

A selection rule is comprised of an entity identifier that corresponds to a Singer stream's `tap_stream_id` value, and an attribute identifier that that corresponds to a Singer stream property name, separated by a period (`.`). Rules indicating that an entity or attribute should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/reference/command-line-interface#select).

While this extra can be managed using [`meltano config`](/reference/command-line-interface#config) or environment variables like any other setting,
selection rules are typically specified using [`meltano select`](/reference/command-line-interface#select).

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3-5}
extractors:
- name: tap-gitlab
  select:
  - project_members.*
  - commits.*
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

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

#### <a name="select-filter-extra"></a>`select_filter` extra

- Setting: `_select_filter`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__SELECT_FILTER`, e.g. `TAP_GITLAB__SELECT_FILTER`
- [`meltano elt`](/reference/command-line-interface#elt) CLI options: `--select` and `--exclude`
- Default: `[]`

An extractor's `select_filter` [extra](/guide/configuration#plugin-extras) holds an array of [entity selection](#select-extra) filter rules
that are applied to the extractor's [discovered](/guide/integration#extractor-catalog-generation) or [provided](#catalog-extra) catalog file
when the extractor is run using [`meltano elt`](/reference/command-line-interface#elt) or [`meltano invoke`](/reference/command-line-interface#invoke),
after [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules are applied.

It can be used to only extract records for specific matching entities, or to extract records for all entities _except_ for those specified, by letting you apply filters on top of configured [entity selection rules](#select-extra).

Selection filter rules use entity identifiers that correspond to Singer stream `tap_stream_id` values. Rules indicating that an entity should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used in entity identifiers to match multiple entities at once.

Entity names can be discovered using [`meltano select --list --all <plugin>`](/reference/command-line-interface#select).

While this extra can be managed using [`meltano config`](/reference/command-line-interface#config) or environment variables like any other setting,
selection filers are typically specified using [`meltano elt`](/reference/command-line-interface#elt)'s `--select` and `--exclude` options.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{6-7}
extractors:
- name: tap-gitlab
  select:
  - project_members.*
  - commits.*
  select_filter:
  - commits
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

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

#### `state` extra

- Setting: `_state`
- [Environment variable](/guide/configuration#configuring-settings): `<EXTRACTOR>__STATE`, e.g. `TAP_GITLAB__STATE`
- [`meltano elt`](/reference/command-line-interface#elt) CLI option: `--state`
- Default: None

An extractor's `state` [extra](/guide/configuration#plugin-extras) holds a path to a [state file](https://hub.meltano.com/singer/spec#state-files) (relative to the [project directory](project)) to be provided to the extractor
when it is run as part of a pipeline using [`meltano elt`](/reference/command-line-interface#elt).

If a state path is not set, the state will be [looked up automatically](/guide/integration#incremental-replication-state) based on the ELT run's State ID.

While this extra can be managed using [`meltano config`](/reference/command-line-interface#config) or environment variables like any other setting,
a state file is typically provided using [`meltano elt`](/reference/command-line-interface#elt)'s `--state` option.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  state: extract/tap-gitlab.state.json
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <extractor> set _state <path>

export <EXTRACTOR>__STATE=<path>

meltano elt <extractor> <loader> --state <path>

# For example:
meltano config tap-gitlab set _state extract/tap-gitlab.state.json

export TAP_GITLAB__STATE=extract/tap-gitlab.state.json

meltano elt tap-gitlab target-jsonl --state extract/tap-gitlab.state.json
```

### Loaders

Loaders are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/reference/command-line-interface#elt) as part of [data integration](/guide/integration).
They are responsible for loading [extracted](#extractors) data into arbitrary data destinations: databases, SaaS APIs, or file formats.

Meltano supports [Singer targets](https://singer.io): executables that implement the [Singer specification](https://hub.meltano.com/singer/spec).

To learn which loaders are [discoverable](#discoverable-plugins) and supported out of the box, refer to the [Loaders page](https://hub.meltano.com/loaders/) or run [`meltano discover loaders`](/reference/command-line-interface#discover).

#### Extras

Loaders support the following [extras](/guide/configuration#plugin-extras):

- [`dialect`](#dialect-extra)
- [`target_schema`](#target-schema-extra)

#### `dialect` extra

- Setting: `_dialect`
- [Environment variable](/guide/configuration#configuring-settings): `<LOADER>__DIALECT`, e.g. `TARGET_POSTGRES__DIALECT`
- Default: `$MELTANO_LOADER_NAMESPACE`, which [will expand to](/guide/configuration#expansion-in-setting-values) the loader's `namespace`. Note that this default has been overridden on [discoverable](#discoverable-plugins) loaders, e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`.

A loader's `dialect` [extra](/guide/configuration#plugin-extras)
holds the name of the dialect of the target database, so that
[transformers](#transformers) in the same pipeline can determine the type of database to connect to.

The value of this extra [can be referenced](/guide/configuration#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_LOAD__DIALECT`
[pipeline environment variable](/guide/integration#pipeline-environment-variables).
It is used as the default value for `dbt`'s `target` setting, and should therefore correspond to a target name in `transform/profile/profiles.yml`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3}
loaders:
- name: target-example-db
  dialect: example-db
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <loader> set _dialect <dialect>

export <LOADER>__DIALECT=<dialect>

# For example:
meltano config target-example-db set _dialect example-db

export TARGET_EXAMPLE_DB__DIALECT=example-db
```

#### <a name="target-schema-extra"></a>`target_schema` extra

- Setting: `_target_schema`
- [Environment variable](/guide/configuration#configuring-settings): `<LOADER>__TARGET_SCHEMA`, e.g. `TARGET_POSTGRES__TARGET_SCHEMA`
- Default: `$MELTANO_LOAD_SCHEMA`, which [will expand to](/guide/configuration#expansion-in-setting-values) the value of the loader's `schema` setting

A loader's `target_schema` [extra](/guide/configuration#plugin-extras)
holds the name of the database schema the loader has been configured to load data into (assuming the destination supports schemas), so that
[transformers](#transformers) in the same pipeline can determine the database schema to load data from.

The value of this extra is usually not set explicitly, since its should correspond to the value of the loader's own "target schema" setting.
If the name of this setting is not `schema`, its value [can be referenced](/guide/configuration#expansion-in-setting-values) from the extra's value using `$MELTANO_LOAD_<TARGET_SCHEMA_SETTING>`, e.g. `$MELTANO_LOAD_DESTINATION_SCHEMA` for setting `destination_schema`.

The value of this extra [can be referenced](/guide/configuration#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_LOAD__TARGET_SCHEMA`
[pipeline environment variable](/guide/integration#pipeline-environment-variables).
It is used as the default value for `dbt`'s `source_schema` setting.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{5}
loaders:
- name: target-example-db
  settings:
  - name: destination_schema
  target_schema: $MELTANO_LOAD_DESTINATION_SCHEMA # Value of `destination_schema` setting
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <loader> set _target_schema <schema>

export <LOADER>__TARGET_SCHEMA=<schema>

# For example:
meltano config target-example-db set _target_schema '$MELTANO_LOAD_DESTINATION_SCHEMA'

# If the target schema cannot be determined dynamically using a setting reference:
meltano config target-example-db set _target_schema explicit_target_schema

export TARGET_EXAMPLE_DB__TARGET_SCHEMA=explicit_target_schema
```

### Transforms

Transforms are [dbt packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management) containing [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models),
that are used by [`meltano elt`](/reference/command-line-interface#elt) as part of [data transformation](/guide/transformation).

Together with the [dbt](https://www.getdbt.com) [transformer](#transformers), they are responsible for transforming data that has been loaded into a database (data warehouse) into a different format, usually one more appropriate for [analysis](/guide/analysis).

When a transform is added to your project using [`meltano add`](/reference/command-line-interface#add),
the [dbt package Git repository](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages) referenced by its `pip_url`
will be added to your project's `transform/packages.yml` and the package will be enabled in `transform/dbt_project.yml`.

#### Extras

Transforms support the following [extras](/guide/configuration#plugin-extras):

- [`package_name`](#package-name-extra)
- [`vars`](#vars-extra)

#### <a name="package-name-extra"></a>`package_name` extra

- Setting: `_package_name`
- [Environment variable](/guide/configuration#configuring-settings): `<TRANSFORM>__PACKAGE_NAME`, e.g. `TAP_GITLAB__PACKAGE_NAME`
- Default: `$MELTANO_TRANSFORM_NAMESPACE`, which [will expand to](/guide/configuration#expansion-in-setting-values) the transform's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

A transform's `package_name` [extra](/guide/configuration#plugin-extras)
holds the name of the dbt package's internal dbt project: the value of `name` in `dbt_project.yml`.

When a transform is added to your project using [`meltano add`](/reference/command-line-interface#add), this name will be added to the `models` dictionary in `transform/dbt_project.yml`.

The value of this extra [can be referenced](/guide/configuration#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_TRANSFORM__PACKAGE_NAME`
[pipeline environment variable](/guide/integration#pipeline-environment-variables).
It is included in the default value for `dbt`'s `models` setting: `$MELTANO_TRANSFORM__PACKAGE_NAME $MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{4}
transforms:
- name: dbt-facebook-ads
  namespace: tap_facebook
  package_name: facebook_ads
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <transform> set _package_name <name>

export <TRANSFORM>__PACKAGE_NAME=<name>

# For example:
meltano config dbt-facebook-ads set _package_name facebook_ads

export DBT_FACEBOOK_ADS__PACKGE_NAME=facebook_ads
```

#### `vars` extra

- Setting: `_vars`
- [Environment variable](/guide/configuration#configuring-settings): `<TRANSFORM>__VARS`, e.g. `TAP_GITLAB__VARS`
- Default: `{}` (an empty object)

A transform's `vars` [extra](/guide/configuration#plugin-extras) holds an object representing [dbt model variables](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-variables)
that can be referenced from a model using the [`var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/var).

When a transform is added to your project using [`meltano add`](/reference/command-line-interface#add), this object will be used as the dbt model's `vars` object in `transform/dbt_project.yml`.

Because these variables are handled by dbt rather than Meltano, [environment variables](/guide/configuration#expansion-in-setting-values) can be referenced using the [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) instead of `$VAR` or `${VAR}`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml
{% raw %}
transforms:
- name: tap-gitlab
  vars:
    schema: '{{ env_var(''DBT_SOURCE_SCHEMA'') }}'
{% endraw %}
```

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
{% raw %}
meltano config <transform> set _vars <key> <value>

export <TRANSFORM>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'
{% endraw %}
```
### Orchestrators

Orchestrators are [pip packages](https://pip.pypa.io/en/stable/) responsible for [orchestrating](/guide/orchestration) a project's [scheduled pipelines](/reference/command-line-interface#schedule).

Meltano supports [Apache Airflow](https://airflow.apache.org/) out of the box, but can be used with any tool capable of reading the output of [`meltano schedule list --format=json`](/reference/command-line-interface#schedule) and executing each pipeline's [`meltano elt`](/reference/command-line-interface#elt) command on a schedule.

When the `airflow` orchestrator is added to your project using [`meltano add`](/reference/command-line-interface#add),
its related [file bundle](#file-bundles) will automatically be added as well.

### Transformers

Transformers are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/reference/command-line-interface#elt) as part of [data transformation](/guide/transformation).
They are responsible for running [transforms](#transforms).

Meltano supports [dbt](https://www.getdbt.com) and its [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) out of the box.

When the `dbt` transformer is added to your project using [`meltano add`](/reference/command-line-interface#add),
its related [file bundle](#file-bundles) will automatically be added as well.

### File bundles

File bundles are [pip packages](https://pip.pypa.io/en/stable/) bundling files you may want in your project.

When a file bundle is added to your project using [`meltano add`](/reference/command-line-interface#add),
the bundled files will automatically be added as well.
The file bundle itself will not be added to your [`meltano.yml` project file](project#meltano-yml-project-file) unless it contains files that are
[managed by the file bundle](#update-extra) and to be updated automatically when [`meltano upgrade`](/reference/command-line-interface#upgrade) is run.

#### `update` extra

- Setting: `_update`
- [Environment variable](/guide/configuration#configuring-settings): `<BUNDLE>__UPDATE`, e.g. `DBT__UPDATE`
- Default: `{}` (an empty object)

A file bundle's `update` [extra](/guide/configuration#plugin-extras) holds an object mapping file paths (of files inside the bundle, relative to the project root) to booleans. [Glob](https://en.wikipedia.org/wiki/Glob_(programming)) patterns are supported to allow matching of multiple files with a single path.

When a file path's value is `True`, the matching files are considered to be managed by the file bundle and updated automatically when [`meltano upgrade`](/reference/command-line-interface#upgrade) is run.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](project#meltano-yml-project-file):

```yaml{3-4}
files:
- name: dbt
  update:
    transform/dbt_project.yml: false
    profiles/*.yml: true
```

<div class="notification is-info">
  <p>If a file path starts with a <code>*</code>, it must be wrapped in quotes to be considered valid YAML. For example, using <code>*.yml</code> to match all <code>.yml</code> files:</p>
<pre>
files:
- name: dbt
  update:
    '*.yml': true
</pre>
</div>

Alternatively, manage this extra using [`meltano config`](/reference/command-line-interface#config) or an [environment variable](/guide/configuration#configuring-settings):

```bash
meltano config <bundle> set _update <path> <true/false>

export <BUNDLE>__UPDATE='{"<path>": <true/false>}'

# For example:
meltano config --plugin-type=files dbt set _update transform/dbt_project.yml false
meltano config --plugin-type=files dbt set _update profiles/*.yml true

export DBT__UPDATE='{"transform/dbt_project.yml": false, "profiles/*.yml": true}'
```

### Utilities

If none of the other plugin types address your needs, any [pip package](https://pip.pypa.io/en/stable/) that exposes an executable can be added to your project as a utility.
Meltano has a selection of available utilities listed on [MeltanoHub](https://hub.meltano.com/utilities), or you can easily add your own custom utility.

#### Custom Utilities

Any [pip package](https://pip.pypa.io/en/stable/) that exposes an executable can be added to your project as a custom utility.

```bash
meltano add --custom utility <plugin>

# For example:
meltano add --custom utility yoyo
(namespace): yoyo
(pip_url): yoyo-migrations
(executable): yoyo
```

You can then invoke the executable using [`meltano invoke`](/reference/command-line-interface#invoke):

```bash
meltano invoke <plugin> [<executable arguments>...]

# For example:
meltano invoke yoyo new ./migrations -m "Add column to foo"
```

The benefit of doing this as opposed to adding the package to `requirements.txt` or running `pip install <package>` directly is that any packages installed this way benefit from Meltano's [virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) isolation.
This avoids dependency conflicts between packages.

### Mappers

Mappers allow you to transform or manipulate data after extraction and before loading. Common applications include:

- Streams/properties can be aliased to provide custom naming downstream.
- Stream records can be filtered based on any user-defined logic.
- Properties can be transformed inline (i.e. converting types, sanitizing PII data).
- Properties can be removed from the stream.
- New properties can be added to the stream.

Note that mappers are currently only available when using [`meltano run`](/reference/command-line-interface#run).

##### How to use

You can install mappers like any other other plugin using [`meltano add`](/reference/command-line-interface#add):

```bash

$ meltano discover mappers
Mappers
transform-field
meltano-map-transformer

$ meltano add mapper transform-field
Installing mapper 'transform-field'...
Installed mapper 'transform-field'

To learn more about mapper 'transform-field', visit https://github.com/transferwise/pipelinewise-transform-field
```

Mappers are unique in that after install you don't invoke them directly. Instead you define `mappings` by name and add a config object for each mapping.
This config object is passed to the mapper when the **mapping name** is called as part of a [`meltano run`](/reference/command-line-interface#run) invocation.
Note that this differs from other plugins, as you're not invoking a plugin name - but referencing the mapping name instead.
Additionally, the requirements for the config object itself will vary by plugin.

So given a mapper with mappings configured like so:

```yaml
mappers:
  - name: transform-field
    variant: transferwise
    pip_url: pipelinewise-transform-field
    executable: transform-field
    mappings:
    - name: hide-gitlab-secrets
      config:
        transformations:
          - field_id: "author_email"
            tap_stream_name: "commits"
            type: "MASK-HIDDEN"
          - field_id: "committer_email"
            tap_stream_name: "commits"
            type: "MASK-HIDDEN"
    - name: null-created-at
      config:
        transformations:
          - field_id: "created_at"
            tap_stream_name: "accounts"
            type: "SET-NULL"
```

You can then invoke the mappings by name:

```bash

# hide-gitlab-secrets will resolve to mapping with the same name. In this case, that mapping will perform two actions.
# Transform the "author_email" field in the "commits" stream and hide the email address.
# Transform the "committer_email" field in the "commits" stream and hide the email address.
$ meltano run tap-gitlab hide-gitlab-secrets target-jsonl

# null-created-at will resolve to mapping with the same name. In this case, that mapping will perform one action.
# Transform the "created_at" field in the "accounts" stream and set it to null.
$ meltano run tap-someapi null-created-at target-jsonl
```

You can also invoke multiple mappings at once in series:

```bash
$ tap-someapi fix-null-id fix-country-code target-jsonl
```

Each mapping will execute in a unique process instance of the mapper plugin. That means that you can also
call mappings that leverage the same plugin at multiple locations numerous times within the run invocation:

```bash

# Fix any null country codes using transform-field mapper.
# Set the customers region based on their country code using your own mapper.
# Mask the id if the customer is in the EU region using transform-field mapper.
$ tap-someapi fix-null-country set-region-from-country  mask-id-if-eu target-jsonl
```
