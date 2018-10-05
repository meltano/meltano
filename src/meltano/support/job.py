import logging
import sqlalchemy.types as types

from enum import Enum
from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableDict
from .db import SystemModel, session_open
from .error import Error


class InconsistentStateError(Error):
    """
    Occur upon a wrong operation for the current state.
    """


class ImpossibleTransitionError(Error):
    """
    Occur upon a wrong transition.
    """


class State(Enum):
    IDLE = (0, ('RUNNING', 'FAIL'))
    RUNNING = (1, ('SUCCESS', 'FAIL'))
    SUCCESS = (2, ())
    FAIL = (3, ('RUNNING',))
    DEAD = (4, ())

    def transitions(self):
        return self.value[1]

    def __str__(self):
        return self.name


class Job(SystemModel):
    __tablename__ = 'job'

    id = Column(types.Integer, primary_key=True)
    elt_uri = Column(types.String)
    state = Column(types.Enum(State))
    started_at = Column(types.DateTime)
    ended_at = Column(types.DateTime)
    payload = Column(MutableDict.as_mutable(types.JSON))

    def __init__(self, **kwargs):
        kwargs['state'] = kwargs.get('state', State.IDLE)
        super().__init__(**kwargs)

    def transit(self, state: State) -> (State, State):
        transition = (self.state, state)

        if self.state is state:
            return transition

        if state.name not in self.state.transitions():
            raise ImpossibleTransitionError(transition)

        self.state = state
        logging.debug("Job {} → {}.".format(self, state))
        return transition

    def __repr__(self):
        return "<Job(id='%s', elt_uri='%s', state='%s')>" % (
            self.id, self.elt_uri, self.state)

    def save(job):
        with session_open() as session:
            session.add(job)
