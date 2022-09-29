# Add environments, jobs and schedules with the CLI

Using the CLI to add Meltano objects to a project.

## Setup

To begin, download or copy the [meltano.yml](/docs/example-library/meltano-objects/meltano.yml) to an empty directory.

## Add a few plugins

```shell
meltano add extractor tap-gitlab
meltano add loader target-jsonl
```

## Add some environments

```shell
meltano environment add qa
meltano environment add prod
```

## Add a job

```shell
meltano job add gitlab_to_jsonl --tasks '["tap-gitlab target-jsonl"]'
```

## Add a schedule

```shell
meltano schedule add run_gitlab --job gitlab_to_jsonl --interval "@daily"
```

## Remove a plugin

```shell
meltano remove extractor tap-gitlab
```
