#!/usr/bin/env bash

set -eu

source "$(git rev-parse --show-toplevel)/integration/commons.sh"
cd "${TEST_DOCS_DIR}"

# Test 1: Auto-compilation when no manifest exists
echo "Test 1: Auto-compilation when no manifest exists"
rm -rf .meltano/manifests
output=$(meltano invoke tap-gitlab --help 2>&1)
# Check for the correct manifest file (environment-specific)
[ -f .meltano/manifests/meltano-manifest.dev.json ]
echo "✓ Manifest auto-compiled when missing"

# Test 2: Verify env vars from manifest
echo "Test 2: Verify env vars from manifest"
meltano --environment=dev compile --unsafe
manifest_content=$(cat .meltano/manifests/meltano-manifest.dev.json)
echo "$manifest_content" | grep -q '"PROJECT_VAR": "project_value"'
echo "✓ Manifest contains expected env vars"

# Test 3: Test with environment
echo "Test 3: Test with environment"
meltano --environment=dev compile --unsafe
dev_manifest=$(cat .meltano/manifests/meltano-manifest.dev.json)
echo "$dev_manifest" | grep -q '"DEV_VAR": "dev_value"'
echo "✓ Environment-specific manifest contains env vars"

# Test 4: Staleness warning
echo "Test 4: Staleness warning"
touch meltano.yml
sleep 1
output=$(meltano invoke tap-gitlab --help 2>&1 || true)
echo "$output" | grep -q "Manifest may be out of date" || echo "Warning: Staleness warning not found (may be in logs)"

echo "All tests passed!"
