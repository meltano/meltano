import pytest
import os
import sqlalchemy
import contextlib
import logging

from meltano.core.db import DB, project_engine
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
    user = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DATABASE")

    # create the database
    engine_uri = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
    recreate_database(engine, database)

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture()
def engine_sessionmaker(project, engine_uri):
    # create the engine
    engine, sessionmaker = project_engine(project, engine_uri, default=True)

    return (engine, sessionmaker)


@pytest.fixture()
def session(request, engine_sessionmaker):
    """Creates a new database session for a test."""
    engine, sessionmaker = engine_sessionmaker
    truncate_tables(engine)

    session = sessionmaker()

    yield session

    # teardown
    session.close()
    logging.debug("Session closed.")
    truncate_tables(engine)


def truncate_tables(engine, schema=None):
    with engine.connect() as con:
        con.execute("SET session_replication_role TO 'replica';")

        with con.begin():
            meta = MetaData(bind=engine, schema=schema)
            meta.reflect()

            for table in meta.sorted_tables:
                if table.name == "alembic_version":
                    continue

                logging.debug(f"table {table} truncated.")
                con.execute(table.delete())

        con.execute("SET session_replication_role TO 'origin';")


@pytest.fixture()
def pg_stats(request, session):
    yield

    from meltano.core.job import Job

    jobs = session.query(Job).all()
    print(f"{request.node.name} created {len(jobs)} Job.")
