---
title: Troubleshooting
description: Learn what you can do if you need to troubleshoot
layout: doc
redirect_from:
 - /reference/ui
 - /guide/ui/
sidebar_position: 25
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

If you have a question about Meltano, are having trouble getting it to work, or have any kind of feedback, you can:

<div class="columns is-multiline is-centered">
    <div class="column is-half">
      <div class="card chiclet">
        <div class="card-content has-text-centered">
          <div class="block">
            <p><span class="icon is-large"><i class="fab fa-github fa-5x"></i></span></p>
            <p>Check out the <a href="https://github.com/meltano/meltano/issues/">Meltano issue tracker</a> to see if someone else has already reported the same issue or made the same request. Feel free to weigh in with extra information, or just to make sure the issue gets the attention it deserves.</p>
          </div>
        </div>
      </div>
    </div>
    <div class="column is-half">
      <div class="card chiclet">
        <div class="card-content has-text-centered">
          <div class="block">
            <p><span class="icon is-large"><i class="fab fa-slack fa-5x"></i></span></p>
            <p>Join the <a href="https://meltano.com/slack">Meltano Slack workspace</a>, which is frequented by the core team and thousands of community members and data experts. You can ask any questions you may have in here or just chat with fellow users.</p>
          </div>
        </div>
      </div>
    </div>
</div>

## Common Issues

_Problem: "Why do **incremental runs** produce duplicate data?"_

Singer takes an "at least once" approach to replication, so if you're encountering this, it might be intended behavior. [This issue](https://github.com/MeltanoLabs/Singer-Working-Group/issues/13) is a good summary of the current state and a proposal to change this behavior.

_Problem: "My **runs take too long**."_

