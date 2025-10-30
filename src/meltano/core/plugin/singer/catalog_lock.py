"""Catalog file locking utilities to prevent race conditions."""

from __future__ import annotations

import typing as t
from contextlib import contextmanager

import structlog
from fasteners import InterProcessLock

if t.TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

logger = structlog.stdlib.get_logger(__name__)


@contextmanager
def catalog_lock(
    catalog_path: Path,
    *,
    timeout: float = 60.0,
    delay: float = 0.05,
    max_delay: float = 5.0,
) -> Generator[None, None, None]:
    """Acquire a lock on the catalog file to prevent concurrent access.

    This prevents race conditions when multiple pipelines using the same
    extractor try to read/write the catalog file simultaneously.

    Args:
        catalog_path: Path to the catalog file to lock.
        timeout: Maximum time in seconds to wait for the lock. After this
            time, the lock is ignored and execution continues. Defaults to 60s.
        delay: Starting delay between retry attempts in seconds. Defaults to 0.05s.
        max_delay: Maximum delay between retry attempts in seconds. Defaults to 5s.

    Yields:
        None - The lock is held during the context manager execution.

    Example:
        >>> with catalog_lock(catalog_path):
        ...     # Perform catalog operations safely
        ...     catalog = json.loads(catalog_path.read_text())
    """
    lock_path = catalog_path.with_suffix(f"{catalog_path.suffix}.lock")
    lock = InterProcessLock(str(lock_path))

    # Use fasteners' built-in retry logic
    lock_acquired = lock.acquire(
        blocking=True,
        timeout=timeout,
        delay=delay,
        max_delay=max_delay,
    )

    if lock_acquired:
        logger.debug(
            "Acquired catalog lock",
            catalog_path=catalog_path,
            lock_path=lock_path,
        )
    else:
        logger.warning(
            "Catalog lock timeout exceeded, proceeding without lock",
            catalog_path=catalog_path,
            timeout=timeout,
        )

    try:
        yield
    finally:
        if lock_acquired:
            lock.release()
            logger.debug(
                "Released catalog lock",
                catalog_path=catalog_path,
                lock_path=lock_path,
            )
            # Note: We don't delete the lock file here to avoid racing with
            # other processes. The fasteners library manages the lock file
            # lifecycle.
