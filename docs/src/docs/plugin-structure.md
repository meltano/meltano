---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Plugin Structure

### Plugins

Your project's [plugins](/docs/plugin-structure.html#project-plugins),
typically [added to your project](/docs/plugin-management.html#adding-a-plugin-to-your-project)
using [`meltano add`](/docs/command-line-interface.html#add),
are defined under the `plugins` property, inside an array named after the [plugin type](/docs/plugin-structure.html#types) (e.g. `extractors`, `loaders`).

Every plugin in your project needs to have:
1. a `name` that's unique among plugins of the same type,
2. a [base plugin description](/docs/plugin-structure.html#project-plugins) describing the package in terms Meltano can understand, and
3. [configuration](/docs/configuration.html) that can be defined across [various layers](/docs/configuration.html#configuration-layers), including the definition's [`config` property](#plugin-configuration).

A base plugin description consists of the `pip_url`, `executable`, `capabilities`, and `settings` properties,
but not every plugin definition will specify these explicitly:

- An [**inheriting plugin definition**](#inheriting-plugin-definitions) has an **`inherit_from`** property and inherits its base plugin description from another plugin in your project or a [discoverable plugin](/docs/plugin-structure.html#discoverable-plugins) identified by name.
- A [**custom plugin definition**](#custom-plugin-definitions) has a **`namespace`** property instead and explicitly defines its base plugin description.
- A [**shadowing plugin definition**](#shadowing-plugin-definitions) has neither property and implicitly inherits its base plugin description from the [discoverable plugin](/docs/plugin-structure.html#discoverable-plugins) with the same **`name`**.

When inheriting a base plugin description, the plugin definition does not need to explicitly specify a `pip_url`
(the package's [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument),
but you may want to override the inherited value and set the property explicitly to [point at a (custom) fork](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin) or to [pin a package to a specific version](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin#pinning-a-plugin-to-a-specific-version).
When a plugin is added using `meltano add`, the `pip_url` is automatically repeated in the plugin definition for convenience.

#### Inheriting plugin definitions

A plugin defined with an `inherit_from` property inherits its [base plugin description](/docs/plugin-structure.html#project-plugins) from another plugin identified by name. To find the matching plugin, other plugins in your project are considered first, followed by
[discoverable plugins](/docs/plugin-structure.html#discoverable-plugins):

```yml{5,7}
plugins:
  extractors:
  - name: tap-postgres          # Shadows discoverable `tap-postgres` (see below)
  - name: tap-postgres--billing
    inherit_from: tap-postgres  # Inherits from project's `tap-postgres`
  - name: tap-bigquery--events
    inherit_from: tap-bigquery  # Inherits from discoverable `tap-bigquery`
```

When inheriting from another plugin in your project, its [configuration](/docs/configuration.html) is also inherited as if the values were defaults, which can then be overridden as appropriate:

```yml{10-12,15-18}
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: '2020-10-01T00:00:00Z'
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: '2020-12-01T00:00:00Z' # `start_date` is overridden
      view_id: 789012
```

Note that the presence of a [`variant` property](#variants) causes only discoverable plugins to be considered
(even if there is also a matching plugin in the project),
since only these can have multiple [variants](/docs/plugin-structure.html#variants):

```yml{6,8-9}
plugins:
  loaders:
  - name: target-snowflake          # Shadows discoverable `target-snowflake` (see below)
    variant: datamill-co            # using variant `datamill-co`
  - name: target-snowflake--derived
    inherit_from: target-snowflake  # Inherits from project's `target-snowflake`
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake  # Inherits from discoverable `target-snowflake`
    variant: transferwise           # using variant `transferwise`
```

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#plugin-inheritance).

#### Custom plugin definitions

A plugin defined with a `namespace` property (but no `inherit_from` property) is a [custom plugin](/docs/plugin-structure.html#custom-plugins) that explicitly defines its [base plugin description](/docs/plugin-structure.html#project-plugins):

```yaml{4-14}
plugins:
  extractors:
  - name: tap-covid-19
    namespace: tap_covid_19
    pip_url: tap-covid-19
    executable: tap-covid-19
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: api_token
    - name: user_agent
    - name: start_date
```

To learn how to add a custom plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).

#### Shadowing plugin definitions

A plugin defined without an `inherit_from` or `namespace` property implicitly inherits its [base plugin description](/docs/plugin-structure.html#project-plugins) from the [discoverable plugin](/docs/plugin-structure.html#discoverable-plugins) with the same `name`, as a form of [shadowing](https://en.wikipedia.org/wiki/Variable_shadowing):

```yaml{3}
plugins:
  extractors:
  - name: tap-gitlab
```

To learn how to add a discoverable plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#discoverable-plugins).

##### Variants

If multiple [variants](/docs/plugin-structure.html#variants) of a discoverable plugin are available,
the `variant` property can be used to choose a specific one:

```yaml{4}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
```

If no `variant` is specified, the _original_ variant supported by Meltano is used.
Note that this is not necessarily the _default_ variant that is recommended to new users and would be used if the plugin were newly added to the project.

#### Plugin configuration

A plugin's [configuration](/docs/configuration.html) is stored under a `config` property.
Values for [plugin extras](/docs/configuration.html#plugin-extras) are stored among the plugin's other properties, outside of the `config` object:

```yaml{3-7}
extractors:
- name: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

## Project plugins

In order to use a given package as a plugin in a [project](/docs/project.html),
assuming it meets the requirements of the [plugin type](#types) in question, Meltano needs to know:
1. where to find the package, typically a [pip package](https://pip.pypa.io/en/stable/) identified by its name on [PyPI](https://pypi.org/), public or private Git repository URL, or local directory path,
2. what [settings](/docs/configuration.html) and other capabilities it supports, and finally
3. what its [configuration](/docs/configuration.html) should be when invoked.

Together, a package's location (1) and the metadata (2) describing it in terms Meltano can understand make up the **base plugin description**.
In your project, **plugins** extend this description with a specific configuration (3) and a unique name.

This means that [different configurations](/docs/configuration.html#multiple-plugin-configurations) of the same package (base plugin)
would be represented in your project as separate plugins with their own unique names,
that can be thought of as differently initialized instances of the same class.
For example: extractors `tap-postgres--billing` and `tap-postgres--events` derived from base extractor [`tap-postgres`](/plugins/extractors/postgres.html),
or `tap-google-analytics--client-foo` and `tap-google-analytics--client-bar` derived from base extractor [`tap-google-analytics`](/plugins/extractors/google-analytics.html).

Each plugin in a project can either:
- inherit its base plugin description from a [discoverable plugin](#discoverable-plugins) that's supported out of the box,
- define its base plugin description explicitly, making it a [custom plugin](#custom-plugins), or
- [inherit](#plugin-inheritance) both base plugin description and configuration from another plugin in the project.

To learn how to add a plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#adding-a-plugin-to-your-project).

## Discoverable plugins

[Base plugin descriptions](#project-plugins) for many popular [extractors](#extractors) (Singer taps), [loaders](#loaders) (Singer targets),
and other plugins have already been collected by users and [contributed](/docs/contributor-guide.html#discoverable-plugins) to Meltano's index of discoverable plugins,
making them supported out of the box.

Discoverable plugins are defined in the `discovery.yml` manifest,
which can be found [in the Meltano repository](https://gitlab.com/meltano/meltano/-/blob/master/src/meltano/core/bundle/discovery.yml),
ships inside the [`meltano` package](https://pypi.org/project/meltano/),
and is available at <https://www.meltano.com/discovery.yml>.
If you'd like to use a different (custom) manifest in your project,
put a `discovery.yml` file at the root of your project,
or change the [`discovery_url` setting](/docs/settings.html#discovery-url).

To find discoverable plugins, run [`meltano discover`](/docs/command-line-interface.html#discover) or refer to the lists of [Sources](/plugins/extractors/) and [Destinations](/plugins/loaders/).

To learn how to add a discoverable plugin to your project using a [shadowing plugin definition](/docs/plugin-structure.html#shadowing-plugin-definitions) or [inheriting plugin definition](/docs/plugin-structure.html#inheriting-plugin-definitions), refer to the [Plugin Management guide](/docs/plugin-management.html#discoverable-plugins).

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

When multiple variants of a discoverable plugin are available, [`meltano discover`](/docs/command-line-interface.html#discover) will list their names alongside the plugin name.

To learn how to add a non-default variant of a discoverable plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#variants).

## Custom plugins

If you'd like to use a package in your project whose [base plugin description](#project-plugins) isn't [discoverable](#discoverable-plugins) yet,
you'll need to collect and provide this metadata yourself.

To learn how to add a custom plugin to your project using a [custom plugin definition](/docs/plugin-structure.html#custom-plugin-definitions), refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).

::: tip
Once you've got the plugin working in your project, please consider
[contributing its description](/docs/contributor-guide.html#discoverable-plugins)
to the [`discovery.yml` manifest](https://gitlab.com/meltano/meltano/-/blob/master/src/meltano/core/bundle/discovery.yml)
to make it discoverable and supported out of the box for new users!
:::

## Plugin inheritance

If you'd like to use the same package (base plugin) in your project multiple times with [different configurations](/docs/configuration.html#multiple-plugin-configurations),
you can add a new plugin that inherits from an existing one.

The new plugin will inherit its parent's [base plugin description](#project-plugins) and [configuration](/docs/configuration.html) as if they were defaults,
which can then be overridden as appropriate.

To learn how to add an inheriting plugin to your project using an [inheriting plugin definition](/docs/plugin-structure.html#inheriting-plugin-definitions), refer to the [Plugin Management guide](/docs/plugin-management.html#plugin-inheritance).

## Types

Meltano supports the following types of plugins:

- [**Extractors**](#extractors) pull data out of arbitrary data sources.
- [**Loaders**](#loaders) load extracted data into arbitrary data destinations.
- [**Transforms**](#transforms) transform data that has been loaded into a database (data warehouse).
- [**Models**](#models) describe the schema of the data being analyzed and the ways different tables can be joined.
- [**Dashboards**](#dashboards) bundle curated Meltano UI dashboards and reports.
- [**Orchestrators**](#orchestrators) orchestrate a project's scheduled pipelines.
- [**Transformers**](#transformers) run transforms.
- [**File bundles**](#file-bundles) bundle files you may want in your project.
- [**Utilities**](#utilities) perform arbitrary tasks provided by [pip packages](https://pip.pypa.io/en/stable/) with executables.

### Extractors

Extractors are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for pulling data out of arbitrary data sources: databases, SaaS APIs, or file formats.

Meltano supports [Singer taps](https://singer.io): executables that implement the [Singer specification](/docs/singer-spec.html).

To learn which extractors are [discoverable](#discoverable-plugins) and supported out of the box, refer to the [Sources page](/plugins/extractors/) or run [`meltano discover extractors`](/docs/command-line-interface.html#discover).

#### Extras

Extractors support the following [extras](/docs/configuration.html#plugin-extras):

- [`catalog`](#catalog-extra)
- [`load_schema`](#load-schema-extra)
- [`metadata`](#metadata-extra)
- [`schema`](#schema-extra)
- [`select`](#select-extra)
- [`select_filter`](#select-filter-extra)
- [`state`](#state-extra)

#### `catalog` extra

- Setting: `_catalog`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__CATALOG`, e.g. `TAP_GITLAB__CATALOG`
- [`meltano elt`](/docs/command-line-interface.html#elt) CLI option: `--catalog`
- Default: None

An extractor's `catalog` [extra](/docs/configuration.html#plugin-extras) holds a path to a [catalog file](/docs/singer-spec.html#catalog-files) (relative to the [project directory](/docs/project.html)) to be provided to the extractor
when it is run in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md) using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If a catalog path is not set, the catalog will be [generated on the fly](/docs/integration.html#extractor-catalog-generation)
by running the extractor in [discovery mode](/docs/singer-spec.html#discovery-mode) and applying the [schema](#schema-extra), [selection](#select-extra), and [metadata](#metadata-extra) rules to the discovered file.

[Selection filter rules](#select-filter-extra) are always applied to manually provided catalogs as well as discovered ones.

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
a catalog file is typically provided using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--catalog` option.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  catalog: extract/tap-gitlab.catalog.json
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <extractor> set _catalog <path>

export <EXTRACTOR>__CATALOG=<path>

meltano elt <extractor> <loader> --catalog <path>

# For example:
meltano config tap-gitlab set _catalog extract/tap-gitlab.catalog.json

export TAP_GITLAB__CATALOG=extract/tap-gitlab.catalog.json

meltano elt tap-gitlab target-jsonl --catalog extract/tap-gitlab.catalog.json
```

#### `load_schema` extra

- Setting: `_load_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__LOAD_SCHEMA`, e.g. `TAP_GITLAB__LOAD_SCHEMA`
- Default: `$MELTANO_EXTRACTOR_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the extractor's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

An extractor's `load_schema` [extra](/docs/configuration.html#plugin-extras)
holds the name of the database schema extracted data should be loaded into,
when this extractor is used in a pipeline with a [loader](#loaders) for a database that supports schemas, like [PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html) or [Snowflake](https://docs.snowflake.com/en/sql-reference/ddl-database.html).

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a loader's configuration using the `MELTANO_EXTRACT__LOAD_SCHEMA`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is used as the default value for the [`target-postgres`](/plugins/loaders/postgres.html) and [`target-snowflake`](/plugins/loaders/snowflake.html) `schema` settings.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  load_schema: gitlab_data
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <extractor> set _load_schema <schema>

export <EXTRACTOR>__LOAD_SCHEMA=<schema>

# For example:
meltano config tap-gitlab set _load_schema gitlab_data

export TAP_GITLAB__LOAD_SCHEMA=gitlab_data
```

#### `metadata` extra

- Setting: `_metadata`, alias: `metadata`
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__METADATA`, e.g. `TAP_GITLAB__METADATA`
- Default: `{}` (an empty object)

An extractor's `metadata` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream and property metadata](/docs/singer-spec.html#metadata)
rules that are applied to the extractor's [discovered catalog file](/docs/singer-spec.html#catalog-files)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

Stream (entity) metadata `<key>: <value>` pairs (e.g. `{"replication-method": "INCREMENTAL"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<key>`.

Property (attribute) metadata `<key>: <value>` pairs (e.g. `{"is-replication-key": true}`) are nested under top-level entity identifiers and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_metadata.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

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

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__SCHEMA`, e.g. `TAP_GITLAB__SCHEMA`
- Default: `{}` (an empty object)

An extractor's `schema` [extra](/docs/configuration.html#plugin-extras) holds an object describing
[Singer stream schema](/docs/singer-spec.html#schemas) override
rules that are applied to the extractor's [discovered catalog file](/docs/singer-spec.html#catalog-files)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

[JSON Schema](https://json-schema.org/) descriptions for specific properties (attributes) (e.g. `{"type": ["string", "null"], "format": "date-time"}`) are nested under top-level entity identifiers that correspond to Singer stream `tap_stream_id` values, and second-level attribute identifiers that correspond to Singer stream property names.
These [nested properties](/docs/command-line-interface.html#nested-properties) can also be thought of and interacted with as settings named `_schema.<entity>.<attribute>` and `_schema.<entity>.<attribute>.<key>`.

[Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

If a schema is specified for a property that does not yet exist in the discovered stream's schema, the property (and its schema) will be added to the catalog.
This allows you to define a full schema for taps such as [`tap-dynamodb`](https://github.com/singer-io/tap-dynamodb) that do not themselves have the ability to discover the schema of their streams.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3-7}
extractors:
- name: tap-postgres
  schema:
    some_stream_id:
      created_at:
        type: ["string", "null"]
        format: date-time
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__SELECT`, e.g. `TAP_GITLAB__SELECT`
- Default: `["*.*"]`

An extractor's `select` [extra](/docs/configuration.html#plugin-extras) holds an array of [entity selection rules](/docs/command-line-interface.html#select)
that are applied to the extractor's [discovered catalog file](/docs/singer-spec.html#catalog-files)
when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
These rules are not applied when a catalog is [provided manually](#catalog-extra).

A selection rule is comprised of an entity identifier that corresponds to a Singer stream's `tap_stream_id` value, and an attribute identifier that that corresponds to a Singer stream property name, separated by a period (`.`). Rules indicating that an entity or attribute should be excluded are prefixed with an exclamation mark (`!`). [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used in entity and attribute identifiers to match multiple entities and/or attributes at once.

Entity and attribute names can be discovered using [`meltano select --list --all <plugin>`](/docs/command-line-interface.html#select).

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
selection rules are typically specified using [`meltano select`](/docs/command-line-interface.html#select).

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3-5}
extractors:
- name: tap-gitlab
  select:
  - project_members.*
  - commits.*
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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

#### `select_filter` extra

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

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{6-7}
extractors:
- name: tap-gitlab
  select:
  - project_members.*
  - commits.*
  select_filter:
  - commits
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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
- [Environment variable](/docs/configuration.html#configuring-settings): `<EXTRACTOR>__STATE`, e.g. `TAP_GITLAB__STATE`
- [`meltano elt`](/docs/command-line-interface.html#elt) CLI option: `--state`
- Default: None

An extractor's `state` [extra](/docs/configuration.html#plugin-extras) holds a path to a [state file](/docs/singer-spec.html#state-files) (relative to the [project directory](/docs/project.html)) to be provided to the extractor
when it is run as part of a pipeline using [`meltano elt`](/docs/command-line-interface.html#elt).

If a state path is not set, the state will be [looked up automatically](/docs/integration.html#incremental-replication-state) based on the ELT run's Job ID.

While this extra can be managed using [`meltano config`](/docs/command-line-interface.html#config) or environment variables like any other setting,
a state file is typically provided using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--state` option.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3}
extractors:
- name: tap-gitlab
  state: extract/tap-gitlab.state.json
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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

Loaders are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data integration](/docs/integration.md).
They are responsible for loading [extracted](#extractors) data into arbitrary data destinations: databases, SaaS APIs, or file formats.

Meltano supports [Singer targets](https://singer.io): executables that implement the [Singer specification](/docs/singer-spec.html).

To learn which loaders are [discoverable](#discoverable-plugins) and supported out of the box, refer to the [Destinations page](/plugins/loaders/) or run [`meltano discover loaders`](/docs/command-line-interface.html#discover).

#### Extras

Loaders support the following [extras](/docs/configuration.html#plugin-extras):

- [`dialect`](#dialect-extra)
- [`target_schema`](#target-schema-extra)

#### `dialect` extra

- Setting: `_dialect`
- [Environment variable](/docs/configuration.html#configuring-settings): `<LOADER>__DIALECT`, e.g. `TARGET_POSTGRES__DIALECT`
- Default: `$MELTANO_LOADER_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the loader's `namespace`. Note that this default has been overridden on [discoverable](#discoverable-plugins) loaders, e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`.

A loader's `dialect` [extra](/docs/configuration.html#plugin-extras)
holds the name of the dialect of the target database, so that
[transformers](#transformers) in the same pipeline and [Meltano UI](/docs/ui.html)'s [Analysis feature](/docs/analysis.html)
can determine the type of database to connect to.

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_LOAD__DIALECT`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is used as the default value for `dbt`'s `target` setting, and should therefore correspond to a target name in `transform/profile/profiles.yml`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3}
loaders:
- name: target-example-db
  dialect: example-db
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <loader> set _dialect <dialect>

export <LOADER>__DIALECT=<dialect>

# For example:
meltano config target-example-db set _dialect example-db

export TARGET_EXAMPLE_DB__DIALECT=example-db
```

#### `target_schema` extra

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

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{5}
loaders:
- name: target-example-db
  settings:
  - name: destination_schema
  target_schema: $MELTANO_LOAD_DESTINATION_SCHEMA # Value of `destination_schema` setting
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

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
that are used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).

Together with the [dbt](https://www.getdbt.com) [transformer](#transformers), they are responsible for transforming data that has been loaded into a database (data warehouse) into a different format, usually one more appropriate for [analysis](/docs/analysis.html).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the [dbt package Git repository](https://docs.getdbt.com/docs/building-a-dbt-project/package-management#git-packages) referenced by its `pip_url`
will be added to your project's `transform/packages.yml` and the package will be enabled in `transform/dbt_project.yml`.

#### Extras

Transforms support the following [extras](/docs/configuration.html#plugin-extras):

- [`package_name`](#package-name-extra)
- [`vars`](#vars-extra)

#### `package_name` extra

- Setting: `_package_name`
- [Environment variable](/docs/configuration.html#configuring-settings): `<TRANSFORM>__PACKAGE_NAME`, e.g. `TAP_GITLAB__PACKAGE_NAME`
- Default: `$MELTANO_TRANSFORM_NAMESPACE`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the transform's `namespace`, e.g. `tap_gitlab` for `tap-gitlab`

A transform's `package_name` [extra](/docs/configuration.html#plugin-extras)
holds the name of the dbt package's internal dbt project: the value of `name` in `dbt_project.yml`.

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add), this name will be added to the `models` dictionary in `transform/dbt_project.yml`.

The value of this extra [can be referenced](/docs/configuration.html#expansion-in-setting-values) from a transformer's configuration using the `MELTANO_TRANSFORM__PACKAGE_NAME`
[pipeline environment variable](/docs/integration.html#pipeline-environment-variables).
It is included in the default value for `dbt`'s `models` setting: `$MELTANO_TRANSFORM__PACKAGE_NAME $MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{4}
transforms:
- name: dbt-facebook-ads
  namespace: tap_facebook
  package_name: facebook_ads
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <transform> set _package_name <name>

export <TRANSFORM>__PACKAGE_NAME=<name>

# For example:
meltano config dbt-facebook-ads set _package_name facebook_ads

export DBT_FACEBOOK_ADS__PACKGE_NAME=facebook_ads
```

#### `vars` extra

- Setting: `_vars`
- [Environment variable](/docs/configuration.html#configuring-settings): `<TRANSFORM>__VARS`, e.g. `TAP_GITLAB__VARS`
- Default: `{}` (an empty object)

A transform's `vars` [extra](/docs/configuration.html#plugin-extras) holds an object representing [dbt model variables](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-variables)
that can be referenced from a model using the [`var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/var).

When a transform is added to your project using [`meltano add`](/docs/command-line-interface.html#add), this object will be used as the dbt model's `vars` object in `transform/dbt_project.yml`.

Because these variables are handled by dbt rather than Meltano, [environment variables](/docs/configuration.html#expansion-in-setting-values) can be referenced using the [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) instead of `$VAR` or `${VAR}`.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3-4}
transforms:
- name: tap-gitlab
  vars:
    schema: '{{ env_var(''DBT_SOURCE_SCHEMA'') }}'
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <transform> set _vars <key> <value>

export <TRANSFORM>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'
```

### Models

Models are [pip packages](https://pip.pypa.io/en/stable/) used by [Meltano UI](/docs/ui.html) to aid in [data analysis](/docs/analysis.html).
They describe the schema of the data being analyzed and the ways different tables can be joined,
and are used to automatically generate SQL queries using a point-and-click interface.

### Dashboards

Dashboards are [pip packages](https://pip.pypa.io/en/stable/) bundling curated [Meltano UI](/docs/ui.html) dashboards and reports.

When a dashboard is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled dashboards and reports will automatically be added to your project's `analyze` directory as well.

### Orchestrators

Orchestrators are [pip packages](https://pip.pypa.io/en/stable/) responsible for [orchestrating](/docs/orchestration.html) a project's [scheduled pipelines](/docs/command-line-interface.html#schedule).

Meltano supports [Apache Airflow](https://airflow.apache.org/) out of the box, but can be used with any tool capable of reading the output of [`meltano schedule list --format=json`](/docs/command-line-interface.html#schedule) and executing each pipeline's [`meltano elt`](/docs/command-line-interface.html#elt) command on a schedule.

When the `airflow` orchestrator is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

### Transformers

Transformers are [pip packages](https://pip.pypa.io/en/stable/) used by [`meltano elt`](/docs/command-line-interface.html#elt) as part of [data transformation](/docs/transforms.md).
They are responsible for running [transforms](#transforms).

Meltano supports [dbt](https://www.getdbt.com) and its [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) out of the box.

When the `dbt` transformer is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
its related [file bundle](#file-bundles) will automatically be added as well.

### File bundles

File bundles are [pip packages](https://pip.pypa.io/en/stable/) bundling files you may want in your project.

When a file bundle is added to your project using [`meltano add`](/docs/command-line-interface.html#add),
the bundled files will automatically be added as well.
The file bundle itself will not be added to your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) unless it contains files that are
[managed by the file bundle](#update-extra) and to be updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run.

#### `update` extra

- Setting: `_update`
- [Environment variable](/docs/configuration.html#configuring-settings): `<BUNDLE>__UPDATE`, e.g. `DBT__UPDATE`
- Default: `{}` (an empty object)

A file bundle's `update` [extra](/docs/configuration.html#plugin-extras) holds an object mapping file paths (of files inside the bundle, relative to the project root) to booleans.

When a file path's value is `True`, the file is considered to be managed by the file bundle and updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run.

##### How to use

Manage this extra directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yaml{3-4}
files:
- name: dbt
  update:
    transform/dbt_project.yml: false
```

Alternatively, manage this extra using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config <bundle> set _update <path> <true/false>

export <BUNDLE>__UPDATE='{"<path>": <true/false>}'

# For example:
meltano config --plugin-type=files dbt set _update transform/dbt_project.yml false

export DBT__UPDATE='{"transform/dbt_project.yml": false}'
```

### Utilities

If none of the other plugin types address your needs, any [pip package](https://pip.pypa.io/en/stable/) that exposes an executable can be added to your project as a utility:

```bash
meltano add --custom utility <plugin>

# For example:
meltano add --custom utility yoyo
(namespace): yoyo
(pip_url): yoyo-migrations
(executable): yoyo
```

You can then invoke the executable using [`meltano invoke`](/docs/command-line-interface.html#invoke):

```bash
meltano invoke <plugin> [<executable arguments>...]

# For example:
meltano invoke yoyo new ./migrations -m "Add column to foo"
```

The benefit of doing this as opposed to adding the package to `requirements.txt` or running `pip install <package>` directly is that any packages installed this way benefit from Meltano's [virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) isolation.
This avoids dependency conflicts between packages.
