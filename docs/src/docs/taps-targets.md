# Taps & Targets

## Tap

See our [sample first tap](https://gitlab.com/meltano/tap-gitlab/) as a good tap starting point.

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of taps](https://www.singer.io/#taps)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

## Target

See our [csv target](https://gitlab.com/meltano/target-csv) as a good starting point for targets.

Based on [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)

[List of targets](https://singer.io/#targets)

Also see [workflow for tap/target development](#workflow-for-tap-target-development)

## Workflow for tap/target development

### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target developement please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitLab
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

## Discoverability

We will maintain a curated list of taps/targets that are expected to work out of the box with Meltano.

Meltano should help the end-user find components via a `discover` command:

```
$ meltano discover extract
tap-demo==...
tap-zendesk==1.3.0
tap-marketo==...
...

$ meltano discover load
target-demo==...
target-snowflake==git+https://gitlab.com/meltano/target-snowflake@master.git
target-postgres==...
```

## How to install taps/targets

### Locally

See `meltano-add`

### On a CI

A docker image should be build containing all the latest curated version of the taps/targets, each isolated into its own virtualenv.

This way we do not run into `docker-in-docker` problems (buffering, permissions, security).

Meltano should provide a wrapper script to manage the execution of the selected components:

`meltano extract tap-zendesk --to target-postgres`