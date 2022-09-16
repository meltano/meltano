"""Storage managers for job state."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session

from meltano.core.job_state import JobState
from meltano.core.utils import merge


class StateStoreManager(ABC):
    """Base state store manager."""

    def __init__(self, **kwargs):
        """Initialize state store manager.

        Args:
            kwargs: additional keyword arguments
        """
        ...

    @abstractmethod
    def set(self, job_name: str, state: str, complete: bool):
        """Set the job state for the given job_name.

        Args:
            job_name: the name of the job to set state for.
            state: the state to set.
            complete: true if the state being set is for a complete run, false if partial

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def get(self, job_name):
        """Get the job state for the given job_name.

        Args:
            job_name: the name of the job to get state for.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        ...

    @abstractmethod
    def clear(self, job_name):
        """Clear state for the given job_name.

        Args:
            job_name: the job name to clear state for
        """
        ...

    @abstractmethod
    def get_job_names(self, pattern=None):
        """Get all job names available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by
        """
        ...

    @abstractmethod
    def acquire_lock(self, job_name):
        """Acquire a naive lock for the given job's state.

        Args:
            job_name: the job name to lock
        """
        ...

    @abstractmethod
    def release_lock(self, job_name):
        """Release lock for given job's state.

        Args:
            job_name: the job name to unlock
        """
        ...


class DBStateStoreManager(StateStoreManager):
    """StateStoreManager implementation for state stored in the system db."""

    def __init__(self, *args, session: Session, **kwargs):
        """Initialize the DBStateStoreManager.

        Args:
            args: optional positional args to supply to StateStoreManager
            session: the db session to use
            kwargs: optional keyword args to supply to StateStoreManager
        """
        super().__init__(*args, **kwargs)
        self.session = session

    def set(self, job_name: str, state: str, complete: bool) -> None:
        """Set the job state for the given job_name.

        Args:
            job_name: the name of the job to set state for.
            state: the state to set.
            complete: true if the state being set is for a complete run, false if partial
        """
        existing_job_state = (
            self.session.query(JobState).filter(JobState.job_name == job_name).first()
        )
        partial_state = {} if complete else json.loads(state)
        completed_state = json.loads(state) if complete else {}
        if existing_job_state:
            if existing_job_state.partial_state and not complete:
                partial_state = merge(partial_state, existing_job_state.partial_state)
            if not complete:
                completed_state = existing_job_state.completed_state
        new_job_state = JobState(
            job_name=job_name,
            partial_state=partial_state,
            completed_state=completed_state,
        )
        if existing_job_state:
            self.session.delete(existing_job_state)
        self.session.add(new_job_state)
        self.session.commit()

    def get(self, job_name):
        """Get the job state for the given job_name.

        Args:
            job_name: the name of the job to get state for

        Returns:
            The current state for the given job
        """
        job_state: JobState | None = (
            self.session.query(JobState).filter(JobState.job_name == job_name).first()
        )
        return (
            merge(job_state.partial_state, job_state.completed_state)
            if job_state
            else {}
        )

    def clear(self, job_name):
        """Clear state for the given job_name.

        Args:
            job_name: the job name to clear state for
        """
        job_state: JobState | None = (
            self.session.query(JobState).filter(JobState.job_name == job_name).first()
        )
        if job_state:
            self.session.delete(job_state)
            self.session.commit()

    def get_job_names(self, pattern: str | None = None):
        """Get all job names available in this state store manager.

        Args:
            pattern: glob-style pattern to filter by

        Returns:
            Generator yielding names of available jobs
        """
        if pattern:
            return (
                job_state.job_name
                for job_state in self.session.query(JobState)
                .filter(JobState.job_name.like(pattern.replace("*", "%")))
                .all()
            )
        return (
            record[0]
            for record in self.session.execute(select(JobState.job_name)).all()
        )

    def acquire_lock(self, job_name):
        """Acquire a naive lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            job_name: the job name to lock
        """
        ...

    def release_lock(self, job_name):
        """Release the lock for the given job's state.

        For DBStateStoreManager, the db manages transactions.
        This does nothing.

        Args:
            job_name: the job name to unlock
        """
        ...
