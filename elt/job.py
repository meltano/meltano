import psycopg2
import json
import sqlalchemy.types as types

from psycopg2.sql import Identifier, SQL, Placeholder
from enum import Enum
from functools import partial
from elt.db import DB, SystemModel
from elt.schema import Schema, Column as SchemaColumn, DBType
from elt.error import Error
from sqlalchemy import Column


PG_SCHEMA = 'meltano'
PG_TABLE = 'job'
PRIMARY_KEY = 'id'


class InconsistentStateError(Error):
    """
    Occur upon a wrong operation for the current state.
    """


class ImpossibleTransitionError(Error):
    """
    Occur upon a wrong transition.
    """


class State(Enum):
    SUCCESS = (2, ())
    FAIL = (3, ())
    RUNNING = (1, ('SUCCESS', 'FAIL'))
    IDLE = (0, ('RUNNING', 'FAIL'))

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
    payload = Column(types.JSON)

    def transit(self, state: State) -> (State, State):
        transition = (self.state, state)

        if state.name not in self.state.transitions():
            raise ImpossibleTransitionError(transition)

        self.state = state
        return transition

    def __repr__(self):
        return "<Job(id='%s', elt_uri='%s', state='%s')>" % (
            self.id, self.elt_uri, self.state)

    def describe_schema() -> Schema:
        def job_column(name, data_type, is_nullable=False):
            return SchemaColumn(table_name=PG_TABLE,
                        table_schema=PG_SCHEMA,
                        column_name=name,
                        data_type=data_type.value,
                        is_nullable=is_nullable,
                        is_mapping_key=False)

        return Schema(PG_SCHEMA, [
            job_column('elt_uri', DBType.String),
            job_column('state', DBType.String),
            job_column('started_at', DBType.Timestamp, is_nullable=True),
            job_column('ended_at', DBType.Timestamp, is_nullable=True),
            job_column('payload', DBType.JSON, is_nullable=True),
        ], primary_key_name='id')

    def save(job):
        with DB.session() as session:
            session.add(job)
