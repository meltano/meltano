"""Defines Job model class."""
import logging
import os
import signal
import uuid
from contextlib import contextmanager
from datetime import datetime
from enum import Enum

import sqlalchemy.types as types
from meltano.core.error import Error
from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import GUID, IntFlag, JSONEncodedDict
from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableDict


class InconsistentStateError(Error):
    """
    Occur upon a wrong operation for the current state.
    """


class ImpossibleTransitionError(Error):
    """
    Occur upon a wrong transition.
    """


class State(Enum):
    IDLE = (0, ("RUNNING", "FAIL"))
    RUNNING = (1, ("SUCCESS", "FAIL"))
    SUCCESS = (2, ())
    FAIL = (3, ("RUNNING",))
    DEAD = (4, ())

    def transitions(self):
        return self.value[1]

    def __str__(self):
        return self.name


def current_trigger():
    return os.getenv("MELTANO_JOB_TRIGGER")


class Payload(IntFlag):
    STATE = 1
    INCOMPLETE_STATE = 2


class Job(SystemModel):  # noqa: WPS214
    """Model class that represents a `meltano elt` run in the system database."""

    __tablename__ = "job"

    id = Column(types.Integer, primary_key=True)
    job_id = Column(types.String)
    run_id = Column(GUID, nullable=False, default=uuid.uuid4)
    state = Column(types.Enum(State, name="job_state"))
    started_at = Column(types.DateTime)
    last_heartbeat_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)
    trigger = Column(types.String, default=current_trigger)

    def __init__(self, **kwargs):
        kwargs["state"] = kwargs.get("state", State.IDLE)
        kwargs["payload"] = kwargs.get("payload", {})
        kwargs["run_id"] = kwargs.get("run_id", uuid.uuid4())
        super().__init__(**kwargs)

    def is_running(self):
        return self.state is State.RUNNING

    def has_error(self):
        return self.state is State.FAIL

    def is_complete(self):
        return self.state in [State.SUCCESS, State.FAIL]

    def is_success(self):
        return self.state is State.SUCCESS

    def can_transit(self, state: State) -> bool:
        if self.state is state:
            return True

        return state.name in self.state.transitions()

    def transit(self, state: State) -> (State, State):
        transition = (self.state, state)

        if not self.can_transit(state):
            raise ImpossibleTransitionError(transition)

        if self.state is state:
            return transition

        self.state = state

        return transition

    @contextmanager
    def run(self, session):
        """
        Run wrapped code in context of a job.

        Transitions state to RUNNING and SUCCESS/FAIL as appropriate.
        """
        try:
            self.start()
            self.save(session)

            with self._handling_sigterm(session):
                yield

            self.success()
            self.save(session)
        except BaseException as err:
            if not self.is_running():
                raise

            self.fail(error=self._error_message(err))
            self.save(session)

            raise

    def start(self):
        self.started_at = datetime.utcnow()
        self.transit(State.RUNNING)

    def fail(self, error=None):
        self.ended_at = datetime.utcnow()
        self.transit(State.FAIL)
        if error:
            self.payload.update({"error": str(error)})

    def success(self):
        self.ended_at = datetime.utcnow()
        self.transit(State.SUCCESS)

    def __repr__(self):
        return (
            "<Job(id='%s', job_id='%s', state='%s', started_at='%s', ended_at='%s')>"
            % (self.id, self.job_id, self.state, self.started_at, self.ended_at)
        )

    def save(self, session):
        session.add(self)
        session.commit()

        return self

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

        if isinstance(err, KeyboardInterrupt):
            return "The process was interrupted"

        if str(err):
            return str(err)

        return repr(err)
