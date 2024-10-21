"""StateStoreManager for systemdb state backend."""

from __future__ import annotations

import typing as t

from sqlalchemy import select

from meltano.core.job_state import JobState
from meltano.core.state_store.base import StateStoreManager

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session


class DBStateStoreManager(StateStoreManager):
    """StateStoreManager implementation for state stored in the system db."""

    label = "Database"

    def __init__(self, session: Session, **kwargs: t.Any) -> None:
        """Initialize the DBStateStoreManager.

        Args:
            session: the db session to use
            kwargs: optional keyword args to supply to StateStoreManager
        """
        super().__init__(**kwargs)
        self.session = session

    def _get_one(self, state_id: str) -> JobState | None:
        return self.session.get(JobState, state_id)

    def set(self, state: JobState) -> None:
        """Set the job state for the given state_id.

        Args:
            state: the state to set.
        """
        new_job_state = JobState(
            state_id=state.state_id,
            partial_state=state.partial_state,
            completed_state=state.completed_state,
        )

        if existing_job_state := self._get_one(state.state_id):
            if existing_job_state.partial_state and not state.is_complete():
                new_job_state.partial_state = existing_job_state.partial_state
                new_job_state.merge_partial(state)
            if not state.is_complete():
                new_job_state.completed_state = existing_job_state.completed_state

            self.session.delete(existing_job_state)

        self.session.add(new_job_state)
        self.session.commit()

    def get(self, state_id: str) -> JobState | None:
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for

        Returns:
            The current state for the given job
        """
        return self._get_one(state_id)

    def clear(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        if job_state := self._get_one(state_id):
            self.session.delete(job_state)
            self.session.commit()

    def get_state_ids(self, pattern: str | None = None) -> t.Iterable[str]:
        """Get all state_ids available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by

        Returns:
            Generator yielding names of available jobs
        """
        q = select(JobState.state_id)
        if pattern:
            q = q.filter(JobState.state_id.like(pattern.replace("*", "%")))

        return self.session.execute(q).scalars().all()

    def acquire_lock(self, state_id: str) -> None:
        """Acquire a naive lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to lock
        """

    def release_lock(self, state_id: str) -> None:
        """Release the lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to unlock
        """
