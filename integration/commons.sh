#!/usr/bin/env bash

BASE_DIR=$(git rev-parse --show-toplevel)
INTEGRATION_BASE_DIR="${BASE_DIR}/integration"

# What we'll "compile" the markdown to.
TEST_SCRIPT_NAME="${TEST_NAME}.sh"

TEST_DOCS_DIR="./docs/example-library/$TEST_NAME"
if [ ! -d "$TEST_DOCS_DIR" ]; then
  echo "Test directory $TEST_DOCS_DIR does not exist"
  exit 1
fi

TEST_SCRIPT_SOURCE="${TEST_DOCS_DIR}/index.md"
if [ ! -f "$TEST_SCRIPT_SOURCE" ]; then
  echo "Test script source: $TEST_SCRIPT_SOURCE does not exist"
  exit 1
fi

TEST_MELTANO_YML="${TEST_DOCS_DIR}/meltano.yml"
if [ ! -f "$TEST_MELTANO_YML" ]; then
  echo "Test meltano.yml: $TEST_MELTANO_YML does not exist"
  exit 1
fi

TEST_MELTANO_YML_EXPECTED="${TEST_DOCS_DIR}/ending-meltano.yml"
if [ ! -f "$TEST_MELTANO_YML_EXPECTED" ]; then
  echo "Test expected ending meltano.yml: $TEST_MELTANO_YML_EXPECTED does not exist"
  exit 1
fi


inject_logging_yaml(){
  echo "Injecting a logging.yaml file..."
  cp "${INTEGRATION_BASE_DIR}"/logging.yaml "${TEST_DOCS_DIR}"/logging.yaml
}

compile_script(){
  echo "Generating shell script from $TEST_SCRIPT_SOURCE..."
  "${INTEGRATION_BASE_DIR}"/mdsh -c  "${TEST_SCRIPT_SOURCE}" > "${TEST_DOCS_DIR}/${TEST_SCRIPT_NAME}"
}

check_meltano_yaml(){
  echo "Checking to see if the resulting meltano.yml matches the expected meltano.yml..."
  diff "${TEST_MELTANO_YML}" "${TEST_MELTANO_YML_EXPECTED}"
}
