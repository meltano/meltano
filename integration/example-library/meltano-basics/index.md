# Basic meltano usage

A quick overview of how to use meltano - using a prepopulated meltano.yml.

## Setup

To begin, download or copy the [meltano.yml](/integration/example-library/meltano-basic/meltano.yml) to an empty directory and run:

```shell
meltano install
```

## Adjusting the configuration

Adjust the configuration in `meltano.yml` if you wish. For example, you might want to set
an explicit start_date from which you would like tap-gitlab to start importing data, and you might prefer
that the resulting jsonl files NOT actually include timestamps in their file names:

```shell
meltano config set tap-gitlab start_date 2022-04-25T00:00:01Z
meltano config set target-jsonl do_timestamp_file false
```

## Running a task

With tap-gitlab installed and configured and a target-jsonl target installed, we can perform an EL task:

```shell
meltano run tap-gitlab target-jsonl
```
