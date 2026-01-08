#!/usr/bin/env python3
# ruff: noqa: T201, S101, BLE001, ANN201
"""Benchmark script to measure state backend initialization performance.

This script simulates the actual production workload by creating StateService
instances with systemdb backend configuration, matching what happens in the
Matatika logs.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.state_service import StateService


def create_test_project() -> tuple[Project, TemporaryDirectory]:
    """Create a minimal test project with systemdb backend.

    Returns:
        Tuple of (Project, TemporaryDirectory) - keep temp dir ref
    """
    temp_dir = TemporaryDirectory()
    project_dir = Path(temp_dir.name)

    # Create minimal meltano.yml
    meltano_yml = project_dir / "meltano.yml"
    meltano_yml.write_text(
        """
version: 1
project_id: test-project
"""
    )

    # Create .meltano directory
    (project_dir / ".meltano").mkdir()

    return Project(project_dir), temp_dir


def benchmark_state_service_creation(iterations: int = 18) -> float:
    """Benchmark creating StateService instances with systemdb backend.

    This simulates the actual production workload from the logs showing
    18 "Using systemdb state backend" messages.

    Args:
        iterations: Number of StateService instances to create

    Returns:
        Total time in seconds
    """
    project, temp_dir = create_test_project()

    try:
        start = time.time()

        for _ in range(iterations):
            # This is what happens in production - create settings service
            settings_service = ProjectSettingsService(project)

            # Verify systemdb is the backend
            backend_uri = settings_service.get("state_backend.uri")
            assert backend_uri == "systemdb"

            # Create StateService - this calls state_store_manager_from_project_settings
            state_service = StateService(project)

            # Access the state store manager to ensure it's initialized
            _ = state_service.state_store_manager

        end = time.time()
        return end - start

    finally:
        temp_dir.cleanup()


def benchmark_module_import() -> float:
    """Benchmark the time to import state_store and related modules.

    In v3.7.9, the class-level addon attribute causes overhead at import time.
    In the current fix, lazy initialization eliminates this overhead.

    Returns:
        Time to import in seconds
    """
    # Remove modules from cache to force reimport
    modules_to_clear = [
        "meltano.core.state_store",
        "meltano.core.behavior.addon",
        "meltano.core.state_service",
    ]

    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]

    start = time.time()

    # Import the modules (this is what happens when Meltano starts up)
    from meltano.core import (
        state_service,  # noqa: F401
        state_store,  # noqa: F401
    )

    end = time.time()

    return end - start


def benchmark_error_path() -> float:
    """Benchmark the error path that calls backends().

    When an unknown backend is used, StateBackendNotFoundError calls backends()
    to list available backends in the error message.

    Returns:
        Total time in seconds for 10 error scenarios (or 0 if not applicable)
    """
    try:
        from meltano.core.state_store import (
            StateBackend,
            StateBackendNotFoundError,
        )
    except ImportError:
        # v3.6.0 doesn't have StateBackendNotFoundError
        return 0.0

    start = time.time()

    # Simulate error path - this calls backends() in the error message
    for _ in range(10):
        try:
            # Try to get a non-existent backend
            backend = StateBackend("nonexistent")
            _ = backend.manager
        except (StateBackendNotFoundError, Exception):  # noqa: PERF203, S110
            pass  # Expected

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
        from meltano.core.state_store import StateBackend

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
    print("Measures overhead from class-level addon initialization in v3.7.9")
    import_time = benchmark_module_import()
    print(f"Import time: {import_time * 1000:.2f}ms")
    print()

    # Benchmark 2: StateService creation with systemdb (ACTUAL PRODUCTION PATH)
    print("Benchmark 2: StateService Creation with systemdb (18 instances)")
    print("-" * 70)
    print("This simulates the actual production workload from the logs")
    state_service_time = benchmark_state_service_creation(18)
    print(f"Total time: {state_service_time * 1000:.2f}ms ({state_service_time:.3f}s)")
    print(f"Average per instance: {state_service_time / 18 * 1000:.2f}ms")
    print()

    # Benchmark 3: Error path with backends() calls
    print("Benchmark 3: Error Path - backends() calls (10 errors)")
    print("-" * 70)
    print("This tests the overhead when StateBackendNotFoundError is raised")
    error_time = benchmark_error_path()
    if error_time > 0:
        print(f"Total time: {error_time * 1000:.2f}ms")
        print(f"Average per error: {error_time / 10 * 1000:.2f}ms")
    else:
        print("Not applicable for this version (v3.6.0)")
    print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    total_overhead = import_time + state_service_time + error_time
    print(f"Total time: {total_overhead * 1000:.2f}ms ({total_overhead:.3f}s)")
    print()
    print("Key Metrics:")
    print(f"  - Module import: {import_time * 1000:.2f}ms")
    print(f"  - 18 StateService creations: {state_service_time * 1000:.2f}ms")
    print(f"  - 10 error path backends() calls: {error_time * 1000:.2f}ms")
    print()
    print("Production Impact:")
    print(
        f"  - systemdb path overhead per run: ~{state_service_time / 18 * 1000:.2f}ms"
    )
    print(f"  - If backends() called 10x: adds ~{error_time:.2f}s")
    print()


if __name__ == "__main__":
    main()
