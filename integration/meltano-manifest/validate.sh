#!/usr/bin/env bash

set -eu

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

set +o pipefail

diff "$(git rev-parse --show-toplevel)/integration/meltano-manifest/expected-manifests/" '.meltano/manifests/'
