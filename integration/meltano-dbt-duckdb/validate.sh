#!/usr/bin/env bash

set -euo pipefail

LOG_FILE="./integration/example-library/meltano-dbt-duckdb/integration-test.log"

# Custom validations for the `meltano-dbt-duckdb` guide/test.

grep "Block run completed" $LOG_FILE
# dbt colorizes its output in CI, so strip ANSI escape codes before matching
sed $'s/\x1b\\[[0-9;]*m//g' $LOG_FILE | grep -F "Summary: 2 total | 2 success"

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"
meltano state list | grep "dev:tap-smoke-test-to-target-duckdb"
