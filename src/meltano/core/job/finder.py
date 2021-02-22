"""Defines JobFinder."""

from datetime import datetime, timedelta

from .job import HEARTBEAT_VALID_MINUTES, HEARTBEATLESS_JOB_VALID_HOURS, Job, State


class JobFinder:
    """
    Query builder for the `Job` model for a certain `elt_uri`.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id

    def latest(self, session):
        return (
            session.query(Job)
            .filter(Job.job_id == self.job_id)
            .order_by(Job.started_at.desc())
            .first()
        )

    def successful(self, session):
        return session.query(Job).filter(
            (Job.job_id == self.job_id)
            & (Job.state == State.SUCCESS)
            & Job.ended_at.isnot(None)
        )

    def running(self, session):
        """Find jobs in the running state."""
        return session.query(Job).filter(
            (Job.job_id == self.job_id) & (Job.state == State.RUNNING)
        )

    def latest_success(self, session):
        return self.successful(session).order_by(Job.ended_at.desc()).first()

    def latest_running(self, session):
        """Find the most recent job in the running state, if any."""
        return self.running(session).order_by(Job.started_at.desc()).first()

    def with_payload(self, session, flags=0, since=None):
        query = (
            session.query(Job)
            .filter(
                (Job.job_id == self.job_id)
                & (Job.payload_flags != 0)
                & (Job.payload_flags.op("&")(flags) == flags)
                & Job.ended_at.isnot(None)
            )
            .order_by(Job.ended_at.asc())
        )

        if since:
            query = query.filter(Job.ended_at > since)

        return query

    def latest_with_payload(self, session, **kwargs):
        return (
            self.with_payload(session, **kwargs)
            .order_by(None)  # Reset ascending order
            .order_by(Job.ended_at.desc())
            .first()
        )

    @classmethod
    def all_stale(cls, session):
        """Return all stale jobs."""
        now = datetime.utcnow()
        last_valid_heartbeat_at = now - timedelta(minutes=HEARTBEAT_VALID_MINUTES)
        last_valid_started_at = now - timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS)

        return session.query(Job).filter(
            (Job.state == State.RUNNING)
            & (
                (
                    Job.last_heartbeat_at.isnot(None)
                    & (Job.last_heartbeat_at < last_valid_heartbeat_at)
                )
                | (
                    Job.last_heartbeat_at.is_(None)
                    & (Job.started_at < last_valid_started_at)
                )
            )
        )

    def stale(self, session):
        """Return stale jobs with the instance's job ID."""
        return self.all_stale(session).filter(Job.job_id == self.job_id)
