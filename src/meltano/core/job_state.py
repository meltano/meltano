"""Defines JobState model class."""

from __future__ import annotations

import json
import typing as t
from datetime import datetime

from sqlalchemy.orm import Mapped, Session, mapped_column

from meltano.core.job import JobFinder, Payload
from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import StateType  # noqa: TCH001
from meltano.core.utils import merge

if t.TYPE_CHECKING:
    from io import TextIOWrapper


SINGER_STATE_KEY = "singer_state"
STATE_ID_COMPONENT_DELIMITER = ":"


class JobState(SystemModel):
    """Model class that represents the current state of a given job.

    Modified during `meltano elt` or `meltano run` runs whenever a
    STATE message is emitted by a Singer target. Also written and read
    by `meltano state` CLI invocations. Only holds the _current_ state
    for a given state_id. Full job run history is held by the Job model.
    """

    __tablename__ = "state"
    state_id: Mapped[str] = mapped_column(unique=True, primary_key=True)

    updated_at: Mapped[t.Optional[datetime]] = mapped_column(  # noqa: UP007
        onupdate=datetime.now,
    )

    partial_state: Mapped[t.Optional[StateType]]  # noqa: UP007
    completed_state: Mapped[t.Optional[StateType]]  # noqa: UP007

    def __eq__(self, other: object) -> bool:
        """Check equality with another JobState.

        Does not take into account updated_at;
        merely checks equality of state_id and partial and completed state.

        Args:
            other: the other JobState to check against

        Returns:
            True if other is equal to this JobState, else False
        """
        if not isinstance(other, JobState):
            return NotImplemented
        return (
            (self.state_id == other.state_id)
            and (self.partial_state == other.partial_state)
            and (self.completed_state == other.completed_state)
        )

    @classmethod
    def from_job_history(cls, session: Session, state_id: str):  # noqa: ANN206
        """Build JobState from job run history.

        Args:
            session: the session to use in finding job history
            state_id: state_id to build JobState for

        Returns:
            JobState built from job run history
        """
        completed_state: dict[t.Any, t.Any] = {}
        partial_state: dict[t.Any, t.Any] = {}
        incomplete_since = None
        finder = JobFinder(state_id)

        # Get the state for the most recent completed job.
        # Do not consider dummy jobs create via add_state.
        if state_job := finder.latest_with_payload(session, flags=Payload.STATE):
            incomplete_since = state_job.ended_at
            if SINGER_STATE_KEY in state_job.payload:
                merge(state_job.payload, partial_state)

        # If there have been any incomplete jobs since the most recent completed jobs,
        # merge the state emitted by those jobs into the state for the most recent
        # completed job. If there are no completed jobs, get the full history of
        # incomplete jobs and use the most recent state emitted per stream
        incomplete_state_jobs = finder.with_payload(
            session,
            flags=Payload.INCOMPLETE_STATE,
            since=incomplete_since,
        )
        for incomplete_state_job in incomplete_state_jobs:
            if SINGER_STATE_KEY in incomplete_state_job.payload:
                partial_state = merge(incomplete_state_job.payload, partial_state)

        return cls(
            state_id=state_id,
            partial_state=partial_state,
            completed_state=completed_state,
        )

    @classmethod
    def from_json(cls, state_id: str, json_str: str) -> JobState:
        """Create JobState from json representation.

        Args:
            state_id: the state ID of the job to create JobState for.
            json_str: the json representation of state to use.

        Returns:
            JobState representing args.
        """
        state_dict = json.loads(json_str)
        return cls(
            state_id=state_id,
            completed_state=state_dict.get("completed", {}),
            partial_state=state_dict.get("partial", {}),
        )

    def json(self) -> str:
        """Get the json representation of this JobState.

        Returns:
            json representation of this JobState
        """
        return json.dumps(
            {"completed": self.completed_state, "partial": self.partial_state},
        )

    def json_merged(self) -> str:
        """Return the json representation of partial state merged onto complete state.

        Returns:
            json representation of partial state merged onto complete state.
        """
        return json.dumps(merge(self.partial_state, self.completed_state))

    @classmethod
    def from_file(cls, state_id: str, file_obj: TextIOWrapper) -> JobState:
        """Create JobState from a file-like object containing state json.

        Args:
            state_id: the state_id for the JobState
            file_obj: the file-like object containing state json.

        Returns:
            JobState
        """
        return cls.from_json(state_id=state_id, json_str=file_obj.read())

    def merge_partial(
        self,
        state: JobState,
    ) -> None:
        """Merge provided partial state onto this JobState.

        Args:
            state: the partial state to merge onto this state.
        """
        self.partial_state = merge(
            state.partial_state,
            self.partial_state,
        )

    def is_complete(self) -> bool:
        """Check if this JobState is complete.

        Returns:
            True if complete, else False
        """
        return bool(self.completed_state)

    def to_file(self, file_obj: TextIOWrapper) -> None:
        """Persist JobState to a file-like object.

        Args:
            file_obj: the file-like object to write to.
        """
        file_obj.write(self.json())
