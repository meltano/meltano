import contextlib
import logging
import os

import pytest
import sqlalchemy
from sqlalchemy import create_engine, text


def recreate_database(engine, db_name):
    """
    Drop & Create a new database, PostgreSQL only.
    """
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        engine.execute(text(f"DROP DATABASE {db_name}"))

    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        engine.execute(text(f"CREATE DATABASE {db_name}"))


@pytest.fixture(scope="session")
def engine_uri():
    host = os.getenv("POSTGRES_ADDRESS")
    port = os.getenv("POSTGRES_PORT", 5432)
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB", "pytest_meltano")

    # create the database
    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
    recreate_database(engine, database)

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    print(f"{request.node.name} created {len(jobs)} Job.")
