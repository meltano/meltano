---
description: Learn how to extract and load data using Meltano and Singer taps and targets
---

# Data Integration (EL)

Meltano lets you easily extract and load data from and to databases, SaaS APIs, and file formats
using [Singer](https://www.singer.io/) [taps](https://www.singer.io/#taps) and [targets](https://www.singer.io/#targets),
which take the role of [your project](/docs/project.html)'s [extractors](/docs/plugins.html#extractors) and [loaders](/docs/plugins.html#loaders).

Meltano [manages your tap and target configuration](#plugin-configuration) for you,
makes it easy to [select which entities and attributes to extract](#selecting-entities-and-attributes-for-extraction),
and keeps track of [the state of your extraction](#pipeline-state),
so that subsequent pipeline runs with the same job ID will always pick up right where
the previous run left off.

You can run EL(T) pipelines using [`meltano elt`](/docs/command-line-interface.html#elt).

## Plugin configuration

As described in the [Configuration guide](/docs/configuration.html#configuration-layers), [`meltano elt`](/docs/command-line-interface.html#elt) will determine the configuration of the extractor, loader, and (optionally) transformer by looking in **the environment**, your project's [**`.env` file**](/docs/project.html#env), the [system database](/docs/project.html#system-database), and finally your [**`meltano.yml` project file**](/docs/project.html#meltano-yml-project-file), falling back to a default value if nothing was found.

You can use [`meltano config <plugin> list`](/docs/command-line-interface.html#config) to list all available settings with their names, environment variables, and current values. [`meltano config <plugin>`](/docs/command-line-interface.html#config) will print the current configuration in JSON format.

### Pipeline-specific configuration

If you'd like to specify (or override) the values of certain settings at runtime, on a per-pipeline basis, you can set them in the [`meltano elt`](/docs/command-line-interface.html#elt) execution environment using [environment variables](https://en.wikipedia.org/wiki/Environment_variable).

This lets you use the same extractors and loaders (Singer taps and targets) in multiple pipelines, configured differently each time.

On a shell, you can explicitly `export` environment variables, that will be passed along to every following command invocation, or you can specify them in-line with a specific invocation, ahead of the command:

```bash
export TAP_FOO_BAR=bar
export TAP_FOO_BAZ=baz
meltano elt ...

TAP_FOO_BAR=bar TAP_FOO_BAZ=baz meltano elt ...
```

To verify that these environment variables will be picked up by Meltano as you intented, you can test them with `meltano config <plugin>` before running `meltano elt`.

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

Airflow's [`BashOperator`](https://airflow.apache.org/docs/stable/_api/airflow/operators/bash_operator/index.html#airflow.operators.bash_operator.BashOperator), for example, supports an `env` parameter:

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
[`meltano elt`](/docs/command-line-interface.html#elt) dynamically sets a number of pipeline-specific environment variables before compiling their configuration and invoking their executables.

#### Extractor variables

In addition to variables [set through the environment](#pipeline-specific-configuration) or your project's [`.env` file](/docs/project.html#env), the following variables describing the [extractor](/docs/plugins.html#extractors) are available to loaders _and_ transformers:

- `MELTANO_EXTRACTOR_NAME`: the extractor's `name`, e.g. `tap-gitlab`
- `MELTANO_EXTRACTOR_NAMESPACE`: the extractor's `namespace`, e.g. `tap_gitlab`
- `MELTANO_EXTRACT_<SETTING_NAME>`: one environment variable for each of the extractor's settings and [extras](/docs/configuration.html#plugin-extras), e.g. `MELTANO_EXTRACT_PRIVATE_TOKEN` for the `private_token` setting, and `MELTANO_EXTRACT__PREFERRED_SCHEMA` for the [`preferred_schema` extra](/docs/plugins.html#preferred-schema-extra)
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

#### How to use

Inside your loader or transformer's `config` object in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file), you can reference these (and other) environment variables as `$VAR` (as a single word) or `${VAR}` (inside a word). Inside your plugin, you can reference these through `os.environ` (if using Python) as usual.

This feature is used to dynamically configure the `target-postgres` and `target-snowflake` loaders and `dbt` transformer as appropriate, independent of the specific extractor and loader used:
- Default value for the `target-postgres` and `target-snowflake` `schema` settings:
  - [`$MELTANO_EXTRACT__PREFERRED_SCHEMA`](/docs/plugins.html#preferred-schema-extra), e.g. `tap_gitlab` for `tap-gitlab`
- Default value for `dbt`'s `target` setting:
  - [`$MELTANO_LOAD__DIALECT`](/docs/plugins.html#dialect-extra), e.g. `postgres` for `target-postgres` and `snowflake` for `target-snowflake`, which correspond to the target names in `transform/profile/profiles.yml`
- `dbt` default value for `source_schema`: `$MELTANO_LOAD_SCHEMA`, e.g. `tap_gitlab`
- `dbt` default value for `models`: `$MELTANO_EXTRACTOR_NAMESPACE my_meltano_model`, e.g. `tap_gitlab my_meltano_model`

## Selecting entities and attributes for extraction

Extractors are often capable of extracting many more entities and attributes than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and attributes you actually plan on using.

With stock Singer taps, entity selection (and specification of other [metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)) involves a few steps. First, you run a tap in
[discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
to generate a `catalog.json` file describing all available entities and attributes.
Then, you edit this file and add `"selected": true` (and any other metadata) to the `metadata` objects for all of the desired entities and attributes.
Finally, you pass this file to the tap using the `--catalog` flag when you run it in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md).
Because these catalog files can be very large and can get outdated as data sources evolve, this process can be tedious and error-prone.

Meltano makes it easy to select specific entities and attributes for inclusion or exclusion using [`meltano select`](/docs/command-line-interface.html#select),
which lets you specify inclusion and exclusion rules that can contain [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) to match multiple entities and/or attributes at once.

Additional [Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
(like `replication-method` and `replication-key`) can be specified like
any other [plugin configuration](/docs/configuration.html), using a special
[`_metadata` setting](/docs/plugins.html#metadata-extra) with
[nested properties](/docs/command-line-interface.html#nested-properties)
`_metadata.<entity>.<key>` and `_metadata.<entity>.<attribute>.<key>`.

Similarly, a special [`_schema` setting](/docs/plugins.html#schema-extra)
is available that lets you easily override
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) descriptions.
Here too, [Unix shell-style wildcards](https://en.wikipedia.org/wiki/Glob_(programming)#Syntax) can be used to match multiple entities and/or attributes at once.

Whenever an extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt)
or [`meltano invoke`](/docs/command-line-interface.html#invoke), Meltano will
generate the desired catalog on the fly by running the tap in
discovery mode and applying the selection, metadata, and schema rules to the resulting catalog file
before passing it to the tap in sync mode.

Note that exclusion takes precedence over inclusion: if an entity or attribute is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and attributes are selected.

## Pipeline state

Most extractors (Singer taps) generate [state](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file) when they are run, that can be passed along with a subsequent invocation to have the extractor pick up where it left off the previous time.

Loaders (Singer targets) take in data and state messages from extractors and are responsible for forwarding the extractor state to Meltano once the associated data has been successfully persisted in the destination.

Meltano stores this pipeline state in its [system database](/docs/project.html#system-database), identified by the [`meltano elt`](/docs/command-line-interface.html#elt) run's Job ID.

When `meltano elt` is run a subsequent time, it will look for the most recent completed (successful or failed) pipeline run with the same job ID that generated some state. If found, this state is then passed along to the extractor.

::: tip Not seeing state picked up after a failed run?

Some loaders only emit state once their work is completely done, even if some data may have been persisted already, and if earlier state messages from the extractor could have been forwarded to Meltano. When a pipeline with such a loader fails or is otherwise interrupted, no state will have been emitted yet, and a subsequent ELT run will not be able to pick up where this run actually left off.

:::
