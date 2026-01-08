#!/usr/bin/env python3
# ruff: noqa: T201, S101, BLE001, ANN201
"""Benchmark script to measure state backend initialization performance.

This script simulates the workload from the Matatika logs which shows
18 state backend initializations (9 meltano runs x 2 state checks each).

Usage:
    # On current branch (with fix)
    python benchmark_state_backend.py

    # On v3.6.0
    git checkout v3.6.0
    python benchmark_state_backend.py

    # On v3.7.9 (slow version)
    git checkout v3.7.9
    python benchmark_state_backend.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add src to path so we can import meltano
sys.path.insert(0, str(Path(__file__).parent / "src"))

from meltano.core.state_store import StateBackend


def benchmark_backends_list(iterations: int = 50) -> float:
    """Benchmark the StateBackend.backends() method.

    This simulates error message generation which calls backends()
    to list available backends.

    Args:
        iterations: Number of times to call backends()

    Returns:
        Total time in seconds
    """
    # Clear any existing cache if present
    if hasattr(StateBackend, "_backends_cache"):
        StateBackend._backends_cache = None

    start = time.time()
    for _ in range(iterations):
        backends = StateBackend.backends()
        assert "systemdb" in backends
    end = time.time()

    return end - start


def benchmark_module_import() -> float:
    """Benchmark the time to import the state_store module.

    Returns:
        Time to import in seconds
    """
    # Remove module from cache to force reimport
    if "meltano.core.state_store" in sys.modules:
        del sys.modules["meltano.core.state_store"]
    if "meltano.core.behavior.addon" in sys.modules:
        del sys.modules["meltano.core.behavior.addon"]

    start = time.time()
    from meltano.core import state_store  # noqa: F401

    end = time.time()

    return end - start


def benchmark_state_backend_creation(iterations: int = 18) -> float:
    """Benchmark creating StateBackend instances.

    This simulates the 18 state backend initializations from the logs.

    Args:
        iterations: Number of StateBackend instances to create

    Returns:
        Total time in seconds
    """
    import enum

    start = time.time()

    # Handle both v3.6.0 (enum) and v3.7+ (class) implementations
    is_enum = isinstance(StateBackend, type) and issubclass(StateBackend, enum.Enum)

    if is_enum:
        # v3.6.0 enum-based implementation
        for _ in range(iterations):
            backend = StateBackend.S3
            _ = backend.value
    else:
        # v3.7+ class-based implementation
        for _ in range(iterations):
            backend = StateBackend("s3")
            _ = backend.scheme

    end = time.time()

    return end - start


def main():
    """Run all benchmarks and print results."""
    print("=" * 70)
    print("State Backend Performance Benchmark")
    print("=" * 70)
    print()

    # Check which version we're running
    try:
        # Try to access the new lazy initialization attribute
        if hasattr(StateBackend, "_addon"):
            version_info = "Current Branch (with lazy initialization fix)"
        elif hasattr(StateBackend, "addon"):
            version_info = "v3.7.x (with addon system)"
        else:
            version_info = "v3.6.x (without addon system)"
    except Exception:
        version_info = "Unknown version"

    print(f"Version: {version_info}")
    print(f"Python: {sys.version.split()[0]}")
    print()

    # Benchmark 1: Module import time
    print("Benchmark 1: Module Import Time")
    print("-" * 70)
    import_time = benchmark_module_import()
    print(f"Import time: {import_time * 1000:.2f}ms")
    print()

    # Benchmark 2: StateBackend.backends() calls (simulates error messages)
    print("Benchmark 2: backends() Method (50 calls)")
    print("-" * 70)
    backends_time = benchmark_backends_list(50)
    print(f"Total time: {backends_time * 1000:.2f}ms")
    print(f"Average per call: {backends_time / 50 * 1000:.2f}ms")
    print()

    # Benchmark 3: StateBackend instance creation (simulates real workload)
    print("Benchmark 3: StateBackend Creation (18 instances)")
    print("-" * 70)
    creation_time = benchmark_state_backend_creation(18)
    print(f"Total time: {creation_time * 1000:.2f}ms")
    print(f"Average per instance: {creation_time / 18 * 1000:.2f}ms")
    print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    total_overhead = import_time + backends_time + creation_time
    print(f"Total overhead: {total_overhead * 1000:.2f}ms ({total_overhead:.3f}s)")
    print()

    # Extrapolation for the full workload from logs
    # 18 state backend initializations with potential backends() calls
    estimated_total = (import_time + backends_time + creation_time) * 18
    print("Estimated overhead for 18 full initializations:")
    print(f"  {estimated_total:.2f}s (~{estimated_total / 60:.2f} minutes)")
    print()

    print("Note: Actual performance difference in production depends on:")
    print("  - Number of installed packages (affects entry_points() scan)")
    print("  - Cold vs warm Python module cache")
    print("  - Disk I/O speed")
    print("  - Whether StateBackend.backends() is called (e.g., in error messages)")
    print()


if __name__ == "__main__":
    main()
