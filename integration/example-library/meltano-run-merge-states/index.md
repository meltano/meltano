# Get setup

This example shows how state from sequential invocations of `meltano run` can be merged together to create a state object that combines bookmarks from streams synced in different runs.

This is useful for when you want to backfill/refresh a single stream, without losing the state of other streams.

```shell
meltano install
```

## Without state merging (default)

### Extract all streams

```shell
TAP_WITH_STATE_TS='2023-01-01T00:00:00+00:00' \
meltano run tap-with-state target-jsonl --state-id-suffix=no-merge
```

### Extract a single stream

Run a 'full refresh' pipeline of a single stream.

```shell
TAP_WITH_STATE_TS='2023-01-01T01:00:00+00:00' \
TAP_WITH_STATE__SELECT_FILTER='["stream_1"]' \
meltano run tap-with-state target-jsonl --full-refresh --state-id-suffix=no-merge --state-strategy=overwrite
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
        "created_at": "2023-01-01T01:00:00+00:00"
      }
    }
  }
}
```

## With state merging

### Extract all streams

```shell
TAP_WITH_STATE_TS='2023-01-01T00:00:00+00:00' \
meltano run tap-with-state target-jsonl --state-id-suffix=merge
```

### Filter a single stream, merging states

Run a 'full refresh' pipeline of a single stream, but merge the current pipelines state with the latest stored state.

```shell
TAP_WITH_STATE_TS='2024-01-01T00:00:00+00:00' \
TAP_WITH_STATE__SELECT_FILTER='["stream_1"]' \
meltano run tap-with-state target-jsonl --full-refresh --state-id-suffix=merge --state-strategy=merge
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
        "created_at": "2024-01-01T00:00:00+00:00"
      },
      "stream_2": {
        "created_at": "2023-01-01T00:00:00+00:00"
      },
      "stream_3": {
        "created_at": "2023-01-01T00:00:00+00:00"
      }
    }
  }
}
```
