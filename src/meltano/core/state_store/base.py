"""Storage managers for job state."""

from __future__ import annotations

import dataclasses
import json
import typing as t
from abc import ABC, abstractmethod
from contextlib import contextmanager

from meltano.core.utils import merge

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable


class UnsupportedStateBackendURIError(Exception):
    """Provided state backend URI is not supported."""


class MissingStateBackendSettingsError(Exception):
    """Required setting values for a configured State Backend are missing."""


class StateIDLockedError(Exception):
    """A job attempted to acquire a lock on an already-locked state ID."""


@dataclasses.dataclass(slots=True)
class MeltanoState:
    """State object."""

    state_id: str
    partial_state: dict[str, t.Any] | None = None
    completed_state: dict[str, t.Any] | None = None

    @classmethod
    def from_json(cls, state_id: str, json_str: str) -> MeltanoState:
        """Create MeltanoState from json representation.

        Args:
            state_id: the state ID of the job to create MeltanoState for.
            json_str: the json representation of state to use.

        Returns:
            MeltanoState representing args.
        """
        state_dict = json.loads(json_str)
        return cls(
            state_id=state_id,
            completed_state=state_dict.get("completed", {}),
            partial_state=state_dict.get("partial", {}),
        )

    @classmethod
    def from_file(cls, state_id: str, file_obj: t.TextIO) -> MeltanoState:
        """Create MeltanoState from a file-like object containing state json.

        Args:
            state_id: the state_id for the MeltanoState
            file_obj: the file-like object containing state json.

        Returns:
            MeltanoState
        """
        return cls.from_json(state_id=state_id, json_str=file_obj.read())

    def json(self) -> str:
        """Get the json representation of this MeltanoState.

        Returns:
            json representation of this MeltanoState
        """
        return json.dumps(
            {"completed": self.completed_state, "partial": self.partial_state},
        )

    def json_merged(self) -> str:
        """Return the json representation of partial state merged onto complete state.

        Returns:
            json representation of partial state merged onto complete state.
        """
        return json.dumps(merge(self.partial_state, self.completed_state))

    def merge_partial(self, state: MeltanoState) -> None:
        """Merge provided partial state onto this MeltanoState.

        Args:
            state: the partial state to merge onto this state.
        """
        self.partial_state = merge(
            state.partial_state,
            self.partial_state,
        )

    def is_complete(self) -> bool:
        """Check if this MeltanoState is complete.

        Returns:
            True if complete, else False
        """
        return bool(self.completed_state)


class StateStoreManager(ABC):
    """Base state store manager."""

    def __init__(self, **kwargs: t.Any) -> None:  # noqa: B027
        """Initialize state store manager.

        Args:
            kwargs: additional keyword arguments
        """

    @t.final
    def update(self, state: MeltanoState) -> None:
        """Update state for the given `state_id`.

        If the provided state is partial, it will be merged with the existing state.

        Args:
            state: the state to set.
        """
        state_to_write = state
        with self.acquire_lock(state.state_id, retry_seconds=1):
            if not state.is_complete() and (current_state := self.get(state.state_id)):
                current_state.merge_partial(state)
                state_to_write = current_state

            self.set(state_to_write)

    @t.final
    def clear(self, state_id: str) -> None:
        """Delete the job state for the given state_id.

        Args:
            state_id: the state_id to delete.
        """
        with self.acquire_lock(state_id, retry_seconds=1):
            self.delete(state_id)

    @property
    @abstractmethod
    def label(self) -> str:
        """Get the label for the StateStoreManager."""
        ...

    @abstractmethod
    def set(self, state: MeltanoState) -> None:
        """Set the job state for the given state_id.

        Args:
            state: the state to set.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def get(self, state_id: str) -> MeltanoState | None:
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def delete(self, state_id: str) -> None:
        """Delete state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        ...

    def clear_all(self) -> int:
        """Clear all states.

        Override this method if the store supports bulk deletion.

        Returns:
            The number of states cleared from the store.
        """
        count = 0
        for state_id in self.get_state_ids("*"):
            self.clear(state_id)
            count += 1
        return count

    @abstractmethod
    def get_state_ids(self, pattern: str | None = None) -> Iterable[str]:
        """Get all state_ids available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by
        """
        ...

    @abstractmethod
    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        *,
        retry_seconds: int,
    ) -> Generator[None, None, None]:
        """Acquire a naive lock for the given job's state.

        Args:
            state_id: the state_id to lock
            retry_seconds: the number of seconds to wait before retrying
        """
        ...
