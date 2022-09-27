"""Defines JobState model class."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, Session

from meltano.core.job import JobFinder, Payload
from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import JSONEncodedDict
from meltano.core.utils import merge

SINGER_STATE_KEY = "singer_state"


class JobState(SystemModel):
    """Model class that represents the current state of a given job.

    Modified during `meltano elt` or `meltano run` runs whenever a
    STATE message is emitted by a Singer target. Also written and read
    by `meltano state` CLI invocations. Only holds the _current_ state
    for a given state_id. Full job run history is held by the Job model.
    """

    __tablename__ = "state"
    state_id = Column(types.String, unique=True, primary_key=True, nullable=False)

    updated_at = Column(types.DATETIME, onupdate=datetime.now)

    partial_state: Mapped[Any] = Column(MutableDict.as_mutable(JSONEncodedDict))
    completed_state: Mapped[Any] = Column(MutableDict.as_mutable(JSONEncodedDict))

    @classmethod
    def from_job_history(cls, session: Session, state_id: str):
        """Build JobState from job run history.

        Args:
            session: the session to use in finding job history
            state_id: state_id to build JobState for

        Returns:
            JobState built from job run history
        """
        completed_state: dict[Any, Any] = {}
        partial_state: dict[Any, Any] = {}
        incomplete_since = None
        finder = JobFinder(state_id)

        # Get the state for the most recent completed job.
        # Do not consider dummy jobs create via add_state.
        state_job = finder.latest_with_payload(session, flags=Payload.STATE)
        if state_job:
            incomplete_since = state_job.ended_at
            if SINGER_STATE_KEY in state_job.payload:
                merge(state_job.payload, partial_state)

        # If there have been any incomplete jobs since the most recent completed jobs,
        # merge the state emitted by those jobs into the state for the most recent
        # completed job. If there are no completed jobs, get the full history of
        # incomplete jobs and use the most recent state emitted per stream
        incomplete_state_jobs = finder.with_payload(
            session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        for incomplete_state_job in incomplete_state_jobs:
            if SINGER_STATE_KEY in incomplete_state_job.payload:
                partial_state = merge(incomplete_state_job.payload, partial_state)

        return cls(
            state_id=state_id,
            partial_state=partial_state,
            completed_state=completed_state,
        )
