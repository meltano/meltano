"""Benchmarks for state backend operations.

These benchmarks verify the optimization that skips locking for complete states
(the common case during normal ELT runs), while still locking for partial states
that require read-merge-write atomicity.

See: https://github.com/meltano/meltano/pull/8367
"""

from __future__ import annotations

import platform
import shutil
import typing as t

import pytest

from meltano.core.state_store import MeltanoState
from meltano.core.state_store.filesystem import (
    _LocalFilesystemStateStoreManager,
    _WindowsFilesystemStateStoreManager,
)

if t.TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from pytest_codspeed import BenchmarkFixture


def on_windows() -> bool:
    return "Windows" in platform.system()


class TestStateBackendBenchmarks:
    """Benchmarks for state backend update operations."""

    @pytest.fixture
    def subject(self, tmp_path: Path) -> Generator[_LocalFilesystemStateStoreManager]:
        """Create a filesystem state store manager."""
        state_path = tmp_path / ".meltano" / "state"
        state_path.mkdir(parents=True, exist_ok=True)

        if on_windows():
            yield _WindowsFilesystemStateStoreManager(
                uri=f"file://{state_path}\\",
                lock_timeout_seconds=10,
            )
        else:
            yield _LocalFilesystemStateStoreManager(
                uri=f"file://{state_path}/",
                lock_timeout_seconds=10,
            )
        shutil.rmtree(state_path, ignore_errors=True)

    @pytest.mark.benchmark
    def test_local_filesystem_update_complete_state(
        self,
        subject: _LocalFilesystemStateStoreManager,
        benchmark: BenchmarkFixture,
    ) -> None:
        """Benchmark update() with complete state (optimized path, no locking).

        This is the common case during normal ELT runs. Complete states
        skip the locking overhead entirely.
        """
        state = MeltanoState(
            state_id="test-complete",
            partial_state={},
            completed_state={"singer_state": {"bookmark": 1}},
        )

        def do_update() -> None:
            subject.update(state)

        benchmark(do_update)

    @pytest.mark.benchmark
    def test_local_filesystem_update_partial_state(
        self,
        subject: _LocalFilesystemStateStoreManager,
        benchmark: BenchmarkFixture,
    ) -> None:
        """Benchmark update() with partial state (requires locking).

        Partial states require locking for read-merge-write atomicity.
        This path is only used when state_strategy=merge.
        """
        state = MeltanoState(
            state_id="test-partial",
            partial_state={"singer_state": {"bookmark": 1}},
            completed_state={},
        )

        def do_update() -> None:
            subject.update(state)

        benchmark(do_update)
