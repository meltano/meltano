import psycopg2
import json

from psycopg2.sql import Identifier, SQL, Placeholder
from enum import Enum
from elt.db import DB
from elt.schema import Schema, Column, DBType
from elt.error import Error
from functools import partial


PG_SCHEMA = 'meltano'
PG_TABLE = 'job_runs'
PRIMARY_KEY = 'id'


class InconsistentStateError(Error):
    """
    Occur upon a wrong operation for the current state.
    """


class ImpossibleTransitionError(Error):
    """
    Occur upon a wrong transition.
    """


def describe_schema() -> Schema:
    def job_column(name, data_type, is_nullable=False):
        return Column(table_name=PG_TABLE,
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


class State(Enum):
    SUCCESS = (2, ())
    FAIL = (3, ())
    RUNNING = (1, ('SUCCESS', 'FAIL'))
    IDLE = (0, ('RUNNING', 'FAIL'))

    def transitions(self):
        return self.value[1]

    def __str__(self):
        return self.name


class Job:
    """
    Represents a Job at a certain state (JobState).
    """
    schema_name = PG_SCHEMA
    table_name = PG_TABLE

    @classmethod
    def identifier(self):
        return map(Identifier, (self.schema_name, self.table_name))

    def __init__(self, elt_uri,
                 state=State.IDLE,
                 started_at=None,
                 ended_at=None,
                 payload={}):
        self.elt_uri = elt_uri
        self._state = state
        self._started_at = started_at
        self._ended_at = ended_at
        self.payload = payload

    @property
    def state(self):
        return self._state

    @property
    def started_at(self):
        return self._started_at

    @started_at.setter
    def started_at(self, value):
        if self.state != State.RUNNING:
            raise InconsistentStateError(self.state)
        self._started_at = value

    @property
    def ended_at(self):
        return self._ended_at

    @ended_at.setter
    def ended_at(self, value):
        if self.state not in (State.SUCCESS, State.FAIL):
            raise InconsistentStateError(self.state)
        self._ended_at = value

    def transit(self, state: State) -> (State, State):
        transition = (self.state, state)

        if state.name not in self.state.transitions():
            raise ImpossibleTransitionError(transition)

        self._state = state
        return transition

    def __dict__(self):
        return {
            'state': str(self.state),
            'elt_uri': str(self.elt_uri),
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'payload': json.dumps(self.payload),
        }

    @classmethod
    def save(self, job):
        job_serial = job.__dict__()
        columns, values = (job_serial.keys(), job_serial.values())

        insert = SQL(("INSERT INTO {}.{} ({}) "
                      "VALUES ({}) "))

        with DB.open() as db, db.cursor() as cursor:
            cursor.execute(
                insert.format(
                    *self.identifier(),
                    SQL(",").join(map(Identifier, columns)),
                    SQL(",").join(Placeholder() * len(values)),
                    ),
                list(values),
            )
            db.commit()

        return job

    @classmethod
    def for_elt(self, elt_uri, limit=100):
        fetch = SQL(("SELECT elt_uri, state, started_at, ended_at, payload FROM {}.{} "
                     "WHERE elt_uri = %s "
                     "ORDER BY started_at DESC "
                     "LIMIT %s ")).format(*self.identifier())

        def as_job(row):
            return Job(row[0],
                       state=State[row[1]],
                       started_at=row[2],
                       ended_at=row[3],
                       payload=row[4])

        with DB.open() as db, db.cursor() as cursor:
            cursor.execute(fetch, (elt_uri, limit))
            return list(map(as_job, cursor.fetchall()))
