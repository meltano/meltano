#!/usr/bin/env bash
set -euo pipefail

source $(git rev-parse --show-toplevel)/integration/commons.sh

TEST_DIR="./docs/example-library/meltano-basics/"
TEST_SCRIPT_SOURCE="${TEST_DIR}/index.md"
TEST_MELTANO_YML="${TEST_DIR}/meltano.yml"
TEST_MELTANO_YML_EXPECTED="${TEST_DIR}/ending-meltano.yml"

inject_logging_yaml "${TEST_DIR}"
compile_script "${TEST_SCRIPT_SOURCE}" basics.sh

echo "bash -xeuo pipefail basics.sh"

check_meltano_yaml "${TEST_MELTANO_YML}" "${TEST_MELTANO_YML_EXPECTED}"
