"""Defines helpers related to the system database."""

import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from .project_settings_service import ProjectSettingsService

# Keep a Project → Engine mapping to serve
# the same engine for the same Project
_engines = dict()


def project_engine(project, default=False) -> ("Engine", sessionmaker):
    """Creates and register a SQLAlchemy engine for a Meltano project instance."""

    existing_engine = _engines.get(project)
    if existing_engine:
        return existing_engine

    settings = ProjectSettingsService(project)

    engine_uri = settings.get("database_uri")
    logging.debug(f"Creating engine {project}@{engine_uri}")
    engine = create_engine(engine_uri, pool_pre_ping=True)

    check_db_connection(
        engine,
        max_retries=settings.get("database_max_retries"),
        retry_timeout=settings.get("database_retry_timeout"),
    )

    init_hook(engine)

    engine_session = (engine, sessionmaker(bind=engine))

    if default:
        # register the default engine
        _engines[project] = engine_session

    return engine_session


def check_db_connection(engine, max_retries, retry_timeout):  # noqa: WPS231
    """Check if the database is available the first time a project's engine is created."""
    attempt = 0
    while True:
        try:
            engine.connect()
        except OperationalError:
            if attempt == max_retries:
                logging.error(
                    "Could not connect to the Database. Max retries exceeded."
                )
                raise
            attempt += 1
            logging.info(
                f"DB connection failed. Will retry after {retry_timeout}s. Attempt {attempt}/{max_retries}"
            )
            time.sleep(retry_timeout)
        else:
            break


def init_hook(engine):
    function_map = {"sqlite": init_sqlite_hook}

    try:
        function_map[engine.dialect.name](engine)
    except KeyError:
        pass
    except Exception as e:
        raise Exception(f"Can't initialize database: {str(e)}") from e


def init_sqlite_hook(engine):
    # enable the WAL
    engine.execute("PRAGMA journal_mode=WAL")


class DB:
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

        logging.info(f"Schema {schema_name} has been created successfully.")
        for role in grant_roles:
            logging.info(f"Usage has been granted for role: {role}.")
