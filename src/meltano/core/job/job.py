import logging
import sqlalchemy.types as types

from datetime import datetime
from contextlib import contextmanager
from enum import Enum
from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableDict
from meltano.core.db import SystemModel
from meltano.core.error import Error
from meltano.core.sqlalchemy import JSONEncodedDict, IntFlag


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


class Job(SystemModel):
    __tablename__ = "job"

    id = Column(types.Integer, primary_key=True)
    job_id = Column(types.String)
    state = Column(types.Enum(State))
    started_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(JSONEncodedDict))
    payload_flags = Column(IntFlag, default=0)

    def __init__(self, **kwargs):
        kwargs["state"] = kwargs.get("state", State.IDLE)
        kwargs["payload"] = kwargs.get("payload", {})
        super().__init__(**kwargs)

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
        try:
            self.start()
            self.save(session)

            yield

            self.success()
            self.save(session)
        except Exception as err:
            logging.error(err)
            self.fail(error=err)
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
        return "<Job(id='%s', job_id='%s', state='%s')>" % (
            self.id,
            self.job_id,
            self.state,
        )

    def save(self, session):
        session.add(self)
        session.commit()

        return self
