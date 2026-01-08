#!/bin/bash
# Script to compare performance across different Meltano versions

set -e

echo "======================================================================"
echo "Performance Comparison Script"
echo "======================================================================"
echo ""

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Function to run benchmark
run_benchmark() {
    local version=$1
    echo "======================================================================"
    echo "Testing $version"
    echo "======================================================================"
    uv run python benchmark_state_backend.py
    echo ""
}

# Test v3.6.0
echo "Switching to v3.6.0..."
git checkout v3.6.0 2>&1 | grep -v "^Note:"
run_benchmark "v3.6.0 (baseline - fast)"

# Test v3.7.9
echo "Switching to v3.7.9..."
git checkout v3.7.9 2>&1 | grep -v "^Note:"
run_benchmark "v3.7.9 (regression - slow)"

# Test current branch
echo "Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH" 2>&1 | grep -v "^Note:"
run_benchmark "$CURRENT_BRANCH (with fix)"

echo "======================================================================"
echo "Comparison Complete"
echo "======================================================================"
echo ""
echo "Summary:"
echo "- v3.6.0: Baseline performance (no addon system)"
echo "- v3.7.9: Performance regression (addon system without optimization)"
echo "- $CURRENT_BRANCH: Performance restored (lazy initialization + caching)"
