import pytest
import os
import sqlalchemy
import contextlib
import logging

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData


@pytest.fixture(scope="session")
def test_engine_uri():
    host = os.getenv("PG_ADDRESS")
    port = os.getenv("PG_PORT", 5432)
    user = os.getenv("PG_USERNAME")
    password = os.getenv("PG_PASSWORD")

    # create the database
    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        DB.create_database(engine, "pytest")

    return f"postgresql://{user}:{password}@{host}:{port}/pytest"


@pytest.fixture()
def engine_sessionmaker(project, test_engine_uri):
    # create the engine
    engine, sessionmaker = project_engine(project, test_engine_uri, default=True)

    return (engine, sessionmaker)


@pytest.fixture()
def session(request, engine_sessionmaker):
    """Creates a new database session for a test."""
    engine, sessionmaker = engine_sessionmaker
    truncate_tables(engine, schema="meltano")

    session = sessionmaker()

    yield session

    # teardown
    session.close()
    logging.debug("Session closed.")
    truncate_tables(engine, schema="meltano")


def truncate_tables(engine, schema=None):
    with engine.connect() as con:
        con.execute("SET session_replication_role TO 'replica';")

        with con.begin():
            meta = MetaData(bind=engine, schema=schema)
            meta.reflect()
            for table in meta.sorted_tables:
                logging.debug(f"table {table} truncated.")
                con.execute(table.delete())

        con.execute("SET session_replication_role TO 'origin';")


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    print(f"{request.node.name} created {len(jobs)} Job.")
