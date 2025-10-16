#!/usr/bin/env bash
# shellcheck disable=SC1091

set -euo pipefail

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

# Check config in .env
grep "MELTANO_STATE_BACKEND_URI" < .env
grep "MELTANO_STATE_BACKEND_S3_ENDPOINT_URL" < .env

grep "singer_state" < state.json
grep '{"singer_state":{"bookmark-1":0}}' < new_state.json
