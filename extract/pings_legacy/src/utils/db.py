import psycopg2
import os
import contextlib
import logging

from psycopg2.extras import LoggingConnection

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

class DB:
    connection_class = LoggingConnection

    # db_config dictionary with {'host', 'port', 'user', 'password', 'database'}
    def __init__(self, db_config):
        self.db_config = db_config

        self._connection = None
        self._connection = self.connect()
        self._engine = create_engine(self.engine_uri(), creator=self.connect)

        SystemModel = declarative_base(metadata=MetaData(schema='meltano'))
        Model = declarative_base()

        session_factory = sessionmaker()
        self.Session = scoped_session(session_factory)

        self.Session.configure(bind=self._engine)

    def connect(self):
        if self._connection is not None:
            return self._connection

        conn = psycopg2.connect(**self.db_config,
                                connection_factory=self.connection_class)
        conn.initialize(logging.getLogger(__name__))
        return conn

    def engine(self):
        return self._engine

    def set_connection_class(self, cls):
        self.connection_class = cls

    def close(self):
        if self.engine is not None:
            self._engine.dispose()

    def engine_uri(self):
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**self.db_config)

    @contextlib.contextmanager
    def open(self):
        """Provide a raw connection in a transaction."""
        connection = self.connect()

        try:
            yield connection
            connection.commit()
        except:
            connection.rollback()
            raise

    @contextlib.contextmanager
    def session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
