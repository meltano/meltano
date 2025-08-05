#!/usr/bin/env bash
# shellcheck disable=SC1091

set -euo pipefail

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

meltano state get dev:tap-with-state-to-target-jsonl:no-merge | grep '{"singer_state": {"bookmarks": {"stream_1": {"created_at": "2023-01-01T01:00:00+00:00"}}}}'
meltano state get dev:tap-with-state-to-target-jsonl:merge | grep '{"singer_state": {"bookmarks": {"stream_1": {"created_at": "2024-01-01T00:00:00+00:00"}, "stream_2": {"created_at": "2023-01-01T00:00:00+00:00"}, "stream_3": {"created_at": "2023-01-01T00:00:00+00:00"}}}}'
