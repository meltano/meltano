# Annotations in Meltano project files

This example runs through a variety of operations with a `meltano.yml` that has [annotations](https://docs.meltano.com/concepts/project#annotations).

This example shows how Meltano *does not* affect/use annotations itself.

To begin, download or copy the [meltano.yml](/docs/example-library/meltano-s3/meltano.yml) to an empty directory and run:

```shell
meltano install
```

## Configure meltano to use local filesystem for state.

```shell
meltano config meltano set state_backend.uri "file:///`pwd`/.meltano/state"
```

## Configure the tap and target

```shell
meltano config tap-gitlab set start_date 2022-11-01T00:00:01Z
meltano config target-jsonl set do_timestamp_file false
```

## Update a job

```shell
meltano job set gitlab-to-jsonl --tasks '[tap-gitlab target-jsonl]'
```

## Run a job

```shell
meltano run gitlab-to-jsonl
```

## Check state output

```shell
meltano state get dev:tap-gitlab-to-target-jsonl
```

## Update a schedule

```shell
meltano schedule set daily-gitlab-to-jsonl --interval '5 4 * * *'
```
