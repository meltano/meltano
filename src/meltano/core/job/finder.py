from . import Job, State
from meltano.core.db import DB


class JobFinder:
    """
    Query builder for the `Job` model for a certain `elt_uri`.
    """

    def __init__(self, elt_uri):
        self.elt_uri = elt_uri

    def latest_success(self):
        with DB.default.session() as session:
            return (
                session.query(Job)
                .filter(
                    (Job.elt_uri == self.elt_uri)
                    & (Job.state == State.SUCCESS)
                    & Job.ended_at.isnot(None)
                )
                .order_by(Job.ended_at.desc())
                .first()
            )

    def latest_state(self):
        with DB.default.session() as session:
            return (
                session.query(Job)
                .filter(
                    (Job.elt_uri == self.elt_uri)
                    & Job.payload["singer_state"].isnot(None)
                    & Job.ended_at.isnot(None)
                )
                .order_by(Job.ended_at.desc())
                .first()
            )
