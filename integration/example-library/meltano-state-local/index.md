# Using the local filesystem as a state backend

To begin, download or copy the [meltano.yml](/integration/example-library/meltano-state-local/meltano.yml) to an empty directory and run:

```shell
meltano install
```

## Configure meltano to use local filesystem for state.

```shell
meltano config set meltano state_backend.uri "file:///`pwd`/.meltano/state"
```

## Configure the tap and target

```shell
meltano config set tap-gitlab start_date 2022-11-01T00:00:01Z
meltano config set target-jsonl do_timestamp_file false
```

## Run a job

```shell
meltano run tap-gitlab target-jsonl
```

## Check state output

```shell
meltano state get dev:tap-gitlab-to-target-jsonl
```
