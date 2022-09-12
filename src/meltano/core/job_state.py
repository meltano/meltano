"""Defines JobState model class."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, func, types
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Session

from meltano.core.job import JobFinder, Payload
from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import GUID, JSONEncodedDict
from meltano.core.utils import merge


class JobState(SystemModel):
    """Model class that represents the current state of a given job.

    Modified during `meltano elt` or `meltano run` runs whenever a
    STATE message is emitted by a Singer target. Also written and read
    by `meltano state` CLI invocations. Only holds the _current_ state
    for a given job_name. Full job run history is held by the Job model.
    """

    __tablename__ = "state"
    job_name = Column(types.String, unique=True, primary_key=True)

    updated_at = Column(
        types.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    partial_state = Column(MutableDict.as_mutable(JSONEncodedDict))
    completed_state = Column(MutableDict.as_mutable(JSONEncodedDict))

    @classmethod
    def from_job_history(cls, session: Session, job_name: str):
        """ """
        completed_state = {}
        partial_state = {}
        incomplete_since = None
        finder = JobFinder(job_name)

        # Get the state for the most recent completed job.
        # Do not consider dummy jobs create via add_state.
        state_job = finder.latest_with_payload(session, flags=Payload.STATE)
        if state_job:
            incomplete_since = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload, partial_state)

        # If there have been any incomplete jobs since the most recent completed jobs,
        # merge the state emitted by those jobs into the state for the most recent
        # completed job. If there are no completed jobs, get the full history of
        # incomplete jobs and use the most recent state emitted per stream
        incomplete_state_jobs = finder.with_payload(
            session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        for incomplete_state_job in incomplete_state_jobs:
            if "singer_state" in incomplete_state_job.payload:
                partial_state = merge(incomplete_state_job.payload, partial_state)

        return cls(
            job_name=job_name,
            partial_state=partial_state,
            completed_state=completed_state,
        )
