import psycopg2
import os
import contextlib

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


db_config_keys = [
    "host",
    "port",
    "user",
    "password",
    "database",
]


def engine_uri(**db_config):
    return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**db_config)


SystemModel = declarative_base(metadata=MetaData(schema='meltano'))
Model = declarative_base()
Session = sessionmaker()


class DB:
    db_config = {
        'host': os.getenv('PG_ADDRESS', 'localhost'),
        'port': os.getenv('PG_PORT', 5432),
        'user': os.getenv('PG_USERNAME', os.getenv('USER')),
        'password': os.getenv('PG_PASSWORD'),
        'database': os.getenv('PG_DATABASE'),
    }
    connection_class = psycopg2.extensions.connection
    _connection = None
    _engine = None

    @classmethod
    def setup(self, open_persistent=False, **kwargs):
        self.db_config.update({k: kwargs[k] for k in db_config_keys if k in kwargs})
        self._connection = self.connect()
        self._engine = create_engine(engine_uri(**self.db_config), creator=self.connect)
        Session.configure(bind=self._engine)

    @classmethod
    def connect(self):
        if self._connection is not None:
            return self._connection

        return psycopg2.connect(**self.db_config,
                                connection_factory=self.connection_class)

    @classmethod
    def session(self):
        return session_open()

    @classmethod
    def open(self):
        return db_open()

    @classmethod
    def set_connection_class(self, cls):
        self.connection_class = cls

    @classmethod
    def close(self):
        if self.engine is not None:
            self._engine.dispose()


@contextlib.contextmanager
def db_open():
    """Provide a raw connection in a transaction"""
    connection = DB.connect()
    try:
        yield connection
        connection.commit()
    except:
        connection.rollback()
        raise


@contextlib.contextmanager
def session_open():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
