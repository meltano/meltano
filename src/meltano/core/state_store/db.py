"""StateStoreManager for systemdb state backend."""

from __future__ import annotations

import typing as t
from contextlib import contextmanager

from sqlalchemy import select

from meltano.core.job_state import JobState
from meltano.core.state_store.base import MeltanoState, StateStoreManager
from meltano.core.utils import merge

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterator

    from sqlalchemy.orm import Session


class DBStateStoreManager(StateStoreManager):
    """StateStoreManager implementation for state stored in the system db."""

    label = "Database"

    def __init__(self, session: Session, **kwargs: t.Any):
        """Initialize the DBStateStoreManager.

        Args:
            session: the db session to use
            kwargs: optional keyword args to supply to StateStoreManager
        """
        super().__init__(**kwargs)
        self.session = session

    def set(self, state: MeltanoState) -> None:
        """Set the job state for the given state_id.

        Args:
            state: the state to set.
        """
        existing_job_state = (
            self.session.query(JobState)
            .filter(JobState.state_id == state.state_id)
            .first()
        )
        partial_state = state.partial_state
        completed_state = state.completed_state
        if existing_job_state:
            if existing_job_state.partial_state and not state.is_complete():
                partial_state = merge(
                    state.partial_state,
                    existing_job_state.partial_state,
                )
            if not state.is_complete():
                completed_state = existing_job_state.completed_state
        new_job_state = JobState(
            state_id=state.state_id,
            partial_state=partial_state,
            completed_state=completed_state,
        )
        if existing_job_state:
            self.session.delete(existing_job_state)
        self.session.add(new_job_state)
        self.session.commit()

    def get(self, state_id: str) -> MeltanoState | None:
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for

        Returns:
            The current state for the given job
        """
        if job_state := self.session.get(JobState, state_id):
            return MeltanoState(
                state_id=state_id,
                partial_state=job_state.partial_state,
                completed_state=job_state.completed_state,
            )

        return None

    def clear(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        if job_state := (
            self.session.query(JobState).filter(JobState.state_id == state_id).first()
        ):
            self.session.delete(job_state)
            self.session.commit()

    def clear_all(self) -> int:
        """Clear all states.

        Returns:
            The number of states cleared from the store.
        """
        count = self.session.query(JobState).delete()
        self.session.commit()
        return count

    def get_state_ids(self, pattern: str | None = None) -> Iterator[str]:
        """Get all state_ids available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by

        Returns:
            Generator yielding names of available jobs
        """
        if pattern:
            return (
                job_state.state_id
                for job_state in self.session.query(JobState)
                .filter(JobState.state_id.like(pattern.replace("*", "%")))
                .all()
            )
        return (
            record[0]
            for record in self.session.execute(select(JobState.state_id)).all()
        )

    @contextmanager
    def acquire_lock(
        self,
        state_id: str,  # noqa: ARG002
        *,
        retry_seconds: int = 1,  # noqa: ARG002
    ) -> Generator[None, None, None]:
        """Acquire a naive lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to lock
            retry_seconds: the number of seconds to wait before retrying
        """
        yield

    def release_lock(self, state_id: str) -> None:
        """Release the lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to unlock
        """
