import pytest
import os
import sqlalchemy
import contextlib
import logging

from meltano.core.db import DB, project_engine
from meltano.core.migration_service import MigrationService
from sqlalchemy import text, create_engine, MetaData


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
    database = "pytest_meltano"

    # create the database
    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
    recreate_database(engine, database)

    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(engine_uri)

    # migrate the database up
    migration_service = MigrationService(engine)
    migration_service.upgrade()

    return str(engine.url)


@pytest.fixture()
def engine_sessionmaker(project, engine_uri):
    # create the engine
    engine, sessionmaker = project_engine(project, engine_uri, default=True)

    return (engine, sessionmaker)


@pytest.fixture()
def session(engine_sessionmaker, vacuum_db):
    """Creates a new database session for a test."""
    engine, sessionmaker = engine_sessionmaker
    session = sessionmaker()

    try:
        yield session
    finally:
        # teardown
        session.close()
        vacuum_db()


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    print(f"{request.node.name} created {len(jobs)} Job.")
