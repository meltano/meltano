# Get setup

This example shows how state from sequential invocations of `meltano run` can be merged together to create a single state file.

This is useful for when you want to backfill/refresh a single stream, without losing the state of other streams.

```shell
meltano install
```

## Without state file merging (default)

### Extract all streams

```shell
TAP_WITH_STATE_TS='2023-01-01T00:00:00Z' \
meltano run tap-with-state target-jsonl --state-id-suffix=no-merge
```

### Extract a single stream

Run a 'full refresh' pipeline of a single stream.

```shell
TAP_WITH_STATE_TS='2023-01-01T01:00:00Z' \
TAP_WITH_STATE__SELECT_FILTER='["stream_1"]' \
meltano run tap-with-state target-jsonl --full-refresh --state-id-suffix=no-merge
```

Note that the state will only contain the bookmark for `stream_1`.

```shell
meltano --environment=dev state get dev:tap-with-state-to-target-jsonl:no-merge
```

```json
{
  "singer_state": {
    "bookmarks": {
      "stream_1": {
        "created_at": "2023-01-01T01:00:00Z"
      }
    }
  }
}
```

## With state file merging

### Extract all streams

```shell
TAP_WITH_STATE_TS='2023-01-01T00:00:00Z' \
meltano run tap-with-state target-jsonl --state-id-suffix=merge
```

### Filter a single stream, merging states

Run a 'full refresh' pipeline of a single stream, but merge the state with the existing state.

```shell
TAP_WITH_STATE_TS='2023-01-01T01:00:00Z' \
TAP_WITH_STATE__SELECT_FILTER='["stream_1"]' \
meltano run tap-with-state target-jsonl --full-refresh --state-id-suffix=merge --merge-state
```

Note that the state will now contain both the new bookmark for `stream_1` and the old bookmarks for the other streams.

```shell
meltano --environment=dev state get dev:tap-with-state-to-target-jsonl:merge
```

```json
{
  "singer_state": {
    "bookmarks": {
      "stream_1": {
        "created_at": "2023-01-01T01:00:00Z"
      },
      "stream_2": {
        "created_at": "2023-01-01T00:00:00Z"
      },
      "stream_3": {
        "created_at": "2023-01-01T00:00:00Z"
      }
    }
  }
}
```
