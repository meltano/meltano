"""Manager for state that persists across runs of a BlockSet.

'State' in this module refers to _Singer_ state, which is held in a Job's
'payload' field. This is not to be confused with the Job's 'state' field,
which refers to a given job run's status, e.g. 'RUNNING' or 'FAILED'.
"""
from __future__ import annotations

import datetime
import json
from typing import Any

import structlog

from meltano.core.job import Job, Payload, State
from meltano.core.job_state import SINGER_STATE_KEY
from meltano.core.state_store import DBStateStoreManager

STATE_ID_COMPONENT_DELIMITER = ":"

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

    def list_state(self, state_id_pattern: str | None = None):
        """List all state found in the db.

        Args:
            state_id_pattern: An optional glob-style pattern of state_ids to search for

        Returns:
            A dict with state_ids as keys and state payloads as values.
        """
        return {
            state_id: self.get_state(state_id)
            for state_id in self.state_store_manager.get_state_ids(state_id_pattern)
        }

    def _get_or_create_job(self, job: Job | str) -> Job:
        """If Job is passed, return it. If state_id is passed, create new and return.

        Args:
            job: either an existing Job to modify state for, or a state_id

        Raises:
            TypeError: if job is not of type Job or str

        Returns:
            A new job with given state_id, or the given Job
        """
        if isinstance(job, str):
            now = datetime.datetime.utcnow()
            return Job(
                job_name=job, state=State.STATE_EDIT, started_at=now, ended_at=now
            )
        elif isinstance(job, Job):
            return job
        raise TypeError("job must be of type Job or of type str")

    @property
    def state_store_manager(self):
        """Initialize and return the correct StateStoreManager for the given SettingsService.

        Defaults to DBStateStoreManager.

        Returns:
            StateStoreManager instance.
        """
        return DBStateStoreManager(session=self.session)

    @staticmethod
    def validate_state(state: dict[str, Any]):
        """Check that the given state str is valid.

        Args:
            state: the state to validate

        Raises:
            InvalidJobStateError: if supplied state is not valid singer state
        """
        if SINGER_STATE_KEY not in state:
            raise InvalidJobStateError(
                f"{SINGER_STATE_KEY} not found in top level of provided state"
            )

    def add_state(
        self,
        job: Job | str,
        new_state: str | None,
        payload_flags: Payload = Payload.STATE,
        validate=True,
    ):
        """Add state for the given Job.

        Args:
            job: either an existing Job or a state_id that future runs may look up state for.
            new_state: the state to add for the given job.
            payload_flags: the payload_flags to set for the job
            validate: whether to validate the supplied state
        """
        new_state_dict = json.loads(new_state)
        if validate:
            self.validate_state(new_state_dict)
        state_to_add_to = self._get_or_create_job(job)
        state_to_add_to.payload = json.loads(new_state)
        state_to_add_to.payload_flags = payload_flags
        state_to_add_to.save(self.session)
        logger.debug(
            f"Added to state {state_to_add_to.job_name} state payload {new_state_dict}"
        )
        self.state_store_manager.set(
            state_id=state_to_add_to.job_name,
            state=json.dumps(new_state_dict),
            complete=(payload_flags == Payload.STATE),
        )

    def get_state(self, state_id: str):
        """Get state for the given state_id.

        Args:
            state_id: The state_id to get state for

        Returns:
            Dict representing state that would be used in the next run.
        """
        return self.state_store_manager.get(state_id=state_id)

    def set_state(self, state_id: str, new_state: str | None, validate: bool = True):
        """Set the state for the state_id.

        Args:
            state_id: the state_id to set state for
            new_state: the state to update to
            validate: whether or not to validate the supplied state.
        """
        self.add_state(
            state_id,
            new_state,
            payload_flags=Payload.STATE,
            validate=validate,
        )

    def clear_state(self, state_id, save: bool = True):
        """Clear the state for the state_id.

        Args:
            state_id: the state_id to clear state for
            save: whether or not to immediately save the state
        """
        self.set_state(state_id, json.dumps({}), validate=False)
        self.state_store_manager.clear(state_id)

    def merge_state(self, state_id_src: str, state_id_dst: str):
        """Merge state from state_id_src into state_id_dst.

        Args:
            state_id_src: the state_id to get state from
            state_id_dst: the state_id_to merge state onto
        """
        src_state_dict = self.get_state(state_id_src)
        src_state = json.dumps(src_state_dict)
        self.add_state(state_id_dst, src_state, payload_flags=Payload.INCOMPLETE_STATE)

    def copy_state(self, state_id_src: str, state_id_dst: str):
        """Copy state from Job state_id_src onto Job state_id_dst.

        Args:
            state_id_src: the state_id to get state from
            state_id_dst: the state_id_to copy state onto
        """
        src_state_dict = self.get_state(state_id_src)
        src_state = json.dumps(src_state_dict)
        self.set_state(state_id_dst, src_state)

    def move_state(self, state_id_src: str, state_id_dst: str):
        """Move state from Job state_id_src to Job state_id_dst.

        Args:
            state_id_src: the state_id to get state from and clear
            state_id_dst: the state_id_to move state onto
        """
        src_state_dict = self.get_state(state_id_src)
        src_state = json.dumps(src_state_dict)
        self.set_state(state_id_dst, src_state)
        self.clear_state(state_id_src)