This [issue provides a good overview on a strategy to figure out performance issues](https://github.com/meltano/meltano/issues/6613#issuecomment-1215074973).

## How to Debug Problems

### Log Level Debug

When you are trying to troubleshoot an issue the Meltano logs should be your first port of call.

If you have a failure using Meltano's execution commands (`invoke`, `elt`, `run`, or `test`) or you're experienced general unexpected behavior, you can learn more about what’s happening behind the scenes by setting Meltano’s [`cli.log_level` setting](/reference/settings#clilog_level) to debug, using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI option:

<Tabs className="meltano-tabs" queryString="meltano-tabs">
  <TabItem className="meltano-tab-content" value="meltano config" label="meltano config" default>

```bash
meltano config meltano set cli log_level debug
```

  </TabItem>
  <TabItem className="meltano-tab-content" value="env" label="env" default>

```bash
export MELTANO_CLI_LOG_LEVEL=debug
```

  </TabItem>
  <TabItem className="meltano-tab-content" value="command" label="command" default>

```bash
meltano --log-level=debug <command> ...
```

  </TabItem>
</Tabs>

In debug mode, Meltano will log additional information about the environment and arguments used to invoke your components (Singer taps and targets, dbt, Airflow, etc.), including the paths to the generated config, catalog, state files, etc. for you to review.

Here is an example with `meltano run`:

```
$ meltano --log-level=debug run tap-gitlab target-jsonl
2023-02-01T17:17:43.308389Z [info     ] Environment 'dev' is active
2023-02-01T17:17:43.375158Z [debug    ] Creating engine '<meltano.core.project.Project object at 0x10d9ff5e0>@sqlite:////demo-project/.meltano/meltano.db'
2023-02-01T17:17:43.646112Z [debug    ] Found plugin parent            parent=tap-gitlab plugin=tap-gitlab source=lockfile
2023-02-01T17:17:43.650014Z [debug    ] found plugin in cli invocation plugin_name=tap-gitlab
2023-02-01T17:17:43.652873Z [debug    ] Found plugin parent            parent=target-jsonl plugin=target-jsonl source=lockfile
2023-02-01T17:17:43.656906Z [debug    ] found plugin in cli invocation plugin_name=target-jsonl
2023-02-01T17:17:43.657112Z [debug    ] head of set is extractor as expected block=<meltano.core.plugin.project_plugin.ProjectPlugin object at 0x1115be850>
2023-02-01T17:17:45.337292Z [debug    ] found block                    block_type=loaders index=1
2023-02-01T17:17:45.337455Z [debug    ] blocks                         idx=1 offset=0
2023-02-01T17:18:54.233065Z [debug    ] found ExtractLoadBlocks set    offset=0
2023-02-01T17:18:54.233220Z [debug    ] All ExtractLoadBlocks validated, starting execution.
2023-02-01T17:18:56.271112Z [debug    ] Created configuration at /home/.meltano/run/tap-gitlab/tap.54d0e4e3-eb71-4000-9138-47a25c8b3743.config.json
2023-02-01T17:18:56.271662Z [debug    ] Could not find tap.properties.json in /home/.meltano/extractors/tap-gitlab/tap.properties.json, skipping.
2023-02-01T17:18:56.272003Z [debug    ] Could not find tap.properties.cache_key in /home/.meltano/extractors/tap-gitlab/tap.properties.cache_key, skipping.
2023-02-01T17:18:56.272321Z [debug    ] Could not find state.json in /home/.meltano/extractors/tap-gitlab/state.json, skipping.
2023-02-01T17:18:56.355385Z [warning  ] No state was found, complete import.
...
```

### Isolate the Connector

If it's unclear which part of the pipeline is generating the problem, test the tap and target individually by using `meltano invoke`.
The [`invoke` command](/reference/command-line-interface#invoke) will run the executable with any specified arguments.

```bash
meltano invoke <plugin> [PLUGIN_ARGS...]
```

It's usually easiest to pipe the raw output of the tap to a file to confirm the tap works then pipe that file's contents to the target so the tap doesn't have to re-replicate the data.
For example:

```bash
meltano invoke tap-csv > output.json
cat output.json | meltano invoke target-postgres
```

### Validate Tap Capabilities

In cases where the tap is not loading any streams or it does not appear to be respecting the configured [`select`](/reference/command-line-interface#select) rules, you may need to validate the capabilities of the tap.

In prior versions of the Singer spec, the `--properties` option was used instead of `--catalog` for the [catalog files](https://hub.meltano.com/singer/spec#catalog-files).
If this is the case for a tap, ensure `properties` is set as a [capability](/contribute/plugins) for the tap instead of `catalog`.
Then `meltano el` will accept the catalog file and will pass it to the tap using the appropriate flag.

For more information, please refer to the [plugin capabilities reference](/reference/plugin-definition-syntax#capabilities).

### Testing Specific Failing Streams

When extracting several streams with a single tap using the `elt` command, it may be challenging to debug a single failing stream.
In this case, it can be useful to run the tap with just the single stream selected.

Instead of duplicating the extractor in `meltano.yml`, try running `meltano el` with the [`--select` flag](/reference/command-line-interface#parameters-2).
This will run the pipeline with just that stream selected.

You can also have `meltano invoke` select an individual stream by setting the [`select_filter` extra](/concepts/plugins#select-filter-extra) as an environment variable:

```bash
export <TAP_NAME>__SELECT_FILTER='["<your_stream>"]'
```

### Incremental Replication Not Running as Expected

If using a custom tap, ensure that the tap declares the `state` capability as described in the [plugin capabilities reference](/reference/plugin-definition-syntax#capabilities).

If you're using `meltano run` be aware that the state ID is generated using the extractor name + loader name + environment name. If you switched multiple environments you might not have the state you were expecting.

If you're trying to run a pipeline with incremental replication using `meltano el` but it's running a full sync, ensure that you're passing a [State ID](/getting-started#run-a-data-integration-el-pipeline) via the [`--state-id` flag](/reference/command-line-interface#how-to-use-4).

### Dump Files Generated by Running Meltano Commands to STDOUT

The [`--dump` flag](/reference/command-line-interface#parameters-1) can be passed to the `meltano invoke` and `meltano el` commands to dump the content of a pipeline-specific generated file to `STDOUT` instead of actually running the pipeline. Note that adding support for `meltano run` is tracked in [this GitHub issue](https://github.com/meltano/meltano/issues/3072).

This can aid in debugging extractor catalog generation, incremental replication state lookup, and pipeline environment variables.

Supported values are:

- **catalog**: Dump the extractor catalog file that would be passed to the tap’s executable using the `--catalog` option.
- **state**: Dump the extractor state file that would be passed to the tap’s executable using the `--state` option.
- **extractor-config**: Dump the extractor config file that would be passed to the tap’s executable using the `--config` option.
- **loader-config**: Dump the loader config file that would be passed to the target’s executable using the `--config` option.

Like any standard output, the dumped content can be redirected to a file using >, e.g. `meltano el ... --dump=state > state.json`.

Examples #

```bash
meltano el tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres

meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --full-refresh

meltano el tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano el tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano el tap-gitlab target-postgres --select commits
meltano el tap-gitlab target-postgres --exclude project_members

meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

### Alternatives to `meltano run --dump`

While the `--dump` flag is not supported with `meltano run`, you can achieve the same outcomes using other Meltano commands:

#### Dumping State

Instead of `meltano run ... --dump=state`, use:

```bash
meltano state get <STATE_ID>
```

#### Dumping Extractor Configuration

Instead of `meltano run ... --dump=extractor-config`, use:

```bash
meltano config <EXTRACTOR_NAME> list
```

Alternatively, you can use:

```bash
meltano invoke <EXTRACTOR_NAME> --dump=config
```

#### Dumping Loader Configuration

Instead of `meltano run ... --dump=loader-config`, use:

```bash
meltano config <LOADER_NAME> list
```

#### Dumping Catalog

Instead of `meltano run ... --dump=catalog`, use:

```bash
meltano invoke <EXTRACTOR_NAME> --dump=catalog
```

### Meltano UI

Early versions of Meltano promoted a simple UI feature that was used for setting up basic pipelines and viewing basic logs. Due to a refocusing of the product on the command line interface, the UI was deprioritized for continued feature enhancements. For [interactive plugin configuration](/reference/command-line-interface#how-to-use-interactive-config), we now recommend our `--interactive` config option in the CLI.

Meltano will eventually have a UI again as the company and community grows. Please let us know your thoughts on what you would like to see in a future Meltano UI in [this GitHub discussion](https://github.com/meltano/meltano/discussions/6957).

To view the previous documentation on the UI, review [this pull request](https://github.com/meltano/meltano/pull/6955) where they were removed.

#### Limitations & Capabilities of the Deprecated UI

If you are still using the UI, please note that it is not compatible with many newer Meltano features.

The UI **does** work with:

- Schedules based on [the `elt` command](https://docs.meltano.com/reference/command-line-interface#elt) (`meltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform ...`)

The UI does **not** work with:

- Schedules based on [jobs](https://docs.meltano.com/reference/command-line-interface#job) (`meltano schedule add <schedule_name> --job <job>`)
- [Environments](https://docs.meltano.com/concepts/environments)

#### Replacing UI functionality

If you're using [Airflow](https://hub.meltano.com/utilities/airflow) or [Dagster](https://hub.meltano.com/utilities/dagster) as your orchestrator, the Airflow or Dagster webserver UI should be able to serve as a replacement for many Meltano UI use cases.

If using Airflow as orchestrator, see the ["Airflow orchestrator" section of the "Deployment in Production" guide](/guide/production#airflow-orchestrator) for more details on how to get the webserver running. From the webserver, you can [view all DAGs](https://airflow.apache.org/docs/apache-airflow/2.10.5/ui.html#dags-view). You can also access the Meltano logs for a specific task instance [in the Audit Log](https://airflow.apache.org/docs/apache-airflow/2.10.5/ui.html#audit-log).

### No Plugin Settings Defined

To configure a plugin that does not already have settings defined, we recommend first adding a `settings:` entry under the plugin definition. You may need to consult the plugin's documentation to determine what settings are available.

Related reference information and guides:

- [Overriding discoverable plugin properties](https://docs.meltano.com/guide/configuration#overriding-discoverable-plugin-properties)
- [Plugin `settings` syntax reference](https://docs.meltano.com/reference/plugin-definition-syntax#settings)
- [Custom settings guide](https://docs.meltano.com/guide/configuration#custom-settings)

After adding definitions for the plugin's settings, you may then configure those settings as usual with the `--interactive` option in `meltano config`.

You may also contribute back to the community by publishing the settings to [MeltanoHub](https://hub.meltano.com) in the form of a new pull request.
