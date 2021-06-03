---
description: Learn how to extract and load data using Meltano and Singer taps and targets
---

# Data Integration (EL)

Meltano lets you easily extract and load data from and to databases, SaaS APIs, and file formats
using [Singer](https://www.singer.io/) [taps](https://www.singer.io/#taps) and [targets](https://www.singer.io/#targets),
which take the role of [your project](/docs/project.html)'s [extractors](/docs/plugins.html#extractors) and [loaders](/docs/plugins.html#loaders).

Meltano [manages your tap and target configuration](#plugin-configuration) for you,
makes it easy to [select which entities and attributes to extract](#selecting-entities-and-attributes-for-extraction),
and keeps track of [the incremental replication state](#incremental-replication-state),
so that subsequent pipeline runs with the same job ID will always pick up right where
the previous run left off.

You can run EL(T) pipelines using [`meltano elt`](/docs/command-line-interface.html#elt).
If you encounter some trouble running a pipeline, read our [troubleshooting tips](#troubleshooting) for some errors commonly seen.

## Plugin configuration

As described in the [Configuration guide](/docs/configuration.html#configuration-layers), [`meltano elt`](/docs/command-line-interface.html#elt) will determine the configuration of the extractor, loader, and (optionally) transformer by looking in [**the environment**](/docs/configuration.html#configuring-settings), your project's [**`.env` file**](/docs/project.html#env), the [system database](/docs/project.html#system-database), and finally your [**`meltano.yml` project file**](/docs/project.html#meltano-yml-project-file), falling back to a default value if nothing was found.

You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list all available settings with their names, environment variables, and current values. [`meltano config <plugin>`](/docs/command-line-interface.html#config) will print the current configuration in JSON format.

### Pipeline-specific configuration

If you'd like to specify (or override) the values of certain settings at runtime, on a per-pipeline basis, you can set them in the [`meltano elt`](/docs/command-line-interface.html#elt) execution environment using [environment variables](/docs/configuration.html#configuring-settings).

This lets you use the same extractors and loaders (Singer taps and targets) in multiple pipelines, configured differently each time, as an alternative to creating [multiple configurations](/docs/configuration.html#multiple-plugin-configurations) using [plugin inheritance](/docs/plugins.html#plugin-inheritance).

On a shell, you can explicitly `export` environment variables, that will be passed along to every following command invocation, or you can specify them in-line with a specific invocation, ahead of the command:

```bash
export TAP_FOO_BAR=bar
export TAP_FOO_BAZ=baz
meltano elt ...

TAP_FOO_BAR=bar TAP_FOO_BAZ=baz meltano elt ...
```

To verify that these environment variables will be picked up by Meltano as you intended, you can test them with [`meltano config <plugin>`](/docs/command-line-interface.html#config) before running `meltano elt`.

If you're using [`meltano schedule`](/docs/command-line-interface.html#schedule) to [schedule your pipelines](/#orchestration), you can specify environment variables for each pipeline in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file), where each entry in the `schedules` array can have an `env` dictionary:

```yaml{7-9}
schedules:
- name: foo-to-bar
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: '@hourly'
  env:
    TAP_FOO_BAR: bar
    TAP_FOO_BAZ: baz
```

Different runners and execution/orchestration platforms will have their own way of specifying environment variables along with a command invocation.

Airflow's [`BashOperator`](https://airflow.apache.org/docs/apache-airflow/1.10.14/howto/operator/bash.html), for example, supports an `env` parameter:

```python
BashOperator(
    # ...
    bash_command="meltano elt ...",
    env={
        "TAP_FOO_BAR": "bar",
        "TAP_FOO_BAZ": "baz",
    },
)
```

### Pipeline environment variables

To allow [loaders](/docs/plugins.html#loaders) and [transformers](/docs/plugins.html#transformers) to adapt their configuration and behavior based on the extractor and loader they are run with,
[`meltano elt`](/docs/command-line-interface.html#elt) dynamically sets a number of pipeline-specific [environment variables](/docs/configuration.html#environment-variables) before [compiling their configuration](/docs/configuration.html#expansion-in-setting-values) and [invoking their executables](/docs/configuration.html#accessing-from-plugins).

#### Extractor variables

In addition to [variables available to all plugins](/docs/configuration.html#available-environment-variables), the following variables describing the [extractor](/docs/plugins.html#extractors) are available to loaders _and_ transformers:

- `MELTANO_EXTRACTOR_NAME`: the extractor's `name`, e.g. `tap-gitlab`
- `MELTANO_EXTRACTOR_NAMESPACE`: the extractor's `namespace`, e.g. `tap_gitlab`
- `MELTANO_EXTRACT_<SETTING_NAME>`: one environment variable for each of the extractor's settings and [extras](/docs/configuration.html#plugin-extras), e.g. `MELTANO_EXTRACT_PRIVATE_TOKEN` for the `private_token` setting, and `MELTANO_EXTRACT__LOAD_SCHEMA` for the [`load_schema` extra](/docs/plugins.html#load-schema-extra)
- `<SETTING_ENV>`: all of the extractor's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `TAP_GITLAB_API_URL` for the `api_url` setting

#### Loader variables

Additionally, the following variables describing the [loader](/docs/plugins.html#loaders) are available to transformers:

- `MELTANO_LOADER_NAME`: the loader's `name`, e.g. `target-postgres`
- `MELTANO_LOADER_NAMESPACE`: the loader's `namespace`, e.g. `postgres`
- `MELTANO_LOAD_<SETTING_NAME>`: one environment variable for each of the loader's settings and [extras](/docs/configuration.html#plugin-extras), e.g. `MELTANO_LOAD_SCHEMA` for the `schema` setting, and `MELTANO_LOAD__DIALECT` for the [`dialect` extra](/docs/plugins.html#dialect-extra)
- `<SETTING_ENV>`: all of the loader's regular configuration environment variables, as listed by `meltano config <plugin> list`, e.g. `PG_ADDRESS` for the `host` setting

#### Transform variables

Additionally, the following variables describing the [transform](/docs/plugins.html#transforms) are available to transformers:

- `MELTANO_TRANSFORM_NAME`: the loader's `name`, e.g. `tap-gitlab`
- `MELTANO_TRANSFORM_NAMESPACE`: the loader's `namespace`, e.g. `tap_gitlab`
- `MELTANO_TRANSFORM_<SETTING_NAME>`: one environment variable for each of the transform's settings and [extras](/docs/configuration.html#plugin-extras), e.g. `MELTANO_TRANSFORM__PACKAGE_NAME` for the [`package_name` extra](/docs/plugins.html#package-name-extra)

#### How to use

Inside your loader or transformer's `config` object in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file), you can reference these (and other) environment variables as `$VAR` (as a single word) or `${VAR}` (inside a word). Inside your plugin, you can reference them through `os.environ` as usual (assuming you're using Python).

This feature is used to dynamically configure the `target-postgres` and `target-snowflake` loaders and `dbt` transformer as appropriate, independent of the specific extractor and loader used:
- Default value for the `target-postgres` and `target-snowflake` `schema` settings:
  - [`$MELTANO_EXTRACT__LOAD_SCHEMA`](/docs/plugins.html#load-schema-extra), e.g. `tap_gitlab` for `tap-gitlab`
- Default value for `dbt`'s `target` setting:
  - [`$MELTANO_LOAD__DIALECT`](/docs/plugins.html#dialect-extra), e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`, which correspond to the target names in `transform/profile/profiles.yml`
- Default value for `dbt`'s `source_schema` setting:
  - [`$MELTANO_LOAD__TARGET_SCHEMA`](/docs/plugins.html#target-schema-extra), the value of the `schema` setting for `target-postgres` and `target-snowflake`
- Default value for `dbt`'s `models` setting:
  - [`$MELTANO_TRANSFORM__PACKAGE_NAME`](/docs/plugins.html#package-name-extra)`$MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`, e.g. `tap_gitlab tap_gitlab my_meltano_model` for the `tap-gitlab` transform and `tap-gitlab` extractor

## Extractor catalog generation

Many extractors (Singer taps) expect to be provided a [catalog](/docs/singer-spec.html#catalog-files)
when they are run in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md) using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).
This catalog is a JSON file describing the [schemas](/docs/singer-spec.html#schemas) of the available entities (streams, tables) and attributes (properties, columns),
along with [metadata](/docs/singer-spec.html#metadata) to indicate (among other things) which entities and attributes should (or should not) be extracted.

A catalog can be generated by running the extractor in [discovery mode](/docs/singer-spec.html#discovery-mode)
and making the desired modifications to the schemas and metadata for the discovered entities and attributes.
Because these catalog files can be very large and can get outdated as data sources evolve, this process can be tedious and error-prone.

To save you a headache, Meltano can handle catalog generation for you, by letting you describe your desired modifications using
[entity selection](#selecting-entities-and-attributes-for-extraction), [metadata](#setting-metadata), and [schema](#overriding-schemas) rules that can be configured like any other setting,
and are applied to the discovered catalog on the fly when the extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt) or [`meltano invoke`](/docs/command-line-interface.html#invoke).

If you'd like to manually inspect the generated catalog for debugging purposes, you can dump it to [STDOUT](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) or a file using the `--dump=catalog` option on [`meltano invoke`](/docs/command-line-interface.html#invoke) or [`meltano elt`](/docs/command-line-interface.html#elt).

Note that if you've already manually discovered a catalog and modified it to your liking, it can be provided explicitly using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--catalog` option or the [`catalog` extractor extra](/docs/plugins.html#catalog-extra).

### Selecting entities and attributes for extraction

Extractors are often capable of extracting many more entities and attributes than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and attributes you actually plan on using.

Meltano makes it easy to select specific entities and attributes for inclusion or exclusion using [`meltano select`](/docs/command-line-interface.html#select)
and the [`select` extractor extra](/docs/plugins.html#select-extra),
which let you specify inclusion and exclusion rules that can contain [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) to match multiple entities and/or attributes at once.

Note that exclusion takes precedence over inclusion: if an entity or attribute is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and attributes are selected.

### Setting metadata

Additional [Singer stream and property metadata](/docs/singer-spec.html#metadata)
(like `replication-method` and `replication-key`) can be specified
using the [`metadata` extractor extra](/docs/plugins.html#metadata-extra),
which can be treated like a `_metadata` setting with
[nested properties](/docs/command-line-interface.html#nested-properties)
`_metadata.<entity>.<key>` and `_metadata.<entity>.<attribute>.<key>`.

### Overriding schemas

Similarly, a [`schema` extractor extra](/docs/plugins.html#schema-extra) is available that lets you easily override
[Singer stream schema](/docs/singer-spec.html#schemas) descriptions.
Here too, [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used to match multiple entities and/or attributes at once.

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

Most extractors (Singer taps) generate [state](/docs/singer-spec.html#state) when they are run, that can be passed along with a subsequent invocation to have the extractor pick up where it left off the previous time.

Loaders (Singer targets) take in data and state messages from extractors and are responsible for forwarding the extractor state to Meltano once the associated data has been successfully persisted in the destination.

Meltano stores this pipeline state in its [system database](/docs/project.html#system-database), identified by the [`meltano elt`](/docs/command-line-interface.html#elt) run's Job ID.

When `meltano elt` is run a subsequent time, it will look for the most recent completed (successful or failed) pipeline run with the same job ID that generated some state. If found, this state is then passed along to the extractor.

Note that if you already have a state file you'd like to use, it can be provided explicitly using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--state` option or the [`state` extractor extra](/docs/plugins.html#state-extra).

If you'd like to manually inspect a pipeline's state for debugging purposes, or so that you can store it somewhere other than the system database and explicitly pass it along to the next invocation, you can dump it to [STDOUT](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) or a file using [`meltano elt`](/docs/command-line-interface.html#elt)'s `--dump=state` option.

::: tip Not seeing state picked up after a failed run?

Some loaders only emit state once their work is completely done, even if some data may have been persisted already, and if earlier state messages from the extractor could have been forwarded to Meltano. When a pipeline with such a loader fails or is otherwise interrupted, no state will have been emitted yet, and a subsequent ELT run will not be able to pick up where this run actually left off.

:::

## Troubleshooting

### Debug Mode

If you're running into some trouble running a pipeline, the first recommendation is to run the same command in [debug mode](/docs/command-line-interface.html#debugging) so more information is shared on the command line.

```bash
meltano --log-level=debug elt ...
```

The output from debug mode will often be the first thing requested if you're asking for help via the <SlackChannelLink>Meltano Slack group</SlackChannelLink>.

### Isolate the Connector

If it's unclear which part of the pipeline is generating the problem, test the tap and target individually by using `meltano invoke`. The [`invoke` command](/docs/command-line-interface.html#invoke) will run the executable with any specified arguments.

```bash
meltano invoke <plugin> [PLUGIN_ARGS...]
```

This command can also be run in debug mode for additional information.

### Validate Tap Capabilities

In prior versions of the Singer spec, the `properties` capability was used instead of `catalog` for the [catalog files](https://hub.meltano.com/singer/spec#catalog-files). If this is the case for a tap, ensure `properties` is set as a [capability](/docs/contributor-guide.html#taps-targets-development) for the tap. Then `meltano elt` will accept the catalog file, either in the [`catalog` extra](/docs/plugins.html#catalog-extra) or via [`--catalog` on the command line]((/docs/command-line-interface.html#elt)), and will pass it to the tap using the appropriate flag.

### Incremental Replication Not Running as Expected

If you're trying to run a tap in incremental mode using `meltano elt` but it's running a full sync, ensure that you're passing a [Job ID]((/docs/getting-started.html#run-a-data-integration-el-pipeline)) via the [`--job-id` flag](/docs/command-line-interface.html#how-to-use-4).

### Testing Specific Failing Streams

When extracting several streams with a single tap, it may be challenging to debug a single failing stream. In this case, it can be useful to run the tap with just the single stream selected. 

Instead of duplicating the extractor in `meltano.yml`, try running `meltano elt` with the [`--select` flag](/docs/command-line-interface.html#parameters-2). This will run the pipeline with just that stream selected. 

You can also have `meltano invoke` select an individual stream by setting the [`select_filter` extra](/docs/plugins.html#select-filter-extra) as an environment variable:

```bash
export <TAP_NAME>__SELECT_FILTER='["<your_stream>"]'
```
