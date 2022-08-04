"""Defines Job model class."""
from __future__ import annotations

import asyncio
import os
import signal
import uuid
from contextlib import asynccontextmanager, contextmanager, suppress
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import Column, literal, types
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from meltano.core.error import Error
from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import GUID, IntFlag, JSONEncodedDict

HEARTBEATLESS_JOB_VALID_HOURS = 24
HEARTBEAT_VALID_MINUTES = 5


class InconsistentStateError(Error):
    """Occur upon a wrong operation for the current state."""


class ImpossibleTransitionError(Error):
    """Occur upon a wrong transition."""


class State(Enum):
    """Represents status of a Job."""

    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())
    STATE_EDIT = (5, ())

    def transitions(self):
        """Get possible next States for a job of this State.

        Returns:
            The possible states jobs in this state can be transitioned into
        """
        return self.value[1]

    def __str__(self):
        """Get a string representation of this State.

        Returns:
            the name of this State
        """
        return self.name


class StateComparator(Comparator):
    """Compare Job._state to State enums."""

    def __eq__(self, other):
        """Enable SQLAlchemy to directly compare Job.state values with State.

        Args:
            other: the State enum to compare to

        Returns:
            Comparison between __clause_element__ and SQLAlchemy literal for State name
        """
        return self.__clause_element__() == literal(other.name)


def current_trigger():
    """Get the trigger for running job.

    Returns:
        The trigger for currently running job
    """
    return os.getenv("MELTANO_JOB_TRIGGER")


class Payload(IntFlag):
    """Flag indicating whether a Job has state in its payload field."""

    STATE = 1
    INCOMPLETE_STATE = 2


