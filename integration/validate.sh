#!/usr/bin/env bash
set -euo pipefail

TEST_NAME=${1:-}
if [ -z "$TEST_NAME" ]; then
  echo "Usage: $0 <test_name>"
  echo "Example: $0 meltano-basics"
  exit 1
fi

source "$(git rev-parse --show-toplevel)/integration/commons.sh"

inject_logging_yaml
compile_script

CURRENT_DIR=$(pwd)
cd "${TEST_DOCS_DIR}"
echo "Running orchestration script..."
bash -xeuo pipefail "${TEST_NAME}.sh"
cd "${CURRENT_DIR}"

check_meltano_yaml

# if theres a per test validate.sh, run it as well
if [ -f "${INTEGRATION_BASE_DIR}/${TEST_NAME}/validate.sh" ]; then
  export TEST_NAME="$TEST_NAME"
  echo "Running per test validate.sh..."
  bash -xeuo pipefail "${INTEGRATION_BASE_DIR}/${TEST_NAME}/validate.sh"
fi
