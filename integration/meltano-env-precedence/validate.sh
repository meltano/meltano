#!/usr/bin/env bash

set -eu

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

set +o pipefail

export STACKED=1

# FIXME: https://github.com/meltano/meltano/issues/7023
meltano invoke --print-var STACKED example 2>&1 | grep 'STACKED=4' > /dev/null

meltano --environment prod invoke --print-var STACKED example 2>&1 | grep 'STACKED=12345' > /dev/null

meltano install utility example 2>&1 | grep 'env-var-in-pip-url-example-124' > /dev/null