class Job(SystemModel):  # noqa: WPS214
    """Model class that represents a `meltano elt` run in the system database.

    Includes State.STATE_EDIT rows which represent CLI invocations of the
    `meltano state` command which wrote state to the db. Queries that are
    meant to return only actual job runs should filter out records with
    state == State.STATE_EDIT.
    """

    __tablename__ = "runs"

    id = Column(types.Integer, primary_key=True)
    job_name = Column(types.String)
    run_id = Column(GUID, nullable=False, default=uuid.uuid4)
    _state = Column(name="state", type_=types.String)
    started_at = Column(types.DateTime)
    last_heartbeat_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)
    trigger = Column(types.String, default=current_trigger)

    def __init__(self, **kwargs):
        """Construct a Job.

        Args:
            kwargs: keyword args to override defaults and pass to super
        """
        kwargs["_state"] = kwargs.pop("state", State.IDLE).name
        kwargs["payload"] = kwargs.get("payload", {})
        kwargs["run_id"] = kwargs.get("run_id", uuid.uuid4())
        super().__init__(**kwargs)

    @hybrid_property
    def state(self) -> State:
        """Get the job state as a State enum.

        Returns:
            State enum matching string value for this job state
        """
        return State[self._state]

    @state.setter
    def state(self, value):
        """Set the _state value for this Job from a State enum.

        Args:
            value: the State enum to use.
        """
        self._state = str(value)

    @state.comparator
    def state(cls):  # noqa: N805
        """Use this comparison to compare Job.state to State.

        See:
            https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html#building-custom-comparators

        Returns:
            Result of comparison
        """
        return StateComparator(cls._state)

    def is_running(self):
        """Return whether Job is running.

        Returns:
            bool indicating whether this Job is running
        """
        return self.state is State.RUNNING

    def is_stale(self):
        """Return whether Job has gone stale.

        Running jobs with a heartbeat are considered stale after no heartbeat is recorded for 5 minutes.
        Legacy jobs without a heartbeat are considered stale after being in the running state for 24 hours.

        Returns:
            bool indicating whether this Job is stale
        """
        if not self.is_running():
            return False

        if self.last_heartbeat_at:
            timestamp = self.last_heartbeat_at
            valid_for = timedelta(minutes=HEARTBEAT_VALID_MINUTES)
        else:
            timestamp = self.started_at
            valid_for = timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS)

        return datetime.utcnow() - timestamp > valid_for

    def has_error(self):
        """Return whether a job has failed.

        Returns:
            bool indicating whether this Job has failed
        """
        return self.state is State.FAIL

    def is_complete(self):
        """Return whether a job has completed.

        Returns:
            bool indicating whether this job has completed
        """
        return self.state in {State.SUCCESS, State.FAIL}

    def is_success(self):
        """Return whether a job has succeeded.

        Returns:
            a bool indicating whether this job has succeeded
        """
        return self.state is State.SUCCESS

    def can_transit(self, state: State) -> bool:
        """Return whether this job can transit into the given state.

        Args:
            state: the state to check against

        Returns:
            bool indicating whether the given state is transitable from this job's state
        """
        if self.state is state:
            return True

        return state.name in self.state.transitions()

    def transit(self, state: State) -> (State, State):
        """Transition this job into the given state.

        Args:
            state: the state to transition this job to

        Returns:
            a tuple with the original state and the new state

        Raises:
            ImpossibleTransitionError: when this job cannot transition into the given state
        """
        transition = (self.state, state)

        if not self.can_transit(state):
            raise ImpossibleTransitionError(transition)

        if self.state is state:
            return transition

        self.state = state

        return transition

    @asynccontextmanager
    async def run(self, session):
        """Run wrapped code in context of a job.

        Transitions state to RUNNING and SUCCESS/FAIL as appropriate and records heartbeat every second.

        Args:
            session: the session to use for writing to the db

        Raises:
            BaseException: re-raises an exception occurring in the job running in this context
        """  # noqa: DAR301
        try:
            self.start()
            self.save(session)

            with self._handling_sigterm(session):
                async with self._heartbeating(session):
                    yield

            self.success()
            self.save(session)
        except BaseException as err:  # noqa: WPS424
            if not self.is_running():
                raise

            self.fail(error=self._error_message(err))
            self.save(session)

            raise

    def start(self):
        """Mark the job has having started."""
        self.started_at = datetime.utcnow()
        self.transit(State.RUNNING)

    def fail(self, error=None):
        """Mark the job as having failed.

        Args:
            error: the error to associate with the job's failure
        """
        self.ended_at = datetime.utcnow()
        self.transit(State.FAIL)
        if error:
            self.payload.update({"error": str(error)})

    def success(self):
        """Mark the job as having succeeded."""
        self.ended_at = datetime.utcnow()
        self.transit(State.SUCCESS)

    def fail_stale(self):
        """Mark job as failed if it's gone stale.

        Returns:
            False if job is not stale, else True
        """
        if not self.is_stale():
            return False

        if self.last_heartbeat_at:
            reason = f"No heartbeat recorded for {HEARTBEAT_VALID_MINUTES} minutes."
        else:
            reason = f"Still running after {HEARTBEATLESS_JOB_VALID_HOURS} hours."

        self.fail(f"{reason} The process was likely killed unceremoniously.")

        return True

    def __repr__(self):
        """Represent as a string.

        Returns:
            a string representation of the job
        """
        return f"<Job(id='{self.id}', job_name='{self.job_name}', state='{self.state}', started_at='{self.started_at}', ended_at='{self.ended_at}')>"

    def save(self, session):
        """Save the job in the db.

        Args:
            session: the session to use in querying the db

        Returns:
            the saved job
        """
        session.add(self)
        session.commit()

        return self

    def _heartbeat(self):
        """Update last_heartbeat_at for this job in the db."""
        self.last_heartbeat_at = datetime.utcnow()

    async def _heartbeater(self, session):
        """Heartbeat to the db every second.

        Args:
            session: the session to use for writing to the db
        """
        while True:  # noqa: WPS457
            self._heartbeat()
            self.save(session)

            await asyncio.sleep(1)

    @asynccontextmanager
    async def _heartbeating(self, session):
        """Provide a context for heartbeating jobs.

        Args:
            session: the session to use for writing to the db
        """  # noqa: DAR301
        heartbeat_future = asyncio.ensure_future(self._heartbeater(session))
        try:
            yield
        finally:
            if not heartbeat_future.cancelled():
                heartbeat_future.cancel()

            with suppress(asyncio.CancelledError):
                await heartbeat_future

    @contextmanager
    def _handling_sigterm(self, session):
        def handler(*_):  # noqa: WPS430
            sigterm_status = 143
            raise SystemExit(sigterm_status)

        original_termination_handler = signal.signal(signal.SIGTERM, handler)

        try:
            yield
        finally:
            signal.signal(signal.SIGTERM, original_termination_handler)

    def _error_message(self, err):
        if isinstance(err, SystemExit):
            return "The process was terminated"

        if isinstance(err, (KeyboardInterrupt, asyncio.CancelledError)):
            return "The process was interrupted"

        if str(err):
            return str(err)

        return repr(err)
