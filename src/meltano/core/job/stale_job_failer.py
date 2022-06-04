"""Defines StaleJobFailer."""
import logging

from .finder import JobFinder

logger = logging.getLogger(__name__)


class StaleJobFailer:
    """Class that will look for stale jobs and mark them as failed."""

    def __init__(self, state_id=None):
        """Initialize stale job failer with optional state ID to filter by."""
        self.state_id = state_id

    def fail_stale_jobs(self, session):
        """Mark all stale jobs as failed."""
        for job in self._stale_jobs(session):
            self._fail_stale_job(job, session)

    def _stale_jobs(self, session):
        if self.state_id:
            return JobFinder(self.state_id).stale(session)

        return JobFinder.all_stale(session)

    def _fail_stale_job(self, job, session):
        if not job.fail_stale():
            return

        job.save(session)

        # No need to mention state ID if they're all going to be the same.
        with_state_id = "" if self.state_id else f" with state ID '{job.job_id}'"

        error = job.payload["error"]
        logger.info(
            f"Marked stale run{with_state_id} that started at {job.started_at} as failed: {error}"
        )
