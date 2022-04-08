"""Manager for state that persists across runs of a BlockSet.

'State' in this module refers to _Singer_ state, which is held in a Job's
'payload' field. This is not to be confused with the Job's 'state' field,
which refers to a given job run's status, e.g. 'RUNNING' or 'FAILED'.
"""
import datetime
import json
from collections import defaultdict
from functools import singledispatchmethod
from typing import Dict, List, Optional, Union

import structlog

from meltano.core.job import Job, JobFinder, Payload, State
from meltano.core.project import Project
from meltano.core.utils import merge

logger = structlog.getLogger(__name__)


class InvalidJobStateError(Exception):
    """Occurs when invalid job state is parsed"""


class StateService:
    """Meltano Service used to manage job state.

    Currently only manages Singer state for Extract and Load jobs.
    """

    def __init__(self, session: object = None):
        """Create a StateService object.

        Args:
          session: the session to use for interacting with the db
        """
        self.session = session

    def list_state(self, job_id_pattern: Optional[str] = None) -> Dict[str, Dict]:
        """List all state found in the db.

        Args:
          job_id_pattern: An optional glob-style pattern of job_ids to search for

        Returns:
          A dict with job_ids as keys and state payloads as values.
        """
        states = defaultdict(dict)
        query = self.session.query(Job)
        if job_id_pattern:
            query = query.filter(Job.job_id.like(job_id_pattern.replace("*", "%")))
        for job in query:
            states[job.job_id] = merge(job.payload, states[job.job_id])
        return states

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

    @staticmethod
    def validate_state(state: str):
        """Check that the given state str is valid.

        Args:
          state: the state to validate

        Raises:
          InvalidJobStateError, JSONDecodeError
        """
        state_dict = json.loads(state)
        if "singer_state" not in state_dict:
            raise InvalidJobStateError(
                "singer_state not found in top level of provided state"
            )

    def add_state(self, job: Union[Job, str], new_state: Optional[str]):
        """Set state for the given Job.

        Args:
          job: either an existing Job or a job_id that future runs may look up state for.
          new_state: the state to add for the given job.
        """
        self.validate_state(new_state)
        job_to_set = self._get_or_create_job(job)
        job.payload = new_state
        if new_state:
            job.payload_flags = Payload.STATE
        else:
            job.payload_flags = 0
        job.save(self.session)

    def get_state(self, job_id: str) -> Dict:
        """Get state for job with the given job_id.

        Args:
          job_id: The job_id to get state for

        Returns:
          Dict representing state that would be used in the next run of the given job.
        """

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
            self.session,
            flags=Payload.STATE,
            since=last_job_ended_at,
            state=State.DUMMY,
        )

        for state_job in dummy_state_jobs:
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        return state

    def clear_state(self, job_id: str):
        """Clear state for Job job_id.

        Args:
          job_id: the job_id of the job to clear state for.
        """
        finder = JobFinder(job_id)
        for job in finder.get_all():
            self.set_state(job, None)
