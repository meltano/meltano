"""Storage managers for job state."""
from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from meltano.core.job_state import JobState
from meltano.core.state_service import StateService
from meltano.core.utils import merge


class StateStoreManager(ABC):
    """Base state store manager."""

    def __init__(self, state_service: StateService, **kwargs):
        """Initialize state store manager.

        Args:
            state_service: StateService instance
            kwargs: additional keyword arguments
        """
        self.state_service = state_service

    @abstractmethod
    def set(self, job_name: str, state: dict, complete: bool):
        """Set the job state for the given job_name.

        Args:
            job_name: the name of the job to set state for.
            state: the state to set.
            complete: true if the state being set is for a complete run, false if partial

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, job_name):
        """Get the job state for the given job_name.

        Args:
            job_name the name of the job to get state for.

        Raises:
            NotImplementedError: always, this is an abstract method
        """
        raise NotImplementedError

    @abstractmethod
    def acquire_lock(self, job_name):
        """TODO: docstring"""
        ...

    @abstractmethod
    def release_lock(self, job_name):
        """TODO: docstring"""
        ...


class DBStateStoreManager(StateStoreManager):
    """StateStoreManager implementation for state stored in the system db."""

    def __init__(self, *args, session: Session, **kwargs):
        """TODO: docstring"""
        super().__init__(*args, **kwargs)
        self.session = session

    def set(self, job_name: str, state: dict, complete: bool) -> None:
        """Set the job state for the given job_name.

        Args:
            job_name: the name of the job to set state for.
            state: the state to set.
            complete: true if the state being set is for a complete run, false if partial
        """
        existing_job_state: JobState = (
            self.session.query(JobState).filter(JobState.job_name == job_name).first()
        )
        partial_state = state if not complete else {}
        if existing_job_state and existing_job_state.partial_state:
            partial_state = merge(partial_state, existing_job_state.partial_state)
        completed_state = state if complete else existing_job_state.completed_state
        new_job_state = JobState(
            job_name=job_name,
            partial_state=partial_state,
            completed_state=completed_state,
        )
        self.session.delete(existing_job_state)
        self.session.add(new_job_state)
        self.session.commit()

    def get(self, job_name):
        """Get the job state for the given job_name.

        Args:
            job_name the name of the job to get state for.
        """
        job_state: JobState = (
            self.session.query(JobState).filter(JobState.job_name == job_name).first()
        )
        return merge(job_state.partial_state, job_state.completed_state)
