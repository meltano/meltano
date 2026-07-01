"""StateStoreManager for systemdb state backend."""

from __future__ import annotations

import sys
import typing as t
from contextlib import contextmanager

from sqlalchemy import select

from meltano.core.job_state import JobState
from meltano.core.state_store.base import MeltanoState, StateStoreManager
from meltano.core.utils import merge

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from sqlalchemy.orm import Session

    if sys.version_info >= (3, 13):
        from collections.abc import Generator
    else:
        from typing_extensions import Generator


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

    @override
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

    @override
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

    @override
    def delete(self, state_id: str) -> None:
        """Clear state for the given state_id.

        Args:
            state_id: the state_id to clear state for
        """
        if job_state := (
            self.session.query(JobState).filter(JobState.state_id == state_id).first()
        ):
            self.session.delete(job_state)
            self.session.commit()

    @override
    def clear_all(self) -> int:
        """Clear all states.

        Returns:
            The number of states cleared from the store.
        """
        count = self.session.query(JobState).delete()
        self.session.commit()
        return count

    @override
    def get_all(self, pattern: str | None = None) -> Iterator[MeltanoState]:
        """Yield all states in a memory-efficient way, optionally filtered by pattern.

        Args:
            pattern: glob-style pattern to filter by.
        """
        query = self.session.query(JobState)
        if pattern:
            like_pattern = pattern.replace("*", "%")
            query = query.filter(JobState.state_id.like(like_pattern))

        # Use yield_per so rows are fetched in bounded batches instead of all at once.
        query = query.yield_per(1000)

        return (
            MeltanoState(
                state_id=js.state_id,
                partial_state=js.partial_state,
                completed_state=js.completed_state,
            )
            for js in query
        )

    @override
    def set_all(self, states: Iterable[MeltanoState]) -> int:
        """Replace multiple states in bulk using a single transaction.

        Deletes any existing rows for the given state IDs, then inserts the
        new ones — all in one commit.

        Args:
            states: iterable of MeltanoState objects to persist
        """
        state_list = list(states)
        if not state_list:
            return 0
        state_ids = [s.state_id for s in state_list]
        self.session.query(JobState).filter(
            JobState.state_id.in_(state_ids),
        ).delete(synchronize_session=False)
        for state in state_list:
            self.session.add(
                JobState(
                    state_id=state.state_id,
                    partial_state=state.partial_state,
                    completed_state=state.completed_state,
                ),
            )
        self.session.commit()
        return len(state_list)

    @override
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

    @override
    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        *,
        retry_seconds: float = 1,
    ) -> Generator[None]:
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
