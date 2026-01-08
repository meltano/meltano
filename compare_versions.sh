#!/bin/bash
# Script to compare performance across different Meltano versions using uvx

set -e

echo "======================================================================"
echo "Performance Comparison Script"
echo "======================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_SCRIPT="$SCRIPT_DIR/benchmark_state_backend.py"

# Function to run benchmark with a specific Meltano version
run_benchmark() {
    local version=$1
    local label=$2

    echo "======================================================================"
    echo "Testing $label"
    echo "======================================================================"

    if [ "$version" = "current" ]; then
        echo "Using current branch with Python 3.10..."
        uv run -p 3.10 python "$BENCHMARK_SCRIPT"
    else
        echo "Installing Meltano $version with Python 3.10 via uvx..."
        uvx --with "meltano==$version" --python 3.10 python "$BENCHMARK_SCRIPT"
    fi

    echo ""
}

# Test v3.6.0
run_benchmark "3.6.0" "v3.6.0 (baseline - fast)"

# Test v3.7.9
run_benchmark "3.7.9" "v3.7.9 (regression - slow)"

# Test current branch
run_benchmark "current" "Current Branch (with fix)"

echo "======================================================================"
echo "Comparison Complete"
echo "======================================================================"
echo ""
echo "Summary:"
echo "- v3.6.0: Baseline performance (no addon system)"
echo "- v3.7.9: Performance regression (addon system without optimization)"
echo "- Current: Performance restored (lazy initialization + caching)"
