from . import Job, State
from meltano.core.db import DB


class JobFinder:
    """
    Query builder for the `Job` model for a certain `elt_uri`.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id

    def latest(self, session):
        return (
            session.query(Job)
            .filter((Job.job_id == self.job_id))
            .order_by(Job.started_at.desc())
            .first()
        )

    def successful(self, session):
        return session.query(Job).filter(
            (Job.job_id == self.job_id)
            & (Job.state == State.SUCCESS)
            & Job.ended_at.isnot(None)
        )

    def latest_success(self, session):
        return self.successful(session).order_by(Job.ended_at.desc()).first()

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
