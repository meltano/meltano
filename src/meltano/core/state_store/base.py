"""Storage managers for job state."""

from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod, abstractproperty

if t.TYPE_CHECKING:
    from meltano.core.job_state import JobState


class UnsupportedStateBackendURIError(Exception):
    """Provided state backend URI is not supported."""


class MissingStateBackendSettingsError(Exception):
    """Required setting values for a configured State Backend are missing."""


class StateIDLockedError(Exception):
    """A job attempted to acquire a lock on an already-locked state ID."""


class StateStoreManager(ABC):  # noqa: WPS214
    """Base state store manager."""

    def __init__(self, **kwargs):  # noqa: B027
        """Initialize state store manager.

        Args:
            kwargs: additional keyword arguments
        """

    @abstractproperty
    def label(self) -> str:
        """Get the label for the StateStoreManager."""
        ...

    @abstractmethod
    def set(self, state: JobState):
        """Set the job state for the given state_id.

        Args:
            state: the state to set.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def get(self, state_id) -> JobState | None:
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def clear(self, state_id):
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        ...

    @abstractmethod
    def get_state_ids(self, pattern=None):
        """Get all state_ids available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by
        """
        ...

    @abstractmethod
    def acquire_lock(self, state_id):
        """Acquire a naive lock for the given job's state.

        Args:
            state_id: the state_id to lock
        """
        ...

    def get_all(self) -> list[JobState]:
        """Get all state for all state_ids.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        raise NotImplementedError
