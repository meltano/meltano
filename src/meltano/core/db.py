"""Defines helpers related to the system database."""

from __future__ import annotations

import time
import typing as t
from urllib.parse import urlparse

import structlog
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from meltano.core.error import MeltanoError

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.orm import Session

    from meltano.core.project import Project

# Keep a Project → Engine mapping to serve
# the same engine for the same Project
_engines: dict[Project, tuple[Engine, sessionmaker[Session]]] = {}
logger = structlog.stdlib.get_logger(__name__)


class MeltanoDatabaseCompatibilityError(MeltanoError):
    """Raised when the database is not compatible with Meltano."""

    INSTRUCTION = (
        "Upgrade your database to be compatible with Meltano or use a different "
        "database"
    )

    def __init__(self, reason: str):
        """Initialize the error with a reason.

        Args:
            reason: The reason why the database is not compatible.
        """
        super().__init__(reason, self.INSTRUCTION)


class NullConnectionStringError(MeltanoError):
    """Raised when the database is not compatible with Meltano."""

    REASON = "The `database_uri` setting has a null value"
    INSTRUCTION = (
        "Verify that the `database_uri` setting points to a valid database connection "
        "URI, or use `MELTANO_FF_STRICT_ENV_VAR_MODE=1 meltano config meltano list` "
        "to check for missing environment variables"
    )

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(self.REASON, self.INSTRUCTION)


def project_engine(
    project: Project,
    *,
    default: bool = False,
) -> tuple[Engine, sessionmaker]:
    """Create and register a SQLAlchemy engine for a Meltano project instance.

    Args:
        project: The Meltano project that the engine will be connected to.
        default: Whether the engine created should be stored as the default
            engine for this project.

    Returns:
        The engine, and a session maker bound to the engine.

    Raises:
        NullConnectionStringError: The `database_uri` setting has a null value.
    """
    if existing_engine := _engines.get(project):
        return existing_engine

    database_uri: str = project.settings.get("database_uri")
    parsed_db_uri = urlparse(database_uri)
    sanitized_db_uri = parsed_db_uri._replace(
        netloc=(
            f"{parsed_db_uri.username}:********@"  # user:pass auth case
            if parsed_db_uri.password
            else "********@"  # token auth case
            if parsed_db_uri.username
            else ""  # no auth case
        )
        + (parsed_db_uri.hostname or ""),
    ).geturl()
    logger.debug(
        f"Creating DB engine for project at {str(project.root)!r} "  # noqa: G004
        f"with DB URI {sanitized_db_uri!r}",
    )

    if database_uri is None:
        raise NullConnectionStringError

    engine = create_engine(database_uri, poolclass=NullPool, future=True)

    # Connect to the database to ensure it is available.
    connect(
        engine,
        max_retries=project.settings.get("database_max_retries"),
        retry_timeout=project.settings.get("database_retry_timeout"),
    )

    check_database_compatibility(engine)
    init_hook(engine)

    engine_session = (engine, sessionmaker(bind=engine, future=True))

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
        except OperationalError:  # noqa: PERF203
            if attempt >= max_retries:
                logger.error(
                    f"Could not connect to the database after {attempt} "  # noqa: G004
                    "attempts. Max retries exceeded.",
                )
                raise
            attempt += 1
            logger.info(
                f"DB connection failed. Will retry after {retry_timeout}s. "  # noqa: G004
                f"Attempt {attempt}/{max_retries}",
            )
            time.sleep(retry_timeout)


init_hooks: dict[str, Callable[[Connection], t.Any]] = {
    "sqlite": lambda x: x.execute(text("PRAGMA journal_mode=WAL")),
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
    if hook := init_hooks.get(engine.dialect.name):
        with engine.connect() as conn:
            try:
                hook(conn)
            except Exception as ex:
                raise Exception(f"Failed to initialize database: {ex!s}") from ex  # noqa: EM102


def ensure_schema_exists(
    engine: Engine,
    schema_name: str,
    grant_roles: tuple[str, ...] = (),
) -> None:
    """Ensure the specified `schema_name` exists in the database.

    Args:
        engine: The DB engine to be used.
        schema_name: The name of the schema.
        grant_roles: Roles to grant to the specified schema.
    """
    group_identifiers = ",".join(grant_roles)

    create_schema = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    grant_select_schema = text(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT SELECT ON "
        f"TABLES TO {group_identifiers}",
    )
    grant_usage_schema = text(
        f"GRANT USAGE ON SCHEMA {schema_name} TO {group_identifiers}",
    )

    with engine.connect() as conn, conn.begin():
        conn.execute(create_schema)
        if grant_roles:
            conn.execute(grant_select_schema)
            conn.execute(grant_usage_schema)

    logger.info(f"Schema {schema_name} has been created successfully.")  # noqa: G004
    for role in grant_roles:
        logger.info(f"Usage has been granted for role: {role}.")  # noqa: G004


def check_database_compatibility(engine: Engine) -> None:
    """Check that the database is compatible with Meltano.

    Args:
        engine: The DB engine to be used. This should already be connected to
            the database.

    Raises:
        MeltanoDatabaseCompatibilityError: The database is not compatible with
            Meltano.
    """
    dialect = engine.dialect.name
    version = engine.dialect.server_version_info

    if dialect == "sqlite" and version and version < (3, 25, 1):
        version_string = ".".join(map(str, version))
        reason = (
            f"Detected SQLite {version_string}, but Meltano requires at least 3.25.1"
        )
        raise MeltanoDatabaseCompatibilityError(reason)
