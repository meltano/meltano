#!/usr/bin/env bash

set -euo pipefail

LOG_FILE="./integration/example-library/meltano-run/integration-test.log"

# Custom validations for the `meltano-run` guide/test.

# test that meltano run saw dbt:test (set=1) as successfully completed
grep "Block run completed" $LOG_FILE
# test that we see dbt:run output
grep "Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=1 .*name=dbt-postgres" $LOG_FILE

# we could also run psql statements
# check for the existance of files
# etc
source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"
meltano state list | grep "dev:tap-gitlab-to-target-postgres"
meltano state get dev:tap-gitlab-to-target-postgres | grep "singer_state"
