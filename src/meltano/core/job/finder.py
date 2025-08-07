"""Defines JobFinder (will be renamed to StateFinder)."""

from __future__ import annotations

import typing as t
from datetime import datetime, timedelta, timezone

from .job import HEARTBEAT_VALID_MINUTES, HEARTBEATLESS_JOB_VALID_HOURS, Job, State

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Query, Session


class JobFinder:
    """Query builder for the `Job` model for a certain `elt_uri`."""

    def __init__(self, state_id: str) -> None:
        """Initialize the JobFinder.

        Args:
            state_id: the state_id to build queries for.
        """
        self.state_id = state_id

    def latest(self, session: Session) -> Job | None:
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

    def successful(self, session: Session) -> Query[Job]:
        """Get all successful jobs for this instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All successful jobs for this instance's state ID
        """
        return session.query(Job).filter(
            (Job.job_name == self.state_id)
            & (Job.state == State.SUCCESS)
            & Job.ended_at.isnot(None),
        )

    def running(self, session: Session) -> Query[Job]:
        """Find states in the running state.

        Args:
            session: the session to use in querying the db

        Returns:
            All runnings states for state_id.
        """
        return session.query(Job).filter(
            (Job.job_name == self.state_id) & (Job.state == State.RUNNING),
        )

    def latest_success(self, session: Session) -> Job | None:
        """Get the latest successful state for this instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest successful state for this instance's state ID
        """
        return self.successful(session).order_by(Job.ended_at.desc()).first()

    def latest_running(self, session: Session) -> Job | None:
        """Find the most recent state in the running state, if any.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest running state for this instance's state ID
        """
        return self.running(session).order_by(Job.started_at.desc()).first()

    def with_payload(
        self,
        session: Session,
        flags: int = 0,
        since: datetime | None = None,
        state: State | None = None,
    ) -> Query[Job]:
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
                (Job.job_name == self.state_id)
                & (Job.payload_flags != 0)
                & (Job.payload_flags.op("&")(flags) == flags)
                & Job.ended_at.isnot(None),
            )
            .order_by(Job.ended_at.asc())
        )

        if since:
            query = query.filter(Job.ended_at > since)
        if state:
            query = query.filter(Job.state == state)  # type: ignore[arg-type]
        return query

    def latest_with_payload(self, session: Session, **kwargs: t.Any) -> Job | None:
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
    def all_stale(cls, session: Session) -> Query[Job]:
        """Return all stale states.

        Args:
            session: the session to use to query the db

        Returns:
            All stale states with any state ID
        """
        now = datetime.now(tz=timezone.utc)
        last_valid_heartbeat_at = now - timedelta(minutes=HEARTBEAT_VALID_MINUTES)
        last_valid_started_at = now - timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS)

        return session.query(Job).filter(
            (Job.state == State.RUNNING)  # type: ignore[operator]
            & (
                (
                    Job.last_heartbeat_at.isnot(None)
                    & (Job.last_heartbeat_at < last_valid_heartbeat_at)
                )
                | (
                    Job.last_heartbeat_at.is_(None)
                    & (Job.started_at < last_valid_started_at)
                )
            ),
        )

    def stale(self, session: Session) -> Query[Job]:
        """Return stale states with the instance's state ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All stale states with instance's state ID
        """
        return self.all_stale(session).filter(Job.job_name == self.state_id)

    def get_all(self, session: Session, since: datetime | None = None) -> Query[Job]:
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
