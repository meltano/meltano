"""Manager for state that persists across runs of a BlockSet.

'State' in this module refers to _Singer_ state, which is held in a Job's
'payload' field. This is not to be confused with the Job's 'state' field,
which refers to a given job run's status, e.g. 'RUNNING' or 'FAILED'.
"""

from __future__ import annotations

import datetime
import json
import typing as t

import structlog

from meltano.core.job import Job, Payload, State
from meltano.core.job_state import SINGER_STATE_KEY
from meltano.core.project import Project
from meltano.core.state_store import (
    MeltanoState,
    state_store_manager_from_project_settings,
)

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.state_store.base import StateStoreManager

logger = structlog.getLogger(__name__)


class InvalidJobStateError(Exception):
    """Invalid job state is parsed."""


class StateService:
    """Meltano Service used to manage job state.

    Currently only manages Singer state for Extract and Load jobs.
    """

    def __init__(self, project: Project | None = None, session: Session | None = None):
        """Create a StateService object.

        Args:
            project: current meltano Project
            session: the session to use, if using SYSTEMDB state backend
        """
        self.project = project or Project.find()
        self.session = session
        self._state_store_manager: StateStoreManager | None = None

    def list_state(self, state_id_pattern: str | None = None) -> dict:
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
            now = datetime.datetime.now(datetime.timezone.utc)
            return Job(
                job_name=job,
                state=State.STATE_EDIT,
                started_at=now,
                ended_at=now,
            )

        return job

    @property
    def state_store_manager(self) -> StateStoreManager:
        """Initialize and return the correct StateStoreManager.

        Returns:
            StateStoreManager instance.
        """
        if not self._state_store_manager:
            self._state_store_manager = state_store_manager_from_project_settings(
                self.project.settings,
                self.session,
            )
        return self._state_store_manager

    @staticmethod
    def validate_state(state: dict[str, t.Any]) -> None:
        """Check that the given state str is valid.

        Args:
            state: the state to validate

        Raises:
            InvalidJobStateError: if supplied state is not valid singer state
        """
        if SINGER_STATE_KEY not in state:
            msg = f"{SINGER_STATE_KEY} not found in top level of provided state"
            raise InvalidJobStateError(msg)

    def add_state(
        self,
        job: Job | str,
        new_state: str,
        payload_flags: Payload = Payload.STATE,
        *,
        validate: bool = True,
    ) -> None:
        """Add state for the given Job.

        Args:
            job: either an existing Job or a state_id that future runs may look
                up state for.
            new_state: the state to add for the given job.
            payload_flags: the payload_flags to set for the job
            validate: whether to validate the supplied state
        """
        new_state_dict: dict = json.loads(new_state)
        if validate:
            self.validate_state(new_state_dict)
        state_to_add_to = self._get_or_create_job(job)
        state_to_add_to.payload = new_state_dict
        state_to_add_to.payload_flags = payload_flags
        state_to_add_to.save(self.session)  # type: ignore[arg-type]
        logger.debug(
            "Added to state %s state payload %s",
            state_to_add_to.job_name,
            new_state_dict,
        )
        partial_state = (
            new_state_dict if payload_flags == Payload.INCOMPLETE_STATE else {}
        )
        completed_state = new_state_dict if payload_flags == Payload.STATE else {}
        job_state = MeltanoState(
            state_id=state_to_add_to.job_name,
            partial_state=partial_state,
            completed_state=completed_state,
        )
        self.state_store_manager.update(job_state)

    def get_state(self, state_id: str) -> dict:
        """Get state for the given state_id.

        Args:
            state_id: The state_id to get state for

        Returns:
            Dict representing state that would be used in the next run.
        """
        if state := self.state_store_manager.get(state_id=state_id):
            return json.loads(state.json_merged())
        return {}

    def set_state(
        self,
        state_id: str,
        new_state: str,
        *,
        validate: bool = True,
    ) -> None:
        """Set the state for the state_id.

        Args:
            state_id: the state_id to set state for
            new_state: the state to update to
            validate: Whether to validate the supplied state.
        """
        self.add_state(
            state_id,
            new_state,
            payload_flags=Payload.STATE,
            validate=validate,
        )

    def clear_state(self, state_id: str, *, save: bool = True) -> None:  # noqa: ARG002
        """Clear the state for the state_id.

        Args:
            state_id: the state_id to clear state for
            save: Whether to immediately save the state
        """
        self.state_store_manager.clear(state_id)

    def clear_all_states(self) -> int:
        """Clear all states."""
        return self.state_store_manager.clear_all()

    def merge_state(self, state_id_src: str, state_id_dst: str) -> None:
        """Merge state from state_id_src into state_id_dst.

        Args:
            state_id_src: the state_id to get state from
            state_id_dst: the state_id_to merge state onto
        """
        self.add_state(
            state_id_dst,
            json.dumps(self.get_state(state_id_src)),
            payload_flags=Payload.INCOMPLETE_STATE,
        )

    def copy_state(self, state_id_src: str, state_id_dst: str) -> None:
        """Copy state from Job state_id_src onto Job state_id_dst.

        Args:
            state_id_src: the state_id to get state from
            state_id_dst: the state_id_to copy state onto
        """
        self.set_state(state_id_dst, json.dumps(self.get_state(state_id_src)))

    def move_state(self, state_id_src: str, state_id_dst: str) -> None:
        """Move state from Job state_id_src to Job state_id_dst.

        Args:
            state_id_src: the state_id to get state from and clear
            state_id_dst: the state_id_to move state onto
        """
        self.set_state(state_id_dst, json.dumps(self.get_state(state_id_src)))
        self.clear_state(state_id_src)
