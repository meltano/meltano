"""Defines JobFinder."""

from datetime import datetime, timedelta

from .job import HEARTBEAT_VALID_MINUTES, HEARTBEATLESS_JOB_VALID_HOURS, Job, State


class JobFinder:
    """Query builder for the `Job` model for a certain `elt_uri`."""

    def __init__(self, job_id: str):
        """Initialize the JobFinder.

        Args:
            job_id: the job_id to build queries for.
        """
        self.job_id = job_id

    def latest(self, session):
        """Get the latest job for this instance's job ID.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest job for this instance's job ID
        """
        return (
            session.query(Job)
            .filter(Job.job_id == self.job_id)
            .order_by(Job.started_at.desc())
            .first()
        )

    def successful(self, session):
        """Get all successful jobs for this instance's job ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All successful jobs for this instance's job ID
        """
        return session.query(Job).filter(
            (Job.job_id == self.job_id)  # noqa: WPS465
            & (Job.state == State.SUCCESS)
            & Job.ended_at.isnot(None)
        )

    def running(self, session):
        """Find jobs in the running state.

        Args:
            session: the session to use in querying the db

        Returns:
            All runnings jobs for job_id.
        """
        return session.query(Job).filter(
            (Job.job_id == self.job_id) & (Job.state == State.RUNNING)  # noqa: WPS465
        )

    def latest_success(self, session):
        """Get the latest successful job for this instance's job ID.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest successful job for this instance's job ID
        """
        return self.successful(session).order_by(Job.ended_at.desc()).first()

    def latest_running(self, session):
        """Find the most recent job in the running state, if any.

        Args:
            session: the session to use in querying the db

        Returns:
            The latest running job for this instance's job ID
        """
        return self.running(session).order_by(Job.started_at.desc()).first()

    def with_payload(self, session, flags=0, since=None, state=None):
        """Get all jobs for this instance's job ID matching the given args.

        Args:
            session: the session to use in querying the db
            flags: only return jobs with these flags
            since: only return jobs which ended after this time
            state: only include jobs with state matching this state

        Returns:
            All jobs matching these args.
        """
        query = (
            session.query(Job)
            .filter(
                (Job.job_id == self.job_id)  # noqa: WPS465
                & (Job.payload_flags != 0)
                & (Job.payload_flags.op("&")(flags) == flags)
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
        """Return the latest job matching the given kwargs.

        Args:
            session: the session to use to query the db
            kwargs: keyword args to pass to with_payload

        Returns:
            The most recent job returned by with_payload(kwargs)
        """
        return (
            self.with_payload(session, **kwargs)
            .order_by(None)  # Reset ascending order
            .order_by(Job.ended_at.desc())
            .first()
        )

    @classmethod
    def all_stale(cls, session):
        """Return all stale jobs.

        Args:
            session: the session to use to query the db

        Returns:
            All stale jobs with any job ID
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
        """Return stale jobs with the instance's job ID.

        Args:
            session: the session to use in querying the db

        Returns:
            All stale jobs with instance's job ID
        """
        return self.all_stale(session).filter(Job.job_id == self.job_id)

    def get_all(self, session: object, since=None):
        """Return all jobs with the instance's job ID.

        Args:
            session: the session to use in querying the db
            since: only return jobs which ended after this datetime

        Returns:
            All jobs with instance's job ID which ended after 'since'
        """
        query = (
            session.query(Job)
            .filter(Job.job_id == self.job_id)
            .order_by(Job.ended_at.asc())
        )

        if since:
            query = query.filter(Job.ended_at > since)
        return query
