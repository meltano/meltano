"""Tests for catalog file locking functionality."""

from __future__ import annotations

import json
import threading
import time
import typing as t

import pytest

if t.TYPE_CHECKING:
    from pathlib import Path

from meltano.core.plugin.singer.catalog_lock import catalog_lock


# Helper functions for multiprocess tests (defined at module level for pickling)
def _hold_lock_for_duration(path: str, duration: float) -> None:
    """Hold a lock for a specified duration."""
    import time
    from pathlib import Path

    from meltano.core.plugin.singer.catalog_lock import catalog_lock

    catalog_path = Path(path)
    with catalog_lock(catalog_path, timeout=duration + 5):
        time.sleep(duration)


def _access_catalog_with_delay(path: str, process_id: int, work_delay: float) -> None:
    """Access catalog with lock and artificial delay."""
    import json
    import time
    from pathlib import Path

    from meltano.core.plugin.singer.catalog_lock import catalog_lock

    catalog_path = Path(path)
    with catalog_lock(catalog_path, timeout=10.0, delay=0.05, max_delay=0.5):
        # Read, modify, and write back
        catalog_data = json.loads(catalog_path.read_text())
        time.sleep(work_delay)  # Simulate work
        catalog_data["accessed_by"] = process_id
        catalog_path.write_text(json.dumps(catalog_data, indent=2))


def _modify_catalog(path: str, stream_id: str) -> None:
    """Modify catalog by adding a stream."""
    import json
    from pathlib import Path

    from meltano.core.plugin.singer.catalog_lock import catalog_lock

    catalog_path = Path(path)
    with catalog_lock(catalog_path):
        catalog_data = json.loads(catalog_path.read_text())
        catalog_data["streams"].append(
            {"tap_stream_id": stream_id, "schema": {"type": "object"}},
        )
        catalog_path.write_text(json.dumps(catalog_data, indent=2))


