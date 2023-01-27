---
title: Replicate Data
description: Learn how to extract and load data using Meltano and Singer taps and targets
layout: doc
weight: 4
---

Meltano lets you easily extract and load data from and to databases, SaaS APIs, and file formats
using [Singer](https://www.singer.io/) [taps](https://www.singer.io/#taps) and [targets](https://www.singer.io/#targets),
which take the role of [your project](/concepts/project)'s [extractors](/concepts/plugins#extractors) and [loaders](/concepts/plugins#loaders).

Meltano [manages your tap and target configuration](#plugin-configuration) for you,
makes it easy to [select which entities and attributes to extract](#selecting-entities-and-attributes-for-extraction),
and keeps track of [the incremental replication state](#incremental-replication-state),
so that subsequent pipeline runs with the same state ID will always pick up right where
the previous run left off.

You can run EL(T) pipelines using [`meltano run`](/reference/command-line-interface#elt).
If you encounter some trouble running a pipeline, read our [troubleshooting tips](#troubleshooting) for some errors commonly seen.

## Plugin configuration

As described in the [Configuration guide](/guide/configuration#configuration-layers), [`meltano run`](/reference/command-line-interface#run) will determine the configuration of the extractor, loader, and (optionally) transformer by looking in [**the environment**](/guide/configuration#configuring-settings), your project's [**`.env` file**](/concepts/project#env), the [system database](/concepts/project#system-database), and finally your [**`meltano.yml` project file**](/concepts/project#meltano-yml-project-file), falling back to a default value if nothing was found.

You can use [`meltano config <plugin> list`](/reference/command-line-interface#config) to list all available settings with their names, environment variables, and current values. [`meltano config <plugin>`](/reference/command-line-interface#config) will print the current configuration in JSON format.

If supported by the plugin type, its configuration can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

#### Extractor variables

In addition to [variables available to all plugins](/guide/configuration#available-environment-variables), the following variables describing the [extractor](/concepts/plugins#extractors) are available to loaders _and_ transformers:

- `MELTANO_EXTRACTOR_NAME`: the extractor's `name`, e.g. `tap-gitlab`
- `MELTANO_EXTRACTOR_NAMESPACE`: the extractor's `namespace`, e.g. `tap_gitlab`
- `MELTANO_EXTRACT_<SETTING_NAME>`: one environment variable for each of the extractor's settings and [extras](/guide/configuration#plugin-extras), e.g. `MELTANO_EXTRACT_PRIVATE_TOKEN` for the `private_token` setting, and `MELTANO_EXTRACT__LOAD_SCHEMA` for the [`load_schema` extra](/concepts/plugins#load-schema-extra)
- `<SETTING_ENV>`: all of the extractor's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `TAP_GITLAB_API_URL` for the `api_url` setting

#### Loader variables

Additionally, the following variables describing the [loader](/concepts/plugins#loaders) are available to transformers:

- `MELTANO_LOADER_NAME`: the loader's `name`, e.g. `target-postgres`
- `MELTANO_LOADER_NAMESPACE`: the loader's `namespace`, e.g. `postgres`
- `MELTANO_LOAD_<SETTING_NAME>`: one environment variable for each of the loader's settings and [extras](/guide/configuration#plugin-extras), e.g. `MELTANO_LOAD_SCHEMA` for the `schema` setting, and `MELTANO_LOAD__DIALECT` for the [`dialect` extra](/concepts/plugins#dialect-extra)
- `<SETTING_ENV>`: all of the loader's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `TARGET_POSTGRES_HOST` for the `host` setting

#### Transform variables

Additionally, the following variables describing the [transform](/concepts/plugins#transforms) are available to transformers:

- `MELTANO_TRANSFORM_NAME`: the loader's `name`, e.g. `tap-gitlab`
- `MELTANO_TRANSFORM_NAMESPACE`: the loader's `namespace`, e.g. `tap_gitlab`
- `MELTANO_TRANSFORM_<SETTING_NAME>`: one environment variable for each of the transform's settings and [extras](/guide/configuration#plugin-extras), e.g. `MELTANO_TRANSFORM__PACKAGE_NAME` for the [`package_name` extra](/concepts/plugins#package-name-extra)

#### How to use

Inside your loader or transformer's `config` object in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file), you can reference these (and other) environment variables as `$VAR` (as a single word) or `${VAR}` (inside a word). Inside your plugin, you can reference them through `os.environ` as usual (assuming you're using Python).

This feature is used to dynamically configure the `target-postgres` and `target-snowflake` loaders and `dbt` transformer as appropriate, independent of the specific extractor and loader used:

- Default value for the `target-postgres` and `target-snowflake` `schema` settings:
  - [`$MELTANO_EXTRACT__LOAD_SCHEMA`](/concepts/plugins#load-schema-extra), e.g. `tap_gitlab` for `tap-gitlab`
- Default value for `dbt`'s `target` setting:
  - [`$MELTANO_LOAD__DIALECT`](/concepts/plugins#dialect-extra), e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`, which correspond to the target names in `transform/profile/profiles.yml`
- Default value for `dbt`'s `source_schema` setting:
  - [`$MELTANO_LOAD__TARGET_SCHEMA`](/concepts/plugins#target-schema-extra), the value of the `schema` setting for `target-postgres` and `target-snowflake`
- Default value for `dbt`'s `models` setting:
  - [`$MELTANO_TRANSFORM__PACKAGE_NAME`](/concepts/plugins#package-name-extra)`$MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`, e.g. `tap_gitlab tap_gitlab my_meltano_model` for the `tap-gitlab` transform and `tap-gitlab` extractor

### Selecting entities and attributes for extraction

Extractors are often capable of extracting many more entities and attributes than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and attributes you actually plan on using.

Meltano makes it easy to select specific entities and attributes for inclusion or exclusion using [`meltano select`](/reference/command-line-interface#select)
and the [`select` extractor extra](/concepts/plugins#select-extra),
which let you specify inclusion and exclusion rules that can contain [Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) to match multiple entities and/or attributes at once.

Note that exclusion takes precedence over inclusion: if an entity or attribute is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and attributes are selected.

### Setting metadata

Additional [Singer stream and property metadata](https://hub.meltano.com/singer/spec#metadata)
(like `replication-method` and `replication-key`) can be specified
using the [`metadata` extractor extra](/concepts/plugins#metadata-extra),
which can be treated like a `_metadata` setting with
[nested properties](/reference/command-line-interface#nested-properties)
`_metadata.<entity>.<key>` and `_metadata.<entity>.<attribute>.<key>`.

### Overriding schemas

Similarly, a [`schema` extractor extra](/concepts/plugins#schema-extra) is available that lets you easily override
[Singer stream schema](https://hub.meltano.com/singer/spec#schemas) descriptions.
Here too, [Unix shell-style wildcards](<https://en.wikipedia.org/wiki/Glob_(programming)#Syntax>) can be used to match multiple entities and/or attributes at once.

## Replication methods

Extractors can replicate data from a source using one of the following methods:

- [Log-based Incremental Replication](#log-based-incremental-replication)
- [Key-based Incremental Replication](#key-based-incremental-replication)
- [Full Table Replication](#full-table-replication)

Extractors for SaaS APIs typically hard-code the appropriate replication method for each supported entity.
Most database extractors, on the other hand, support two or more of these methods and require you to choose an appropriate option for each table through the `replication-method` [stream metadata](#setting-metadata) key.

To support incremental replication, where a data integration pipeline run picks up where the previous run left off, Meltano keeps track of [incremental replication state](#incremental-replication-state).

### Log-based Incremental Replication

- `replication-method` [stream metadata](#setting-metadata) value: `LOG_BASED`

The extractor uses the database's binary log files to identify what records were inserted, updated, and deleted from the table [since the last run (if any)](#incremental-replication-state), and extracts only these records.

This option is not supported by all databases and database extractors.

To learn more about how Log-based Incremental Replication works and its limitations, refer to the [Stitch Docs](https://www.stitchdata.com/docs/replication/replication-methods/log-based-incremental), which by and large also apply to Singer taps used with Meltano.

### Key-based Incremental Replication

- `replication-method` [stream metadata](#setting-metadata) value: `INCREMENTAL`

The extractor uses the value of a specific column on the table (the Replication Key, e.g. an `updated_at` timestamp or incrementing `id` integer) to identify what records were inserted or updated (but not deleted) [since the last run (if any)](#incremental-replication-state), and extracts only those records.

To learn more about how Key-based Incremental Replication works and its limitations, refer to the [Stitch Docs](https://www.stitchdata.com/docs/replication/replication-methods/key-based-incremental), which by and large also apply to Singer taps used with Meltano.

#### Replication Key

Replication Keys are columns that database extractors use to identify new and updated data for replication.

When you set a table to use Key-based Incremental Replication, you’ll also need to define a Replication Key for that table by setting the `replication-key` [stream metadata](#setting-metadata) key.

To learn more about replication keys, refer to the [Stitch Docs](https://www.stitchdata.com/docs/replication/replication-keys), which by and large also apply to Singer taps used with Meltano.

### Full Table Replication

- `replication-method` [stream metadata](#setting-metadata) value: `FULL_TABLE`

The extractor extracts all available records in the table on every run.

To learn more about how Full-Table Replication works and its limitations, refer to the [Stitch Docs](https://www.stitchdata.com/docs/replication/replication-methods/full-table), which by and large also apply to Singer taps used with Meltano.

## Incremental replication state

Most extractors (Singer taps) generate [state](https://hub.meltano.com/singer/spec#state) when they are run, that can be passed along with a subsequent invocation to have the extractor pick up where it left off the previous time (handled automatically for [`meltano run`](/reference/command-line-interface#run).

Loaders (Singer targets) take in data and state messages from extractors and are responsible for forwarding the extractor state to Meltano once the associated data has been successfully persisted in the destination.

Meltano stores this pipeline state in its [system database](/concepts/project#system-database), identified by the [`meltano run`](/reference/command-line-interface#run) State ID automatically generated based on the extractor name, loader name, and active environment name. For [`meltano run`](/reference/command-line-interface#elt) the State ID has to be created and set manually using the `--state-id` argument, make sure to use a unique string identifier for the pipeline always include it since it must be present in each execution in order for incremental replication to work.

If you'd like to manually inspect a job's state for debugging purposes, or so that you can store it somewhere other than the system database you can use the [`meltano state`](/reference/command-line-interface#state) command to do things like list all states, get state by name, set state, etc.


### Internal State Merge Logic

When running Extract and Load jobs via [`run`](/reference/command-line-interface#run) or [`elt`](/reference/command-line-interface#elt), Meltano will pull state from the system databse from the most recently completed job where the State ID with the same State ID that generated a state.
When a data replication job is executed via [`run`](/reference/command-line-interface#run) or [`elt`](/reference/command-line-interface#elt), Meltano with fetch state from the system database using the State ID as unique key.
If a state record from a completed job is found, its data is then passed along to the extractor.
If one or more partial state records are found, the partial data is merged with the last completed state, to produce an up-to-date state artifact which will be passed along to the extractor.
The same merge behavior is performed whenever a user runs [`meltano state get`](/reference/command-line-interface#state).
This command returns the merged result of the latest completed state plus any newer partial state records, if they exist.
This works as Singer Targets are expected to emit [STATE messages](https://hub.meltano.com/singer/spec#state-files) [only after persisting data for a given stream](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md).

Partial state records are generated when extractors fail before completion.
This can happen when a [`meltano run`](/reference/command-line-interface#run) execution is aborted before a particular stream completes.
Partial state records can also be inserted manually via [`meltano state merge'](/reference/command-line-interface#state).

Unlike [`meltano state merge`](/reference/command-line-interface#state),[`meltano state set`](/reference/command-line-interface#state) will insert a complete record, which causes meltano to ignore any previous state records, whether completed or partial.

<div class="notification is-info">
  <p><strong>Not seeing state picked up after a failed run?</strong></p>
  <p>Some loaders only emit state once their work is completely done, even if some data may have been persisted already, and if earlier state messages from the extractor could have been forwarded to Meltano. When a pipeline with such a loader fails or is otherwise interrupted, no state will have been emitted yet, and a subsequent ELT run will not be able to pick up where this run actually left off.</p>
</div>

## Troubleshooting

### Debug Mode

If you're running into some trouble running a pipeline, the first recommendation is to run the same command in [debug mode](/reference/command-line-interface#debugging) so more information is shared on the command line.

```bash
meltano --log-level=debug run ...
```

The output from debug mode will often be the first thing requested if you're asking for help via the <SlackChannelLink>Meltano Slack group</SlackChannelLink>.

### Isolate the Connector

If it's unclear which part of the pipeline is generating the problem, test the tap and target individually by using `meltano invoke`.
The [`invoke` command](/reference/command-line-interface#invoke) will run the executable with any specified arguments.

```bash
meltano invoke <plugin> [PLUGIN_ARGS...]
```

This command can also be run in debug mode for additional information.