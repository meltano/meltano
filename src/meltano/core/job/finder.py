from . import Job, State
from meltano.core.db import DB


class JobFinder:
    """
    Query builder for the `Job` model for a certain `elt_uri`.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id

    def latest_success(self, session):
        return (
            session.query(Job)
            .filter(
                (Job.job_id == self.job_id)
                & (Job.state == State.SUCCESS)
                & Job.ended_at.isnot(None)
            )
            .order_by(Job.ended_at.desc())
            .first()
        )

    def latest_with_payload(self, session, flags=0):
        return (
            session.query(Job)
            .filter(
                (Job.job_id == self.job_id)
                & (Job.payload_flags != 0)
                & (Job.payload_flags.op("&")(flags) == flags)
                & Job.ended_at.isnot(None)
            )
            .order_by(Job.ended_at.desc())
            .first()
        )
