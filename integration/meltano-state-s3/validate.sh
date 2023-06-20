#!/usr/bin/env bash

set -euo pipefail

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

# Check config in .env
grep "MELTANO_STATE_BACKEND_URI" < .env
grep "MELTANO_STATE_BACKEND_S3_ENDPOINT_URL" < .env

meltano state list | grep "dev:tap-gitlab-to-target-jsonl"
meltano state get dev:tap-gitlab-to-target-jsonl | grep "singer_state"

meltano state set --force dev:tap-gitlab-to-target-jsonl '{"singer_state": {"bookmark-1": 0}}'

meltano state get dev:tap-gitlab-to-target-jsonl | grep '{"singer_state": {"bookmark-1": 0}}'
