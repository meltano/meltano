from __future__ import annotations

import contextlib
import os

import pytest
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


def recreate_database(engine, db_name):
    """Drop & Create a new database, PostgreSQL only."""
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        engine.execute(text(f"DROP DATABASE {db_name}"))

    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        engine.execute(text(f"CREATE DATABASE {db_name}"))


@pytest.fixture(scope="session")
def engine_uri(worker_id: str):
    host = os.getenv("POSTGRES_ADDRESS")
    port = os.getenv("POSTGRES_PORT", 5432)
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = f"{os.getenv('POSTGRES_DB', 'pytest_meltano')}_{worker_id}"

    # create the database
    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(
        engine_uri,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    recreate_database(engine, database)

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
