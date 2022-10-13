"""Create dedicated state table

Revision ID: 6828cc5b1a4f
Revises: 5b43800443d1
Create Date: 2022-09-26 12:47:53.512069

"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from enum import Enum

import sqlalchemy as sa
from alembic import op
import sqlalchemy
from sqlalchemy import Column, MetaData, func, types
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm.session import Session

from meltano.core.sqlalchemy import GUID, IntFlag, JSONEncodedDict
from meltano.core.utils import merge
from meltano.migrations.utils.dialect_typing import (
    get_dialect_name,
    max_string_length_for_dialect,
)

# revision identifiers, used by Alembic.
revision = "6828cc5b1a4f"
down_revision = "f4c225a9492f"
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
    state_id = Column(types.String, unique=True, primary_key=True, nullable=False)

    updated_at = Column(
        types.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    partial_state = Column(MutableDict.as_mutable(JSONEncodedDict))
    completed_state = Column(MutableDict.as_mutable(JSONEncodedDict))

    @classmethod
    def from_job_history(cls, session: Session, state_id: str):
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
        finder = JobFinder(state_id)

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
            state_id=state_id,
            partial_state=partial_state,
            completed_state=completed_state,
        )


# Copied from core/job/finder.py
class JobFinder:
    """Query builder for the `Job` model for a certain `elt_uri`."""

    def __init__(self, state_id: str):
        """Initialize the JobFinder.

        Args:
            state_id: the state_id to build queries for.
        """
        self.state_id = state_id

    def latest(self, session):
        """Get the latest state for this instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest state for this instance's state ID
        """
        return (
            session.query(Job)
            .filter(Job.job_name == self.state_id)
            .order_by(Job.started_at.desc())
            .first()
        )

    def successful(self, session):
        """Get all successful jobs for this instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All successful jobs for this instance's state ID
        """
        return session.query(Job).filter(
            (Job.job_name == self.state_id)  # noqa: WPS465
            & (Job.state == State.SUCCESS)  # noqa: WPS465
            & Job.ended_at.isnot(None)
        )

    def running(self, session):
        """Find states in the running state.

        Args:
            session: the session to use in querying the db

        Returns:
            All runnings states for state_id.
        """
        return session.query(Job).filter(
            (Job.job_name == self.state_id)  # noqa: WPS465
            & (Job.state == State.RUNNING)
        )

    def latest_success(self, session):
        """Get the latest successful state for this instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest successful state for this instance's state ID
        """
        return self.successful(session).order_by(Job.ended_at.desc()).first()

    def latest_running(self, session):
        """Find the most recent state in the running state, if any.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest running state for this instance's state ID
        """
        return self.running(session).order_by(Job.started_at.desc()).first()

    def with_payload(self, session, flags=0, since=None, state=None):
        """Get all states for this instance's state ID matching the given args.

        Args:
            session: the session to use in querying the db
            flags: only return states with these flags
            since: only return states which ended after this time
            state: only include states with state matching this state

        Returns:
            All states matching these args.
        """
        query = (
            session.query(Job)
            .filter(
                (Job.job_name == self.state_id)  # noqa: WPS465
                & (Job.payload_flags != 0)  # noqa: WPS465
                & (Job.payload_flags.op("&")(flags) == flags)  # noqa: WPS465
                & Job.ended_at.isnot(None)
            )
            .order_by(Job.ended_at.asc())
        )

        if since:
            query = query.filter(Job.ended_at > since)
        if state:
            query = query.filter(Job.state == state)
        return query

    def latest_with_payload(self, session, **kwargs):
        """Return the latest state matching the given kwargs.

        Args:
            session: the session to use to query the db
            kwargs: keyword args to pass to with_payload

        Returns:
            The most recent state returned by with_payload(kwargs)
        """
        return (
            self.with_payload(session, **kwargs)
            .order_by(None)  # Reset ascending order
            .order_by(Job.ended_at.desc())
            .first()
        )

    @classmethod
    def all_stale(cls, session):
        """Return all stale states.

        Args:
            session: the session to use to query the db

        Returns:
            All stale states with any state ID
        """
        now = datetime.utcnow()
        last_valid_heartbeat_at = now - timedelta(minutes=HEARTBEAT_VALID_MINUTES)
        last_valid_started_at = now - timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS)

        return session.query(Job).filter(
            (Job.state == State.RUNNING)  # noqa: WPS465
            & (
                (
                    Job.last_heartbeat_at.isnot(None)  # noqa: WPS465
                    & (Job.last_heartbeat_at < last_valid_heartbeat_at)
                )
                | (
                    Job.last_heartbeat_at.is_(None)  # noqa: WPS465
                    & (Job.started_at < last_valid_started_at)
                )
            )
        )

    def stale(self, session):
        """Return stale states with the instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All stale states with instance's state ID
        """
        return self.all_stale(session).filter(Job.job_name == self.state_id)

    def get_all(self, session: object, since=None):
        """Return all state with the instance's state ID.

        Args:
            session: the session to use in querying the db
            since: only return state which ended after this datetime

        Returns:
            All state with instance's state ID which ended after 'since'
        """
        query = (
            session.query(Job)
            .filter(Job.job_name == self.state_id)
            .order_by(Job.ended_at.asc())
        )

        if since:
            query = query.filter(Job.ended_at > since)
        return query


# Copied from core/job/job.py
HEARTBEATLESS_JOB_VALID_HOURS = 24
HEARTBEAT_VALID_MINUTES = 5


class State(Enum):
    """Represents status of a Job."""

    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())
    STATE_EDIT = (5, ())


class Payload(IntFlag):
    """Flag indicating whether a Job has state in its payload field."""

    STATE = 1
    INCOMPLETE_STATE = 2


class Job(SystemModel):  # noqa: WPS214
    """Model class that represents a `meltano elt` run in the system database.

    Includes State.STATE_EDIT rows which represent CLI invocations of the
    `meltano state` command which wrote state to the db. Queries that are
    meant to return only actual job runs should filter out records with
    state == State.STATE_EDIT.
    """

    __tablename__ = "runs"

    id = Column(types.Integer, primary_key=True)
    job_name = Column(types.String(1024))
    run_id = Column(GUID, nullable=False, default=uuid.uuid4)
    _state = Column(name="state", type_=types.String(10))
    started_at = Column(types.DateTime)
    last_heartbeat_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)
    trigger = Column(types.String, default="")


def upgrade():
    # Create state table
    dialect_name = get_dialect_name()
    max_string_length = max_string_length_for_dialect(dialect_name)
    conn = op.get_bind()
    inspector = sqlalchemy.inspect(conn)
    if "state" in inspector.get_table_names():
        op.drop_table("state")
    op.create_table(
        "state",
        sa.Column("state_id", sa.String(900), nullable=False),
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
            sa.types.TIMESTAMP if dialect_name == "postgresql" else sa.types.DATETIME,
            onupdate=datetime.now,
        ),
        sa.PrimaryKeyConstraint("state_id"),
        sa.UniqueConstraint("state_id"),
    )
    session = Session(bind=conn)
    for state_id in {job_run.job_name for job_run in session.query(Job).all()}:
        session.add(JobState.from_job_history(session, state_id))
    session.commit()


def downgrade():
    # Remove job_state table
    # Job run history is still maintained, so no need to copy
    op.drop_table("state")
