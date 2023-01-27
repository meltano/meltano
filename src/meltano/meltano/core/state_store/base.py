"""Storage managers for job state."""
from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty

from meltano.core.job_state import JobState


class UnsupportedStateBackendURIError(Exception):
    """Occurs when a provided state backend URI is not supported."""


class MissingStateBackendSettingsError(Exception):
    """Occurs when required setting values for a configured State Backend are missing from the Meltano project."""


class StateIDLockedError(Exception):
    """Occurs whan a job attempts to acquire a lock on an already-locked state ID."""


class StateStoreManager(ABC):
    """Base state store manager."""

    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize state store manager.

        Args:
            kwargs: additional keyword arguments
        """
        ...

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
