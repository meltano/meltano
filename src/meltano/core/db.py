import psycopg2
import os
import contextlib
import sqlalchemy.pool as pool
import logging
import weakref

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.sql import Identifier, SQL


SystemMetadata = MetaData()
SystemModel = declarative_base(metadata=SystemMetadata)

# Keep a Project → Engine mapping to serve
# the same engine for the same Project
_engines = dict()


def project_register_engine(project, engine):
    if project in _engines:
        return _engines[project]

    Session = sessionmaker(bind=engine)
    _engines[project] = engine, Session

    init_hook(engine)

    return engine, Session


def project_engine(project, engine_uri=None):
    """Creates or register a SQLAlchemy engine for a Meltano project."""
    if project in _engines:
        return _engines[project]

    engine_uri = engine_uri or os.getenv("SQL_ENGINE_URI", "sqlite:///meltano.db")

    engine = create_engine(engine_uri)
    return project_register_engine(project, engine)


def init_hook(engine):
    function_map = {"sqlite": init_sqlite_hook, "postgresql": init_postgresql_hook}

    try:
        function_map[engine.dialect.name](engine)
    except KeyError:
        raise Exception("Meltano only supports SQLite and PostgreSQL")
    except:
        logging.fatal("Can't initialize database.")


def init_postgresql_hook(engine):
    import pdb

    pdb.set_trace()
    schema = os.getenv("PG_SCHEMA", "meltano")
    DB.ensure_schema_exists(engine, schema)

    SystemMetadata.schema = schema

    # we need to manually set the schema for Table that
    # are already imported.
    for table in SystemMetadata.tables.values():
        table.schema = schema

    seed(engine)


def init_sqlite_hook(engine):
    seed(engine)


# TODO: alembic hook?
def seed(engine):
    # import all the models
    import meltano.core.job

    # seed the database
    SystemMetadata.create_all(engine)


class DB:
    @classmethod
    def create_database(cls, engine, db_name):
        """
        Create a new database, PostgreSQL only.
        """
        engine.execute(text(f"CREATE DATABASE {db_name}"))

    @classmethod
    def ensure_schema_exists(cls, engine, schema_name, grant_roles=()):
        """
        Make sure that the given schema_name exists in the database
        If not, create it

        :param db_conn: psycopg2 database connection
        :param schema_name: database schema
        """
        schema_identifier = schema_name
        group_identifiers = ",".join(grant_roles)

        create_schema = text(f"CREATE SCHEMA IF NOT EXISTS {schema_identifier}")
        grant_select_schema = text(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_identifier} GRANT SELECT ON TABLES TO {group_identifiers}"
        )
        grant_usage_schema = text(
            f"GRANT USAGE ON SCHEMA {schema_identifier} TO {group_identifiers}"
        )

        with engine.connect() as conn, conn.begin():
            conn.execute(create_schema)
            if grant_roles:
                conn.execute(grant_select_schema)
                conn.execute(grant_usage_schema)

        logging.info("Schema {} has been created successfully.".format(schema_name))
        for role in grant_roles:
            logging.info("Usage has been granted for role: {}.".format(role))
