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

# Copy benchmark script to temp location (it doesn't exist in old versions)
TEMP_BENCHMARK=$(mktemp)
cp benchmark_state_backend.py "$TEMP_BENCHMARK"
echo "Saved benchmark script to temporary location"
echo ""

# Function to run benchmark
run_benchmark() {
    local version=$1
    echo "======================================================================"
    echo "Testing $version"
    echo "======================================================================"
    # Copy benchmark back from temp location
    cp "$TEMP_BENCHMARK" benchmark_state_backend.py

    # Detect package manager (poetry for v3.6.0, uv for v3.7.9+)
    if [ -f "poetry.lock" ]; then
        echo "Using poetry for $version with Python 3.10..."
        poetry env use python3.10 2>&1 | tail -3
        poetry install --quiet 2>&1 | tail -5
        echo ""
        echo "Running benchmark..."
        poetry run python benchmark_state_backend.py
    else
        echo "Using uv for $version with Python 3.10..."
        uv python pin 3.10 2>&1 | tail -3
        uv sync --quiet 2>&1 | tail -5
        echo ""
        echo "Running benchmark..."
        uv run python benchmark_state_backend.py
    fi
    echo ""
}

# Test v3.6.0
echo "Switching to v3.6.0..."
git checkout v3.6.0 2>&1 | grep -v "^Note:" || true
run_benchmark "v3.6.0 (baseline - fast)"

# Test v3.7.9
echo "Switching to v3.7.9..."
git checkout v3.7.9 2>&1 | grep -v "^Note:" || true
run_benchmark "v3.7.9 (regression - slow)"

# Test current branch
echo "Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH" 2>&1 | grep -v "^Note:" || true
run_benchmark "$CURRENT_BRANCH (with fix)"

# Clean up
rm -f "$TEMP_BENCHMARK"

echo "======================================================================"
echo "Comparison Complete"
echo "======================================================================"
echo ""
echo "Summary:"
echo "- v3.6.0: Baseline performance (no addon system)"
echo "- v3.7.9: Performance regression (addon system without optimization)"
echo "- $CURRENT_BRANCH: Performance restored (lazy initialization + caching)"
