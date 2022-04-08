"""Manager for state that persists across runs of a StatefulBlockSet"""
import datetime
from functools import singledispatchmethod
from typing import Dict, List, Optional, Union

from meltano.core.job import Job, JobFinder, Payload, State
from meltano.core.project import Project


class StateService:
    """Meltano Service used to manage BlockSet State.

    Currently only manages Singer state for Extract and Load jobs.
    """

    def __init__(self, session: object = None):
        self.session = session

    def list_state(job_id_pattern: Optional[str] = None) -> List[Dict]:
        """List all state found in the db.

        Args:
          job_id_pattern:

        Returns:

        """

        NotImplemented

    @singledispatchmethod
    def _get_or_create_job(self, job: Union[Job, str]) -> Job:
        """If Job is passed, return it. If job_id is passed, create new and return.

        Args:
          job: either an existing Job to modify state for, or a job_id

        Returns:
          the Job
        """
        raise TypeError(f"job must be of type Job or of type str")

    @_get_or_create_job.register
    def _(self, job: Job) -> Job:
        return job

    @_get_or_create_job.register
    def _(self, job: str) -> Job:
        now = datetime.utcnow()
        return Job(job_id=job, state=State.DUMMY, started_at=now, ended_at=now)

    def set_state(self, job: Union[Job, str], new_state: Optional[str]):
        """Set state for the given Job

        Args:
          job:
          new_state:
        """
        job_to_set = self._get_or_create_job(job)
        job.payload = new_state
        if new_state:
            job.payload_flags = Payload.STATE
        else:
            job.payload_flags = 0
        job.save(self.session)

    def get_state(self, job_id: str) -> str:
        """Get state for the given job."""

        state = {}
        incomplete_since = None
        finder = JobFinder(job_id)

        state_job = finder.latest_with_payload(self.session, flags=Payload.STATE)
        if state_job:
            logger.info(f"Found state from {state_job.started_at}.")
            incomplete_since = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        incomplete_state_jobs = finder.with_payload(
            self.session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        last_job_ended_at = incomplete_since
        for state_job in incomplete_state_jobs:
            logger.info(
                f"Found and merged incomplete state from {state_job.started_at}."
            )
            last_job_ended_at = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        dummy_state_jobs = finder.with_payload(
            self.session, flags=Payload.DUMMY_STATE, since=last_job_ended_at
        )

        for state_job in dummy_state_jobs:
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        return state

    def clear_state(self, job_id: str):
        """Clear state for Job job_id.

        Args:
          job_id:
        """
        finder = JobFinder(job_id)
        for job in finder.get_all():
            self.set_state(job, None)
