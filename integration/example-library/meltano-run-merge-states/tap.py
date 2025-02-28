#!/usr/bin/env python

"""Simple Singer tap."""

from __future__ import annotations

import argparse
import datetime
import json
import sys

CATALOG = {
    "streams": [
        {
            "tap_stream_id": f"stream_{i}",
            "schema": {
                "properties": {
                    "id": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "metadata": [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "selected": True,
                    },
                },
            ],
        }
        for i in (1, 2, 3)
    ],
}


def sync_stream(stream_id: str, timestamp: str):
    """Sync a stream."""
    sys.stdout.write(
        json.dumps(
            {
                "type": "SCHEMA",
                "stream": stream_id,
                "schema": {
                    "properties": {
                        "id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                },
                "key_properties": ["id"],
            },
        )
        + "\n",
    )
    sys.stdout.write(
        json.dumps(
            {
                "type": "RECORD",
                "stream": stream_id,
                "record": {
                    "id": 1,
                    "created_at": timestamp,
                },
            },
        )
        + "\n",
    )


def is_selected(stream_id: str, catalog: dict):
    """Check if a stream is selected."""
    for stream in catalog["streams"]:
        if stream["tap_stream_id"] != stream_id:
            continue
        metadata = stream.get("metadata", [])
        stream_metadata = next(
            filter(lambda m: m.get("breadcrumb") == [], metadata),
            {},
        )
        print(f"stream_metadata: {stream_metadata}", file=sys.stderr)
        return stream_metadata.get("metadata", {}).get("selected", False)

    return False


def sync(config: dict, catalog: dict, state: dict):
    """Sync data."""
    print(f"catalog: {catalog}", file=sys.stderr)
    timestamp = config.get(
        "ts",
        datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
    )
    state = {"bookmarks": {}}

    for i in (1, 2, 3):
        if not is_selected(f"stream_{i}", catalog):
            continue
        sync_stream(f"stream_{i}", timestamp)
        state["bookmarks"][f"stream_{i}"] = {"created_at": timestamp}

    sys.stdout.write(json.dumps({"type": "STATE", "value": state}))


def discover():
    """Discover catalog."""
    sys.stdout.write(json.dumps(CATALOG))


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=argparse.FileType("r"))
    parser.add_argument("--catalog", type=argparse.FileType("r"))
    parser.add_argument("--state", type=argparse.FileType("r"))
    parser.add_argument("--discover", action="store_true")
    args = parser.parse_args()

    if args.discover:
        discover()
        return

    config = json.load(args.config) if args.config else {}
    catalog = json.load(args.catalog) if args.catalog else {}
    state = json.load(args.state) if args.state else {}

    sync(config, catalog, state)


if __name__ == "__main__":
    main()
