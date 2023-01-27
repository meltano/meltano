"""StateStoreManager for systemdb state backend."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from meltano.core.job_state import JobState
from meltano.core.state_store.base import StateStoreManager
from meltano.core.utils import merge


class DBStateStoreManager(StateStoreManager):
    """StateStoreManager implementation for state stored in the system db."""

    label = "Database"

    def __init__(self, session: Session, **kwargs):
        """Initialize the DBStateStoreManager.

        Args:
            session: the db session to use
            kwargs: optional keyword args to supply to StateStoreManager
        """
        super().__init__(**kwargs)
        self.session = session

    def set(self, state: JobState) -> None:
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
                    state.partial_state, existing_job_state.partial_state
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

    def get(self, state_id):
        """Get the job state for the given state_id.

        Args:
            state_id: the name of the job to get state for

        Returns:
            The current state for the given job
        """
        return (
            self.session.query(JobState).filter(JobState.state_id == state_id).first()
        )

    def clear(self, state_id):
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        job_state: JobState | None = (
            self.session.query(JobState).filter(JobState.state_id == state_id).first()
        )
        if job_state:
            self.session.delete(job_state)
            self.session.commit()

    def get_state_ids(self, pattern: str | None = None):
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

    def acquire_lock(self, state_id):
        """Acquire a naive lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to lock
        """
        ...  # noqa: WPS428

    def release_lock(self, state_id):
        """Release the lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            state_id: the state_id to unlock
        """
        ...  # noqa: WPS428
