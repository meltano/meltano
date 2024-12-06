"""StateStoreManagers for filesystems."""

# ruff: noqa: PTH107, PTH118, PTH119, PTH120, PTH207

from __future__ import annotations

import glob
import os
import re
import shutil
import typing as t
from abc import abstractmethod
from base64 import b64decode, b64encode
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from functools import reduce
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

import smart_open
import structlog

from meltano.core.state_store.base import MeltanoState, StateStoreManager

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator
    from io import TextIOWrapper

logger = structlog.stdlib.get_logger(__name__)


class InvalidStateBackendConfigurationException(Exception):
    """State backend configuration is invalid."""


class BaseFilesystemStateStoreManager(StateStoreManager):
    """Base class for filesystem state backends."""

    delimiter = "/"

    def __init__(self, uri: str, lock_timeout_seconds: int, **kwargs: t.Any) -> None:
        """Initialize the BaseFilesystemStateStoreManager.

        Args:
            uri: the uri for the state backend
            lock_timeout_seconds: how many seconds a lock should be considered active
            kwargs: additional keyword args to pass to parent
        """
        super().__init__(**kwargs)
        self.uri = uri
        self.lock_timeout_seconds = lock_timeout_seconds
        self.parsed = urlparse(self.uri)

    def join_path(self, *components: str) -> str:
        """Join path components in filesystem-independent manner.

        Creates consistent paths for use in various cloud backends.

        Args:
            components: the path components to join

        Returns:
            components joined by '/'
        """
        return reduce(
            lambda comp1, comp2: f"{comp1}{comp2}"
            if (comp1.endswith(self.delimiter) or comp2.startswith(self.delimiter))
            else f"{comp1}{self.delimiter}{comp2}",
            components,
        )

    @staticmethod
    @abstractmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the error to check
        """
        ...

    @property
    def extra_transport_params(self) -> dict[str, t.Any]:
        """Extra transport params for ``smart_open.open``.

        Returns:
            The default transport params for filesystem-based backends.
        """
        return {}

    def uri_with_path(self, path: str) -> str:
        """Build uri with the given path included.

        Args:
            path: the path to join to the uri

        Returns:
            Full URI with path included
        """
        return self.join_path(self.uri.removesuffix(self.state_dir), path)

    @contextmanager
    def get_reader(self, path: str) -> Iterator[TextIOWrapper]:
        """Get reader for given path.

        Args:
            path: the path to get reader for.

        Yields:
            A TextIOWrapper to read the file/blob.
        """
        if self.client:
            with smart_open.open(
                self.uri_with_path(path),
                transport_params={
                    "client": self.client,
                    **self.extra_transport_params,
                },
            ) as reader:
                yield reader
        else:
            with smart_open.open(
                self.uri_with_path(path),
            ) as reader:
                yield reader

    @contextmanager
    def get_writer(self, path: str) -> Iterator[TextIOWrapper]:
        """Get writer for given path.

        Args:
            path: the path to get writer for.

        Yields:
            A TextIOWrapper to read the file/blob.
        """
        transport_params = {"client": self.client} if self.client else {}
        transport_params.update(self.extra_transport_params)
        try:
            with smart_open.open(
                self.uri_with_path(path),
                "w+",
                transport_params=transport_params,
            ) as writer:
                yield writer
        except NotImplementedError:
            with smart_open.open(
                self.uri_with_path(path),
                "w",
                transport_params=transport_params,
            ) as writer:
                yield writer

    @property
    @abstractmethod
    def client(self) -> t.Any:  # noqa: ANN401
        """Get a client for performing fs operations.

        Used for cloud backends, particularly in deleting and listing blobs.
        """
        ...

    @property
    @abstractmethod
    def state_dir(self) -> str:
        """Get the path (either filepath or prefix) that state should be stored at."""
        ...

    def get_path(self, state_id: str, filename: str | None = None) -> str:
        """Get the path for the given state_id and filename.

        Args:
            state_id: the state_id to get path for
            filename: the name of the file to get path for

        Returns:
            The constructed path.
        """
        return (
            self.join_path(self.state_dir, state_id, filename)
            if filename
            else self.join_path(self.state_dir, state_id)
        )

    def get_state_path(self, state_id: str) -> str:
        """Get the path to the file/blob storing complete state for the given state_id.

        Args:
            state_id: the state_id to get path for

        Returns:
            the path to the file/blob storing complete state for the given state_id.
        """
        return self.get_path(state_id, filename="state.json")

    def get_state_dir(self, state_id: str) -> str:
        """Get the path to the state directory for the given state_id.

        Args:
            state_id: the state_id to get path for

        Returns:
            The path to the directory for the given state_id.
        """
        return self.get_path(state_id)

    def get_lock_path(self, state_id: str) -> str:
        """Get the path to the lock file for the given state_id.

        Args:
            state_id: the state_id to get path for

        Returns:
            The path to the lock file for the given state_id.
        """
        return self.get_path(state_id, filename="lock")

    def is_locked(self, state_id: str) -> bool:
        """Indicate whether the given state_id is currently locked.

        Args:
            state_id: the state_id to check

        Returns:
            True if locked, else False

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        lock_path = self.get_lock_path(state_id)
        try:
            with self.get_reader(lock_path) as reader:
                locked_at = datetime.fromtimestamp(
                    float(reader.read()),
                    tz=timezone.utc,
                )
                if locked_at and locked_at < (
                    datetime.now(timezone.utc)
                    - timedelta(
                        seconds=self.lock_timeout_seconds,
                    )
                ):
                    self.delete(lock_path)
                    return False
                return True
        except Exception as e:
            if self.is_file_not_found_error(e):
                return False
            raise e

    def create_state_id_dir_if_not_exists(self, state_id: str) -> None:
        """Create the directory or prefix for a given state_id.

        Does nothing, but not @abstractmethod because many state backends
        will automatically create prefixes when files/blobs are created.

        Args:
            state_id: the state_id to create the dir/prefix for
        """

    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        retry_seconds: int = 1,
    ) -> Generator[None, None, None]:
        """Context manager for locking state_id during reads and writes.

        Args:
            state_id: the state_id to lock.
            retry_seconds: seconds to wait between retries

        Yields:
            None
        """
        lock_path = self.get_lock_path(state_id)
        try:
            self.create_state_id_dir_if_not_exists(state_id)

            while self.is_locked(state_id):
                sleep(retry_seconds)
            with self.get_writer(lock_path) as writer:
                writer.write(str(datetime.now(timezone.utc).timestamp()))
            yield
        finally:
            self.delete(lock_path)

    @abstractmethod
    def get_state_ids(self, pattern: str | None = None) -> Iterable[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        ...

    def get(self, state_id: str) -> MeltanoState | None:
        """Get current state for the given state_id.

        Args:
            state_id: the state_id to get state fore.

        Returns:
            Current state, if any exists, else None

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        logger.info(f"Reading state from {self.label}")  # noqa: G004
        with self.acquire_lock(state_id):
            try:
                with self.get_reader(self.get_state_path(state_id)) as reader:
                    return MeltanoState.from_file(state_id, reader)
            except Exception as e:
                if self.is_file_not_found_error(e):
                    logger.info(f"No state found for {state_id}.")  # noqa: G004
                    return None
                raise e

    def set(self, state: MeltanoState) -> None:
        """Set state for the given state_id.

        Args:
            state: the state to set

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        logger.info(f"Writing state to {self.label}")  # noqa: G004
        filepath = self.get_state_path(state.state_id)
        with self.acquire_lock(state.state_id):
            if state.is_complete():
                state_to_write = state
            else:
                try:
                    with self.get_reader(filepath) as current_state_reader:
                        current_state = MeltanoState.from_file(
                            state.state_id,
                            current_state_reader,
                        )
                        current_state.merge_partial(state)
                        state_to_write = current_state
                except Exception as e:
                    if self.is_file_not_found_error(e):
                        state_to_write = state
                    else:
                        raise e
            with self.get_writer(filepath) as writer:
                writer.write(state_to_write.json())

    @abstractmethod
    def delete(self, file_or_dir_path: str) -> None:
        """Delete the file/blob/directory/prefix at the given path.

        Args:
            file_or_dir_path: the path to delete.
        """
        ...

    def clear(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for.
        """
        with self.acquire_lock(state_id):
            self.delete(self.get_state_path(state_id))


class LocalFilesystemStateStoreManager(BaseFilesystemStateStoreManager):
    """State backend for local filesystem."""

    label: str = "Local Filesystem"

    def __init__(self, **kwargs: t.Any) -> None:
        """Initialize the LocalFilesystemStateStoreManager.

        Args:
            kwargs: additional kwargs to pass to parent __init__.
        """
        super().__init__(**kwargs)
        self._state_path = self.parsed.path
        Path(self._state_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_file_not_found_error(err: Exception) -> bool:
        """Check if err is equivalent to file not being found.

        Args:
            err: the err to check

        Returns:
            True if error represents file not being found, else False
        """
        return isinstance(err, FileNotFoundError)

    @property
    def client(self) -> None:
        """Get a client for performing fs operations.

        Returns:
            None
        """
        return None

    @property
    def state_dir(self) -> str:
        """Get the path that state should be stored at.

        Returns:
            The relevant path
        """
        return self._state_path

    @staticmethod
    def join_path(*components: str) -> str:
        """Join path components in filesystem-dependent manner.

        Overrides base join_path method in favor of os.path.join()

        Args:
            components: the path components to join

        Returns:
            joined path
        """
        return os.path.join(*components)

    def create_state_id_dir_if_not_exists(self, state_id: str) -> None:
        """Create the directory for a given state_id.

        Args:
            state_id: the state_id to create the dir for
        """
        Path(self.get_state_dir(state_id)).mkdir(parents=True, exist_ok=True)

    def get_state_ids(self, pattern: str | None = None) -> Iterable[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        return [
            os.path.basename(os.path.dirname(state_file))
            for state_file in glob.glob(
                os.path.join(
                    self.state_dir,
                    os.path.join(pattern, "state.json")
                    if pattern
                    else os.path.join("*", "state.json"),
                ),
            )
        ]

    def delete(self, file_or_dir_path: str) -> None:
        """Delete the file/blob/directory/prefix at the given path, if it exists.

        Args:
            file_or_dir_path: the path to delete.

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        try:
            shutil.rmtree(file_or_dir_path)
        except NotADirectoryError:
            os.remove(file_or_dir_path)
        except Exception as e:
            if not self.is_file_not_found_error(e):
                raise e

    def clear(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for.
        """
        super().clear(state_id)
        shutil.rmtree(self.get_state_dir(state_id))


class WindowsFilesystemStateStoreManager(LocalFilesystemStateStoreManager):
    """State backend for local Windows filesystem."""

    label: str = "Local Windows Filesystem"
    delimiter = "\\"

    def __init__(self, **kwargs: t.Any) -> None:
        """Initialize the LocalFilesystemStateStoreManager.

        Args:
            kwargs: additional kwargs to pass to parent __init__.
        """
        super().__init__(**kwargs)
        self._state_path = self.parsed.netloc
        Path(self._state_path).mkdir(parents=True, exist_ok=True)

    def get_path(self, state_id: str, filename: str | None = None) -> str:
        """Get the path for the given state_id and filename.

        Args:
            state_id: the state_id to get path for
            filename: the name of the file to get path for

        Returns:
            The constructed path.
        """
        state_id = b64encode(state_id.encode()).decode()
        return (
            self.join_path(self.state_dir, state_id, filename)
            if filename
            else self.join_path(self.state_dir, state_id)
        )

    def get_state_ids(self, pattern: str | None = None) -> set[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        state_ids = set()
        pattern_re = re.compile(pattern.replace("*", ".*")) if pattern else None

        for state_file in glob.glob(
            os.path.join(
                self.state_dir,
                os.path.join("*", "state.json"),
            ),
        ):
            state_id = b64decode(
                os.path.basename(os.path.dirname(state_file)).encode(),
            ).decode()
            if pattern_re is None or pattern_re.match(state_id):
                state_ids.add(state_id)
        return state_ids


class CloudStateStoreManager(BaseFilesystemStateStoreManager):
    """Base class for cloud storage state store managers."""

    def __init__(self, prefix: str | None = None, **kwargs: t.Any) -> None:
        """Initialize the CloudStateStoreManager.

        Args:
            prefix: the prefix to use for state storage
            kwargs: additional kwargs to pass to parent __init__.
        """
        super().__init__(**kwargs)
        self.prefix = prefix or self.parsed.path

    @property
    def state_dir(self) -> str:
        """Get the prefix that state should be stored at.

        Returns:
            The relevant prefix
        """
        return self.prefix.lstrip(self.delimiter).rstrip(self.delimiter)

    def uri_with_path(self, path: str) -> str:
        """Build uri with the given path included.

        Args:
            path: the path to join to the uri

        Returns:
            Full URI with path included
        """
        return self.join_path(self.uri.removesuffix(self.prefix), path)

    @abstractmethod
    def list_all_files(self, *, with_prefix: bool = True) -> Iterator[str]:
        """List all files in the backend.

        Args:
            with_prefix: Whether to include the prefix in the lookup.

        Yields:
            The next file in the backend.
        """
        ...

    @abstractmethod
    def copy_file(self, src: str, dst: str) -> None:
        """Copy a file from one location to another.

        Args:
            src: the source path
            dst: the destination path
        """
        ...

    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        if pattern:
            pattern_re = re.compile(pattern.replace("*", ".*"))
        state_ids = set()
        for filepath in self.list_all_files():
            if "/" not in filepath:
                continue

            (state_id, filename) = filepath.split("/")[-2:]
            if filename == "state.json" and (
                (not pattern) or pattern_re.match(state_id)
            ):
                state_ids.add(state_id)
        return list(state_ids)
