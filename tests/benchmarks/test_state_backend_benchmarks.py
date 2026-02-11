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
        subject.update(state)

    @pytest.mark.benchmark
    def test_local_filesystem_update_partial_state(
        self,
        subject: _LocalFilesystemStateStoreManager,
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
        subject.update(state)

    @pytest.mark.benchmark
    def test_local_filesystem_repeated_updates_complete_state(
        self,
        subject: _LocalFilesystemStateStoreManager,
    ) -> None:
        """Benchmark 50 update() calls with complete state.

        Simulates frequent STATE messages during a normal ELT run.
        With optimization, this should be fast (no locking overhead).
        """
        for i in range(50):
            state = MeltanoState(
                state_id="test-repeated",
                partial_state={},
                completed_state={"singer_state": {"bookmark": i}},
            )
            subject.update(state)

    @pytest.mark.benchmark
    def test_local_filesystem_repeated_updates_partial_state(
        self,
        subject: _LocalFilesystemStateStoreManager,
    ) -> None:
        """Benchmark repeated update() calls with partial state (locking path).

        This stresses the locking-heavy code path by issuing many partial-state
        updates with no completed_state payload, so we can compare against the
        optimized complete-state path under similar load.
        """
        for i in range(50):
            state = MeltanoState(
                state_id="test-partial-repeated",
                partial_state={"singer_state": {"bookmark": i}},
                completed_state={},
            )
            subject.update(state)
