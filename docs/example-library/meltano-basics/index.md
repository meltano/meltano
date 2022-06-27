# Basic meltano usage

## Setup

To begin, copy `meltano.yml` to a new directory and run `meltano install`:

```shell
echo meltano install
```

## Adjusting the configuration

Adjust the configuration in `meltano.yml` to your needs. For example, you might want to set
an explicit start_date from which you would like tap-gitlab to start importing data, and you might prefer
that the resulting jsonl files NOT actually include timestamps in their file names:

```shell
echo meltano config tap-gitlab set start_date 2022-04-25T00:00:01Z
echo meltano config target-jsonl set do_timestamp_file false
```

## Running a task

With tap-gitlab installed and configured and a target-jsonl target installed, we can run EL task:

```shell
echo meltano run tap-gitlab target-jsonl
```
