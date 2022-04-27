"""Manager for state that persists across runs of a BlockSet.

'State' in this module refers to _Singer_ state, which is held in a Job's
'payload' field. This is not to be confused with the Job's 'state' field,
which refers to a given job run's status, e.g. 'RUNNING' or 'FAILED'.
"""
import datetime
import json
from collections import defaultdict
from typing import Any, Dict, Optional, Union

import structlog

from meltano.core.job import Job, JobFinder, Payload, State
from meltano.core.utils import merge

logger = structlog.getLogger(__name__)


class InvalidJobStateError(Exception):
    """Occurs when invalid job state is parsed."""


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
        for job_id in {job.job_id for job in query}:  # noqa: WPS335
            states[job_id] = self.get_state(job_id)
        return states

    def _get_or_create_job(self, job: Union[Job, str]) -> Job:
        """If Job is passed, return it. If job_id is passed, create new and return.

        Args:
            job: either an existing Job to modify state for, or a job_id

        Raises:
            TypeError: if job is not of type Job or str

        Returns:
            A new job with given job_id, or the given Job
        """
        if isinstance(job, str):
            now = datetime.datetime.utcnow()
            return Job(job_id=job, state=State.STATE_EDIT, started_at=now, ended_at=now)
        elif isinstance(job, Job):
            return job
        raise TypeError("job must be of type Job or of type str")

    @staticmethod
    def validate_state(state: Dict[str, Any]):
        """Check that the given state str is valid.

        Args:
            state: the state to validate

        Raises:
            InvalidJobStateError: if supplied state is not valid singer state
        """
        if "singer_state" not in state:
            raise InvalidJobStateError(
                "singer_state not found in top level of provided state"
            )

    def add_state(
        self,
        job: Union[Job, str],
        new_state: Optional[str],
        payload_flags: Payload = Payload.STATE,
        validate=True,
    ):
        """Add state for the given Job.

        Args:
            job: either an existing Job or a job_id that future runs may look up state for.
            new_state: the state to add for the given job.
            payload_flags: the payload_flags to set for the job
            validate: whether to validate the supplied state
        """
        new_state_dict = json.loads(new_state)
        if validate:
            self.validate_state(new_state_dict)
        job_to_add_to = self._get_or_create_job(job)
        job_to_add_to.payload = json.loads(new_state)
        job_to_add_to.payload_flags = payload_flags
        job_to_add_to.save(self.session)
        logger.debug(
            f"Added to job {job_to_add_to.job_id} state payload {new_state_dict}"
        )

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

        # Get the state for the most recent completed job.
        # Do not consider dummy jobs create via add_state.
        state_job = finder.latest_with_payload(self.session, flags=Payload.STATE)
        if state_job:
            logger.info(f"Found state from {state_job.started_at}.")
            incomplete_since = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload, state)

        # If there have been any incomplete jobs since the most recent completed jobs,
        # merge the state emitted by those jobs into the state for the most recent
        # completed job. If there are no completed jobs, get the full history of
        # incomplete jobs and use the most recent state emitted per stream
        incomplete_state_jobs = finder.with_payload(
            self.session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        for incomplete_state_job in incomplete_state_jobs:
            logger.info(
                f"Found and merged incomplete state from {incomplete_state_job.started_at}."
            )
            if "singer_state" in incomplete_state_job.payload:
                merge(incomplete_state_job.payload, state)

        return state

    def set_state(self, job_id: str, new_state: Optional[str], validate: bool = True):
        """Set the state for Job job_id.

        Args:
            job_id: the job_id of the job to set state for
            new_state: the state to update to
            validate: whether or not to validate the supplied state.
        """
        self.add_state(
            job_id,
            new_state,
            payload_flags=Payload.STATE,
            validate=validate,
        )

    def clear_state(self, job_id, save: bool = True):
        """Clear the state for Job job_id.

        Args:
            job_id: the job_id of the job to clear state for
            save: whether or not to immediately save the job
        """
        self.set_state(job_id, json.dumps({}), validate=False)

    def merge_state(self, job_id_src: str, job_id_dst: str):
        """Merge state from Job job_id_src into Job job_id_dst.

        Args:
            job_id_src: the job_id to get state from
            job_id_dst: the job_id_to merge state onto
        """
        src_state_dict = self.get_state(job_id_src)
        src_state = json.dumps(src_state_dict)
        self.add_state(job_id_dst, src_state, payload_flags=Payload.INCOMPLETE_STATE)
