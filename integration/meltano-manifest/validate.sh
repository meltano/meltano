#!/usr/bin/env bash

set -eu

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

set +o pipefail

# Add a newline to the end of any generated manifest if one is missing.
# If we don't do this, then we have to skip the json linter and
# end-of-file-fixer for the expected manifests. This is easier.
for file in .meltano/manifests/*.json; do ed -s "${file}" <<< w; done

diff "$(git rev-parse --show-toplevel)/integration/meltano-manifest/expected-manifests/" '.meltano/manifests/'
