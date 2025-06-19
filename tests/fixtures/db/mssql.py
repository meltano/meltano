from __future__ import annotations

import contextlib
import logging
import os
import typing as t

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

if t.TYPE_CHECKING:
    from sqlalchemy.engine import URL


def recreate_database(engine, db_name) -> None:
    """Drop & Create a new database.

    We need to use the master connection to do this.

    Args:
        engine: The master connection.
        db_name: The name of the database to create.
    """
    with contextlib.suppress(sa.exc.ProgrammingError), engine.begin() as conn:
        # DROP DATABASE IF EXISTS is not supported by SQL Server 2016 and up
        conn.execute(sa.text(f"DROP DATABASE IF EXISTS {db_name}"))

    with contextlib.suppress(sa.exc.ProgrammingError), engine.begin() as conn:
        conn.execute(sa.text(f"CREATE DATABASE {db_name}"))


def create_connection_url(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> URL:
    """Create a MSSQL connection URL for the given parameters.

    Args:
        host: The hostname.
        port: The port.
        user: The username.
        password: The password.
        database: The database name.

    Returns:
        The connection URL.
    """
    return sa.engine.URL.create(
        "mssql+pymssql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )


@pytest.fixture(scope="session")
def engine_uri(worker_id: str):
    host = os.getenv("MSSQL_ADDRESS")
    port = os.getenv("MSSQL_PORT", 1433)
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")
    database = f"{os.getenv('MSSQL_DB', 'pytest_meltano')}_{worker_id}"

    # Recreate the database using the master database
    master_engine_uri = create_connection_url(host, port, user, password, "master")
    engine = create_engine(
        master_engine_uri,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
        future=True,
    )
    recreate_database(engine, database)

    # Connect to the database where the tests will be run
    testing_engine_uri = create_connection_url(host, port, user, password, database)

    return testing_engine_uri.render_as_string(hide_password=False)


@pytest.fixture
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    logging.info("%s created %d Job.", request.node.name, len(jobs))
