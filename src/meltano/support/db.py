import psycopg2
import os
import contextlib
import sqlalchemy.pool as pool
import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.sql import Identifier, SQL


def engine_uri(**db_config):
    return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**db_config)


SystemModel = declarative_base(metadata=MetaData(schema="meltano"))


class MetaDB(type):
    def __init__(cls, *_):
        cls._default = None

    @property
    def default(cls):
        return cls._default

    @default.setter
    def default(cls, v):
        if cls._default:
            cls._default.close()

        cls._default = v


class DB(metaclass=MetaDB):
    db_config = {
        "host": os.getenv("PG_ADDRESS", "localhost"),
        "port": os.getenv("PG_PORT", 5432),
        "user": os.getenv("PG_USERNAME", os.getenv("USER")),
        "password": os.getenv("PG_PASSWORD"),
        "database": os.getenv("PG_DATABASE"),
    }

    @classmethod
    def setup(cls, **kwargs):
        """
        Store the DB connection parameters and create a default engine.
        """
        cls.db_config.update(
            {k: kwargs[k] for k in cls.db_config.keys() if k in kwargs}
        )

        # use connection pooling for all connections
        pool.manage(psycopg2)
        cls.default = cls()

    @classmethod
    def create_database(cls, db_name):
        """
        Create a new database
        """
        config = cls.db_config.copy()
        config.update({"database": "postgres"})
        with create_engine(
            engine_uri(**config), isolation_level="AUTOCOMMIT"
        ).connect() as con:
            con.execute(text(f"CREATE DATABASE {db_name}"))

    @classmethod
    def close_default(cls):
        """
        Close the default engine
        """
        if cls.default:
            cls.default.close()

    @property
    def engine(self):
        return self._engine

    def __init__(self):
        self._engine = create_engine(engine_uri(**self.db_config))
        self._session_cls = scoped_session(sessionmaker(bind=self.engine))

    def create_connection(self):
        return psycopg2.connect(**self.db_config)

    def create_session(self):
        return self._session_cls()

    def open(self):
        return db_open(self)

    def session(self):
        return session_open(self)

    def close(self):
        if self.engine:
            self.engine.dispose()

    def ensure_schema_exists(self, schema_name, grant_roles=()):
        """
        Make sure that the given schema_name exists in the database
        If not, create it

        :param db_conn: psycopg2 database connection
        :param schema_name: database schema
        """
        conn = self.create_connection()
        cursor = conn.cursor()
        schema_identifier = Identifier(schema_name)
        group_identifiers = SQL(",").join(map(Identifier, grant_roles))

        create_schema = SQL(
            """
        CREATE SCHEMA IF NOT EXISTS {}
        """
        ).format(schema_identifier)

        grant_select_schema = SQL(
            """
        ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON TABLES TO {}
        """
        ).format(schema_identifier, group_identifiers)

        grant_usage_schema = SQL(
            """
        GRANT USAGE ON SCHEMA {} TO {}
        """
        ).format(schema_identifier, group_identifiers)

        cursor.execute(create_schema)
        if grant_roles:
            cursor.execute(grant_select_schema)
            cursor.execute(grant_usage_schema)

        conn.commit()

        logging.info("Schema {} has been created successfully.".format(schema_name))
        for role in grant_roles:
            logging.info("Usage has been granted for role: {}.".format(role))


@contextlib.contextmanager
def db_open(db: DB = None):
    """Provide a raw connection in a transaction."""
    connection = (db or DB.default).create_connection()

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise


@contextlib.contextmanager
def session_open(db: DB = None):
    """Provide a transactional scope around a series of operations."""
    session = (db or DB.default).create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
