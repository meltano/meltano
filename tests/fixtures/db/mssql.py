import contextlib
import logging
import os

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


def recreate_database(engine, db_name):
    """
    Drop & Create a new database. We need to use the master connection to do this.
    """
    with contextlib.suppress(sa.exc.ProgrammingError):
        engine.execute(text(f"""
            USE master;
            ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            DROP DATABASE [{db_name}];
        """))

    with contextlib.suppress(sa.exc.ProgrammingError):
        engine.execute(text(f"CREATE DATABASE {db_name}"))

def create_connection_url(host: str, port: int, user: str, password: str, database: str) -> URL:
    """
    Create a MSSQL connection URL for the given parameters.
    """
    connection_url = sa.engine.URL.create(
        "mssql+pyodbc",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "LongAsMax": "Yes",
            "TrustServerCertificate": "Yes",
        },
    )

    return connection_url

@pytest.fixture(scope="session")
def engine_uri():
    host = os.getenv("MSSQL_ADDRESS")
    port = os.getenv("MSSQL_PORT", 1433)
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")
    database = os.getenv("MSSQL_DB", "pytest_meltano")

    # create the database
    engine_uri = create_connection_url(host, port, user, password, database)
    engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
    recreate_database(engine, database)

    return str(engine_uri)


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    print(f"{request.node.name} created {len(jobs)} Job.")
