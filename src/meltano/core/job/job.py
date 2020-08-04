import sys
import os
import logging
import sqlalchemy.types as types
import uuid
import signal
from datetime import datetime
from contextlib import contextmanager
from enum import Enum
from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableDict

from meltano.core.db import SystemModel
from meltano.core.error import Error
from meltano.core.sqlalchemy import JSONEncodedDict, IntFlag, GUID


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


class Job(SystemModel):
    __tablename__ = "job"

    id = Column(types.Integer, primary_key=True)
    job_id = Column(types.String)
    run_id = Column(GUID, nullable=False, default=uuid.uuid4)
    state = Column(types.Enum(State, name="job_state"))
    started_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)
    trigger = Column(types.String, default=current_trigger)

    def __init__(self, **kwargs):
        kwargs["state"] = kwargs.get("state", State.IDLE)
        kwargs["payload"] = kwargs.get("payload", {})
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
        def handle_terminate(signal, frame):
            if self.is_running():
                self.fail(error="The process was terminated")
                self.save(session)

            sys.exit(143)

        try:
            original_termination_handler = signal.signal(
                signal.SIGTERM, handle_terminate
            )

            self.start()
            self.save(session)

            yield

            self.success()
            self.save(session)
        except KeyboardInterrupt:
            if self.is_running():
                self.fail(error="The process was interrupted")
                self.save(session)

            raise
        except BaseException as err:
            if self.is_running():
                if str(err):
                    error = str(err)
                else:
                    error = repr(err)

                self.fail(error=error)
                self.save(session)

            raise
        finally:
            if original_termination_handler:
                signal.signal(signal.SIGTERM, original_termination_handler)

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
