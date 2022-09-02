"""Defines helpers related to the system database."""

from __future__ import annotations

import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from meltano.core.project import Project

from .project_settings_service import ProjectSettingsService

# Keep a Project → Engine mapping to serve
# the same engine for the same Project
_engines = {}


def project_engine(
    project: Project,
    default: bool = False,
) -> tuple[Engine, sessionmaker]:
    """Create and register a SQLAlchemy engine for a Meltano project instance.

    Args:
        project: The Meltano project that the engine will be connected to.
        default: Whether the engine created should be stored as the default
            engine for this project.

    Returns:
        The engine, and a session maker bound to the engine.
    """
    existing_engine = _engines.get(project)
    if existing_engine:
        return existing_engine

    settings = ProjectSettingsService(project)

    engine_uri = settings.get("database_uri")
    logging.debug(f"Creating engine '{project}@{engine_uri}'")

    engine = create_engine(engine_uri, poolclass=NullPool)

    # Connect to the database to ensure it is available.
    connect(
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


def connect(
    engine: Engine,
    max_retries: int,
    retry_timeout: float,
) -> Connection:
    """Connect to the database.

    Args:
        engine: The DB engine with which the check will be performed.
        max_retries: The maximum number of retries that will be attempted.
        retry_timeout: The number of seconds to wait between retries.

    Raises:
        OperationalError: Error during DB connection - max retries exceeded.

    Returns:
        A connection to the database.
    """
    attempt = 0
    while True:
        try:
            return engine.connect()
        except OperationalError:
            if attempt >= max_retries:
                logging.error(
                    f"Could not connect to the database after {attempt} "
                    "attempts. Max retries exceeded."
                )
                raise
            attempt += 1
            logging.info(
                f"DB connection failed. Will retry after {retry_timeout}s. "
                f"Attempt {attempt}/{max_retries}"
            )
            time.sleep(retry_timeout)


init_hooks = {
    "sqlite": lambda x: x.execute("PRAGMA journal_mode=WAL"),
}


def init_hook(engine: Engine) -> None:
    """Run the initialization hook for the provided DB engine.

    The initialization hooks are taken from the `meltano.core.db.init_hooks`
    dictionary, which maps the dialect name of the engine to a unary function
    which will be called with the provided DB engine.

    Args:
        engine: The engine for which the init hook will be run.

    Raises:
        Exception: The init hook raised an exception.
    """
    try:
        hook = init_hooks[engine.dialect.name]
    except KeyError:
        return

    try:
        hook(engine)
    except Exception as ex:
        raise Exception(f"Failed to initialize database: {ex!s}") from ex


def ensure_schema_exists(
    engine: Engine,
    schema_name: str,
    grant_roles: tuple[str] = (),
) -> None:
    """Ensure the specified `schema_name` exists in the database.

    Args:
        engine: The DB engine to be used.
        schema_name: The name of the schema.
        grant_roles: Roles to grant to the specified schema.
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
