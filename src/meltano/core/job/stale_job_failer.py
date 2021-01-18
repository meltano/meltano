"""Defines StaleJobFailer."""
import logging

from .finder import JobFinder

logger = logging.getLogger(__name__)


class StaleJobFailer:
    """Class that will look for stale jobs and mark them as failed."""

    def __init__(self, job_id=None):
        """Initialize stale job failer with optional job ID to filter by."""
        self.job_id = job_id

    def fail_stale_jobs(self, session):
        """Mark all stale jobs as failed."""
        for job in self._stale_jobs(session):
            self._fail_stale_job(job, session)

    def _stale_jobs(self, session):
        if self.job_id:
            return JobFinder(self.job_id).stale(session)

        return JobFinder.all_stale(session)

    def _fail_stale_job(self, job, session):
        if not job.fail_stale():
            return

        job.save(session)

        # No need to mention job ID if they're all going to be the same.
        with_job_id = "" if self.job_id else f" with job ID '{job.job_id}'"

        error = job.payload["error"]
        logger.info(
            f"Marked stale run{with_job_id} that started at {job.started_at} as failed: {error}"
        )
