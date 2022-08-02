import contextlib
import logging
import os

import pytest
import sqlalchemy as sa
from sqlalchemy import DDL, create_engine
from sqlalchemy.engine import URL


def recreate_database(engine, db_name):
    """Drop & Create a new database.

    Args:
        engine: The master connection.
        db_name: The name of the database to create.
    """
    with contextlib.suppress(sa.exc.ProgrammingError):
        engine.execute(
            DDL(
                "DROP DATABASE IF EXISTS %(db_name)s",  # noqa: WPS323
                {"db_name": db_name},
            )
        )

    with contextlib.suppress(sa.exc.ProgrammingError):
        engine.execute(
            DDL(
                "CREATE DATABASE %(db_name)s",  # noqa: WPS323
                {"db_name": db_name},
            )
        )


def create_connection_url(
    host: str, port: int, user: str, password: str, database: str
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
        "mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"charset": "utf8"},
    )


@pytest.fixture(scope="session")
def engine_uri():
    host = os.getenv("MYSQL_ADDRESS")
    port = os.getenv("MYSQL_PORT", 3306)
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DB", "pytest_meltano")

    # Recreate the database using the master database
    master_engine_uri = create_connection_url(host, port, user, password, "mysql")
    engine = create_engine(master_engine_uri, isolation_level="AUTOCOMMIT")
    recreate_database(engine, database)

    # Connect to the database where the tests will be run
    testing_engine_uri = create_connection_url(host, port, user, password, database)

    return str(testing_engine_uri)


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    logging.info("%s created %d Job.", request.node.name, len(jobs))  # noqa: WPS323