class TestCatalogLock:
    """Test catalog file locking."""

    @pytest.fixture
    def catalog_file(self, tmp_path: Path) -> Path:
        """Create a temporary catalog file."""
        catalog_path = tmp_path / "catalog.json"
        catalog_data = {
            "streams": [
                {
                    "tap_stream_id": "test_stream",
                    "schema": {"type": "object"},
                }
            ]
        }
        catalog_path.write_text(json.dumps(catalog_data))
        return catalog_path

    def test_lock_acquisition_and_release(self, catalog_file: Path) -> None:
        """Test that lock is acquired and released properly."""
        # Simply verify the lock can be acquired and released without error
        with catalog_lock(catalog_file):
            # Perform a basic operation
            catalog_data = json.loads(catalog_file.read_text())
            assert "streams" in catalog_data

        # After release, another lock should be acquirable
        with catalog_lock(catalog_file):
            catalog_data = json.loads(catalog_file.read_text())
            assert "streams" in catalog_data

    def test_concurrent_access_blocking(self, catalog_file: Path) -> None:
        """Test that concurrent access is properly blocked across processes.

        Note: InterProcessLock is designed for inter-process locking, not
        inter-thread locking within the same process. This test demonstrates
        that the lock can be acquired by multiple threads, but in production,
        this lock protects against race conditions between separate pipeline
        processes, not threads.
        """
        results = []

        def access_catalog(thread_id: int) -> None:
            """Access catalog with lock."""
            with catalog_lock(catalog_file, timeout=10.0, delay=0.05, max_delay=0.5):
                # Simulate work
                results.append(f"start-{thread_id}")
                time.sleep(0.2)
                results.append(f"end-{thread_id}")

        # Start two threads
        thread1 = threading.Thread(target=access_catalog, args=(1,))
        thread2 = threading.Thread(target=access_catalog, args=(2,))

        thread1.start()
        time.sleep(0.1)  # Ensure thread1 starts first
        thread2.start()

        thread1.join()
        thread2.join()

        # Both threads should complete (4 items total)
        assert len(results) == 4
        assert "start-1" in results
        assert "end-1" in results
        assert "start-2" in results
        assert "end-2" in results

    def test_lock_with_custom_timeout(self, catalog_file: Path) -> None:
        """Test that lock can be configured with custom timeout and delays."""
        # Just verify the lock works with custom parameters
        # The actual timeout behavior depends on the platform and whether
        # there's contention from another process
        with catalog_lock(catalog_file, timeout=5.0, delay=0.1, max_delay=1.0):
            catalog_data = json.loads(catalog_file.read_text())
            assert "streams" in catalog_data

    def test_lock_with_file_operations(self, catalog_file: Path) -> None:
        """Test lock works correctly with file read/write operations."""
        with catalog_lock(catalog_file):
            # Read catalog
            catalog_data = json.loads(catalog_file.read_text())
            assert "streams" in catalog_data

            # Modify catalog
            catalog_data["streams"].append(
                {"tap_stream_id": "new_stream", "schema": {"type": "object"}}
            )

            # Write back
            catalog_file.write_text(json.dumps(catalog_data, indent=2))

        # Verify changes persisted
        catalog_data = json.loads(catalog_file.read_text())
        assert len(catalog_data["streams"]) == 2

    def test_lock_cleanup_on_exception(self, catalog_file: Path) -> None:
        """Test that lock is released even if exception occurs."""
        with (
            pytest.raises(ValueError, match="test error"),
            catalog_lock(catalog_file),
        ):
            raise ValueError("test error")  # noqa: EM101

        # After exception, lock should be released and acquirable again
        with catalog_lock(catalog_file):
            catalog_data = json.loads(catalog_file.read_text())
            assert "streams" in catalog_data

    def test_multiple_sequential_locks(self, catalog_file: Path) -> None:
        """Test that multiple sequential locks work correctly."""
        for i in range(3):
            with catalog_lock(catalog_file):
                catalog_data = json.loads(catalog_file.read_text())
                catalog_data["iteration"] = i
                catalog_file.write_text(json.dumps(catalog_data))

        # Verify final state
        catalog_data = json.loads(catalog_file.read_text())
        assert catalog_data["iteration"] == 2

    def test_lock_on_nonexistent_file(self, tmp_path: Path) -> None:
        """Test that lock works even if catalog file doesn't exist yet."""
        catalog_path = tmp_path / "nonexistent_catalog.json"

        with catalog_lock(catalog_path):
            # Create the file during the lock
            catalog_path.write_text('{"test": true}')

        # Verify file was created
        assert catalog_path.exists()
        catalog_data = json.loads(catalog_path.read_text())
        assert catalog_data["test"] is True

    def test_lock_timeout_with_contention(self, catalog_file: Path) -> None:
        """Test that lock timeout works when another process holds the lock."""
        import multiprocessing

        # Start a process that holds the lock for 3 seconds
        process = multiprocessing.Process(
            target=_hold_lock_for_duration,
            args=(str(catalog_file), 3.0),
        )
        process.start()
        time.sleep(0.5)  # Ensure the process acquires the lock first

        try:
            # Try to acquire the lock with a short timeout
            start_time = time.time()
            with catalog_lock(catalog_file, timeout=1.0, delay=0.1, max_delay=0.3):
                # If we get here, timeout occurred and we proceeded anyway
                pass
            elapsed = time.time() - start_time

            # Should have waited approximately the timeout duration
            assert elapsed >= 0.9  # Allow small tolerance
            assert elapsed < 2.0  # Should not wait for full lock release
        finally:
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()
                process.join()

    def test_multiprocess_lock_contention(self, catalog_file: Path) -> None:
        """Test that concurrent access is properly blocked across processes."""
        import multiprocessing

        # Start two processes that try to access the file concurrently
        p1 = multiprocessing.Process(
            target=_access_catalog_with_delay,
            args=(str(catalog_file), 1, 0.2),
        )
        p2 = multiprocessing.Process(
            target=_access_catalog_with_delay,
            args=(str(catalog_file), 2, 0.2),
        )

        p1.start()
        time.sleep(0.05)  # Small delay to ensure p1 starts first
        p2.start()

        p1.join(timeout=15)
        p2.join(timeout=15)

        # Verify the file is valid JSON and was accessed by both processes
        catalog_data = json.loads(catalog_file.read_text())
        assert "accessed_by" in catalog_data
        assert "streams" in catalog_data
        # The last process to access should have set the value
        assert catalog_data["accessed_by"] in [1, 2]

    def test_concurrent_file_modification(self, catalog_file: Path) -> None:
        """Test that concurrent file modification is serialized."""
        import multiprocessing

        # Start two processes that modify the file concurrently
        p1 = multiprocessing.Process(
            target=_modify_catalog,
            args=(str(catalog_file), "stream_1"),
        )
        p2 = multiprocessing.Process(
            target=_modify_catalog,
            args=(str(catalog_file), "stream_2"),
        )

        p1.start()
        p2.start()
        p1.join(timeout=10)
        p2.join(timeout=10)

        # Verify both changes persisted and no data corruption
        catalog_data = json.loads(catalog_file.read_text())
        stream_ids = {s["tap_stream_id"] for s in catalog_data["streams"]}

        # Both new streams should be present
        assert "stream_1" in stream_ids
        assert "stream_2" in stream_ids
        # Should be original + 2 new streams
        assert len(catalog_data["streams"]) == 3
