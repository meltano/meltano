---
title: Troubleshooting
description: Learn what you can do if you need to troubleshoot
layout: doc
redirect_from:
 - /reference/ui
 - /guide/ui/
weight: 25
---

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

# Common Issues

*Problem: "Why do **incremental runs** produce duplicate data?"*

Singer takes an "at least once" approach to replication, so if you're encountering this, it might be intended behavior. [This issue](https://github.com/MeltanoLabs/Singer-Working-Group/issues/13) is a good summary of the current state and a proposal to change this behavior.

*Problem: "My **runs take too long**."*

This [issue provides a good overview on a strategy to figure out performance issues](https://github.com/meltano/meltano/issues/6613#issuecomment-1215074973).

# How to Debug Problems

## Log Level Debug

When you are trying to troubleshoot an issue the Meltano logs should be your first port of call.

If you have a failure using Meltano's execution commands (`invoke`, `elt`, `run`, or `test`) or you're experienced general unexpected behavior, you can learn more about what’s happening behind the scenes by setting Meltano’s [`cli.log_level` setting](/reference/settings#clilog_level) to debug, using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI option:

```bash
export MELTANO_CLI_LOG_LEVEL=debug

meltano --log-level=debug <command> ...
```

In debug mode, Meltano will log additional information about the environment and arguments used to invoke your components (Singer taps and targets, dbt, Airflow, etc.), including the paths to the generated config, catalog, state files, etc. for you to review.

Here is an example with `meltano elt`:

```
$ meltano --log-level=debug elt tap-gitlab target-jsonl --state-id=gitlab-to-jsonl
meltano            | INFO Running extract & load...
meltano            | INFO Found state from 2020-08-05 21:30:20.487312.
meltano            | DEBUG Invoking: ['demo-project/.meltano/extractors/tap-gitlab/venv/bin/tap-gitlab', '--config', 'demo-project/.meltano/run/tap-gitlab/tap.config.json', '--state', 'demo-project/.meltano/run/tap-gitlab/state.json']
meltano            | DEBUG Env: {'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2021-03-01'}
meltano            | DEBUG Invoking: ['demo-project/.meltano/loaders/target-jsonl/venv/bin/target-jsonl', '--config', 'demo-project/.meltano/run/target-jsonl/target.config.json']
meltano            | DEBUG Env: {'MELTANO_EXTRACTOR_NAME': 'tap-gitlab', 'MELTANO_EXTRACTOR_NAMESPACE': 'tap_gitlab', 'MELTANO_EXTRACT_API_URL': 'https://gitlab.com', 'MELTANO_EXTRACT_PRIVATE_TOKEN': '', 'MELTANO_EXTRACT_GROUPS': '', 'MELTANO_EXTRACT_PROJECTS': 'meltano/meltano', 'MELTANO_EXTRACT_ULTIMATE_LICENSE': 'False', 'MELTANO_EXTRACT_START_DATE': '2021-03-01', 'TAP_GITLAB_API_URL': 'https://gitlab.com', 'GITLAB_API_TOKEN': '', 'GITLAB_API_GROUPS': '', 'GITLAB_API_PROJECTS': 'meltano/meltano', 'GITLAB_API_ULTIMATE_LICENSE': 'False', 'GITLAB_API_START_DATE': '2021-03-01', 'TARGET_JSONL_DESTINATION_PATH': 'output', 'TARGET_JSONL_DO_TIMESTAMP_FILE': 'False'}
```

## No Plugin Settings Defined

To configure a plugin that does not already have settings defined, we recommend first adding a `settings:` entry under the plugin definition. You may need to consult the plugin's documentation to determine what settings are available.

Related reference information and guides:

- [Overriding discoverable plugin properties](https://docs.meltano.com/guide/configuration#overriding-discoverable-plugin-properties)
- [Plugin `settings` syntax reference](https://docs.meltano.com/reference/plugin-definition-syntax#settings)
- [Custom settings guide](https://docs.meltano.com/guide/configuration#custom-settings)

After adding definitions for the plugin's settings, you may then configure those settings as usual with the `--interactive` option in `meltano config`.

You may also contribute back to the community by publishing the settings to [MeltanoHub](https://hub.meltano.com) in the form of a new pull request.

## Dump Files Generated by Running Meltano Commands to STDOUT

The [`--dump` flag](/reference/command-line-interface#parameters-1) can be passed to the `meltano invoke` and `meltano elt` commands to dump the content of a pipeline-specific generated file to `STDOUT` instead of actually running the pipeline. Note that adding support for `meltano run` is tracked in [this GitHub issue](https://github.com/meltano/meltano/issues/3072).

This can aid in debugging extractor catalog generation, incremental replication state lookup, and pipeline environment variables.

Supported values are:

- **catalog**: Dump the extractor catalog file that would be passed to the tap’s executable using the `--catalog` option.
- **state**: Dump the extractor state file that would be passed to the tap’s executable using the `--state` option.
- **extractor-config**: Dump the extractor config file that would be passed to the tap’s executable using the `--config` option.
- **loader-config**: Dump the loader config file that would be passed to the target’s executable using the `--config` option.

Like any standard output, the dumped content can be redirected to a file using >, e.g. `meltano elt ... --dump=state > state.json`.

Examples #
```bash
meltano elt tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres

meltano elt tap-gitlab target-postgres --state-id=gitlab-to-postgres --full-refresh

meltano elt tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano elt tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano elt tap-gitlab target-postgres --select commits
meltano elt tap-gitlab target-postgres --exclude project_members

meltano elt tap-gitlab target-postgres --state-id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

## Meltano UI

Early versions of Meltano promoted a simple UI feature that was used for setting up basic pipelines and viewing basic logs. Due to a refocusing of the product on the command line interface, the UI was deprioritized for continued feature enhancements. For [interactive plugin configuration](/reference/command-line-interface#how-to-use-interactive-config), we now recommend our `--interactive` config option in the CLI.

Meltano will eventually have a UI again as the company and community grows. Please let us know your thoughts on what you would like to see in a future Meltano UI in [this GitHub discussion](https://github.com/meltano/meltano/discussions/6957).

To view the previous documentation on the UI, review [this pull request](https://github.com/meltano/meltano/pull/6955) where they were removed.

### Limitations & Capabilities of the Deprecated UI

If you are still using the UI, please note that it is not compatible with many newer Meltano features.

The UI **does** work with:
- Schedules based on [the `elt` command](https://docs.meltano.com/reference/command-line-interface#elt) (`meltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform ...`)

The UI does **not** work with:
- Schedules based on [jobs](https://docs.meltano.com/reference/command-line-interface#job) (`meltano schedule add <schedule_name> --job <job>`)
- [Environments](https://docs.meltano.com/concepts/environments)

### Replacing UI functionality

If you're using [Airflow](https://hub.meltano.com/utilities/airflow) or [Dagster](https://hub.meltano.com/utilities/dagster) as your orchestrator, the Airflow or Dagster webserver UI should be able to serve as a replacement for many Meltano UI use cases.

If using Airflow as orchestrator, see the ["Airflow orchestrator" section of the "Deployment in Production" guide](/guide/production#airflow-orchestrator) for more details on how to get the webserver running. From the webserver, you can [view all DAGs](https://airflow.apache.org/docs/apache-airflow/1.10.14/ui.html#dags-view). You can also access the Meltano logs for a specific task instance by going to the [task instance context menu](https://airflow.apache.org/docs/apache-airflow/1.10.14/ui.html#task-instance-context-menu) and clicking "Log" or "View logs".
