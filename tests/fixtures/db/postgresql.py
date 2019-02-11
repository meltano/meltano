import pytest
import os
import sqlalchemy
import contextlib

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


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
def engine(project, test_engine_uri):
    # create the engine
    engine, _ = project_engine(project, test_engine_uri)
    truncate_tables(engine, schema="meltano")

    return engine


@pytest.fixture()
def session(request, engine, create_session):
    """Creates a new database session for a test."""

    session = create_session()

    def _cleanup():
        session.close()
        truncate_tables(engine, schema="meltano")

    request.addfinalizer(_cleanup)
    return session


def truncate_tables(engine, schema=None):
    con = engine.connect()
    con.execute("SET session_replication_role TO 'replica';")

    with con.begin():
        meta = MetaData(bind=engine, schema=schema)
        meta.reflect()
        for table in meta.sorted_tables:
            con.execute(table.delete())

    con.execute("SET session_replication_role TO 'origin';")
