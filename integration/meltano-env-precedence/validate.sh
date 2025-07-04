#!/usr/bin/env bash

set -eu

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

set +o pipefail

export STACKED=1

meltano install example

# FIXME: https://github.com/meltano/meltano/issues/7023
[ "$(meltano invoke --print-var STACKED example:echo-stacked)" = $'STACKED=4\nStacked env var value is: 4' ]

[ "$(meltano --environment prod invoke --print-var STACKED example:echo-stacked)" = $'STACKED=12345\nStacked env var value is: 12345' ]

# FIXME: https://github.com/meltano/meltano/issues/7034
# shellcheck disable=SC2016
[ "$(meltano invoke example:echo-config)" = 'Config value is: ${STACKED}4' ]
# shellcheck disable=SC2016
[ "$(meltano --environment prod invoke example:echo-config)" = 'Config value is: ${STACKED}5' ]
