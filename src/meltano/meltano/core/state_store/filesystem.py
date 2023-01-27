"""StateStoreManagers for filesystems."""
from __future__ import annotations

import glob
import logging
import os
import re
import shutil
from abc import abstractmethod, abstractproperty
from base64 import b64decode, b64encode
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import reduce
from io import TextIOWrapper
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

from smart_open import open  # type: ignore

from meltano.core.job_state import JobState
from meltano.core.state_store.base import StateStoreManager

logger = logging.getLogger(__name__)


class InvalidStateBackendConfigurationException(Exception):
    """Occurs when state backend configuration is invalid."""


class BaseFilesystemStateStoreManager(StateStoreManager):  # noqa: WPS214
    """Base class for filesystem state backends."""

    delimiter = "/"

    def __init__(self, uri: str, lock_timeout_seconds: int, **kwargs):
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
    def is_file_not_found_error(err: Exception) -> bool:  # noqa: N805
        """Check if err is equivalent to file not being found.

        Args:
            err: the error to check
        """
        ...

    @contextmanager
    def get_reader(self, path: str) -> Iterator[TextIOWrapper]:
        """Get reader for given path.

        Args:
            path: the path to get reader for.

        Yields:
            A TextIOWrapper to read the file/blob.
        """
        if self.client:
            with open(
                self.join_path(self.uri.rstrip(self.state_dir), path),
                transport_params={"client": self.client},
            ) as reader:
                yield reader
        else:
            with open(self.join_path(self.uri.rstrip(self.state_dir), path)) as reader:
                yield reader

    @contextmanager
    def get_writer(self, path: str) -> Iterator[TextIOWrapper]:
        """Get writer for given path.

        Args:
            path: the path to get writer for.

        Yields:
            A TextIOWrapper to read the file/blob.
        """
        try:
            with open(
                self.join_path(self.uri.rstrip(self.state_dir), path),
                "w+",
                transport_params={"client": self.client} if self.client else {},
            ) as writer:
                yield writer
        except NotImplementedError:
            with open(
                self.join_path(self.uri.rstrip(self.state_dir), path),
                "w",
                transport_params={"client": self.client} if self.client else {},
            ) as writer:
                yield writer

    @abstractproperty
    def client(self):
        """Get a client for performing fs operations.

        Used for cloud backends, particularly in deleting and listing blobs.
        """
        ...

    @abstractproperty
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
        """Indicate whether or not the given state_id is currently locked.

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
                locked_at = datetime.fromtimestamp(float(reader.read()))
                if locked_at and locked_at < datetime.utcnow() - timedelta(
                    seconds=self.lock_timeout_seconds
                ):
                    self.delete(lock_path)
                    return False
                return True
        except Exception as e:
            if self.is_file_not_found_error(e):
                return False
            raise e

    def create_state_id_dir_if_not_exists(self, state_id: str):
        """Create the directory or prefix for a given state_id.

        Does nothing, but not @abstractmethod because many state backends
        will automatically create prefixes when files/blobs are created.

        Args:
            state_id: the state_id to create the dir/prefix for
        """
        ...

    @contextmanager
    def acquire_lock(self, state_id: str, retry_seconds: int = 1) -> Iterator[None]:
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
                writer.write(str(datetime.utcnow().timestamp()))
            yield
        finally:
            self.delete(lock_path)

    @abstractmethod
    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        ...

    def get(self, state_id: str) -> JobState | None:
        """Get current state for the given state_id.

        Args:
            state_id: the state_id to get state fore.

        Returns:
            Current state, if any exists, else None

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        logger.info(f"Reading state from {self.label}")
        with self.acquire_lock(state_id):
            try:
                with self.get_reader(self.get_state_path(state_id)) as reader:
                    return JobState.from_file(state_id, reader)
            except Exception as e:
                if self.is_file_not_found_error(e):
                    logger.info(f"No state found for {state_id}.")
                    return None
                raise e

    def set(self, state: JobState):
        """Set state for the given state_id.

        Args:
            state: the state to set

        Raises:
            Exception: if error not indicating file is not found is thrown
        """
        logger.info(f"Writing state to {self.label}")
        filepath = self.get_state_path(state.state_id)  # type: ignore
        with self.acquire_lock(state.state_id):  # type: ignore
            if state.is_complete():
                state_to_write = state
            else:
                try:
                    with self.get_reader(filepath) as current_state_reader:
                        current_state = JobState.from_file(
                            state.state_id, current_state_reader  # type: ignore
                        )
                        state_to_write = current_state.merge_partial(state)
                except Exception as e:
                    if self.is_file_not_found_error(e):
                        state_to_write = state
                    raise e
            with self.get_writer(filepath) as writer:
                writer.write(state_to_write.json())

    @abstractmethod
    def delete(self, file_or_dir_path: str):
        """Delete the file/blob/directory/prefix at the given path.

        Args:
            file_or_dir_path: the path to delete.
        """
        ...

    def clear(self, state_id: str):
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for.
        """
        with self.acquire_lock(state_id):
            self.delete(self.get_state_path(state_id))


class LocalFilesystemStateStoreManager(BaseFilesystemStateStoreManager):  # noqa: WPS214
    """State backend for local filesystem."""

    label: str = "Local Filesystem"

    def __init__(self, **kwargs):
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
    def client(self):
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

    def create_state_id_dir_if_not_exists(self, state_id: str):
        """Create the directory for a given state_id.

        Args:
            state_id: the state_id to create the dir for
        """
        Path(self.get_state_dir(state_id)).mkdir(parents=True, exist_ok=True)

    def get_state_ids(self, pattern: str | None = None):
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
                    os.path.join(pattern, "state.json")  # noqa: WPS509
                    if pattern
                    else os.path.join("*", "state.json"),
                )
            )
        ]

    def delete(self, file_or_dir_path: str):
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
            if self.is_file_not_found_error(e):
                pass
            else:
                raise e

    def clear(self, state_id: str):
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

    def __init__(self, **kwargs):
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

    def get_state_ids(self, pattern: str | None = None):
        """Get list of state_ids stored in the backend.

        Args:
            pattern: glob-style pattern to filter state_ids by

        Returns:
            List of state_ids
        """
        state_ids = set()
        if pattern:
            pattern_re = re.compile(pattern.replace("*", ".*"))
        for state_file in glob.glob(
            os.path.join(
                self.state_dir,
                os.path.join("*", "state.json"),
            )
        ):
            state_id = b64decode(
                os.path.basename(os.path.dirname(state_file)).encode()
            ).decode()
            if not pattern:
                state_ids.add(state_id)
            elif pattern_re.match(state_id):
                state_ids.add(state_id)
        return state_ids
