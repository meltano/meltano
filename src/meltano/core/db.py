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


def project_engine(project, engine_uri=None, default=False) -> ("Engine", sessionmaker):
    """Creates and register a SQLAlchemy engine for a Meltano project instance."""

    # return the default engine if it is registered
    if not engine_uri and project in _engines:
        return _engines[project]
    elif (project, engine_uri) in _engines:
        return _engines[(project, engine_uri)]

    if not engine_uri:
        logging.debug(f"Can't find engine for {project}@{engine_uri}")
        raise ValueError("No engine registered for this project.")

    logging.debug(f"Creating engine {project}@{engine_uri}")
    engine = create_engine(engine_uri)
    init_hook(engine)

    create_session = sessionmaker(bind=engine)
    engine_session = (engine, create_session)

    if default:
        # register the default engine
        _engines[project] = engine_session
    else:
        _engines[(project, engine_uri)] = engine_session

    return engine_session


def init_hook(engine):
    function_map = {"sqlite": init_sqlite_hook, "postgresql": init_postgresql_hook}

    try:
        function_map[engine.dialect.name](engine)
    except KeyError:
        raise Exception("Meltano only supports SQLite and PostgreSQL")
    except:
        logging.fatal("Can't initialize database.")


def init_postgresql_hook(engine):
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
