"""Create dedicated job_state table

Revision ID: f4c225a9492f
Revises: 5b43800443d1
Create Date: 2022-09-02 09:44:05.581824

"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, MetaData, func, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm.session import Session

from meltano.core.sqlalchemy import GUID, IntFlag, JSONEncodedDict
from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "f4c225a9492f"
down_revision = "5b43800443d1"
branch_labels = None
depends_on = None


SystemMetadata = MetaData()
SystemModel = declarative_base(metadata=SystemMetadata)

# Copied from core/job_state.py
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
        """Build JobState from job run history.

        Args:
            session: the session to use in finding job history
            job_name: the name of the job to build JobState for

        Returns:
            JobState built from job run history
        """
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


# Copied from core/job/job.py
class Job(SystemModel):  # noqa: WPS214
    """Model class that represents a `meltano elt` run in the system database.

    Includes State.STATE_EDIT rows which represent CLI invocations of the
    `meltano state` command which wrote state to the db. Queries that are
    meant to return only actual job runs should filter out records with
    state == State.STATE_EDIT.
    """

    __tablename__ = "runs"

    id = Column(types.Integer, primary_key=True)
    job_name = Column(types.String)
    run_id = Column(GUID, nullable=False, default=uuid.uuid4)
    _state = Column(name="state", type_=types.String)
    started_at = Column(types.DateTime)
    last_heartbeat_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)
    trigger = Column(types.String, default="")

    @classmethod
    def from_job_history(cls, session: Session, job_name: str):
        """Build JobState from job run history.

        Args:
            session: the session to use in finding job history
            job_name: the name of the job to build JobState for

        Returns:
            JobState built from job run history
        """
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


def upgrade():
    # Create state table
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)
    op.create_table(
        "state",
        sa.Column("job_name", sa.String(max_string_length)),
        sa.Column(
            "partial_state",
            MutableDict.as_mutable(JSONEncodedDict(max_string_length)),
        ),
        sa.Column(
            "completed_state",
            MutableDict.as_mutable(JSONEncodedDict(max_string_length)),
        ),
        sa.Column(
            "updated_at",
            sa.types.TIMESTAMP,
            server_default=sa.func.now(),
            onupdate=sa.func.current_timestamp(),
        ),
        sa.PrimaryKeyConstraint("job_name"),
        sa.UniqueConstraint("job_name"),
    )

    session = Session(bind=op.get_bind())
    for job_run in session.query(Job).all():
        session.add(JobState.from_job_history(session, job_run.job_name))
    session.commit()


def downgrade():
    # Remove job_state table
    # Job run history is still maintained, so no need to copy
    op.drop_table("state")
