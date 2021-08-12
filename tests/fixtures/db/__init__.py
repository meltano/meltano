import logging

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import close_all_sessions, sessionmaker


@pytest.fixture(scope="session", autouse=True)
def engine_uri_env(engine_uri):
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("MELTANO_DATABASE_URI", engine_uri)

    yield

    monkeypatch.undo()


@pytest.fixture(scope="class", autouse=True)
def vacuum_db(engine_sessionmaker):
    yield

    logging.debug(f"Cleaning system database...")

    engine, _ = engine_sessionmaker
    close_all_sessions()
    metadata = MetaData(bind=engine)
    metadata.reflect()
    metadata.drop_all()


@pytest.fixture(scope="class")
def engine_sessionmaker(engine_uri):
    # create the engine
    engine = create_engine(engine_uri)
    create_session = sessionmaker(bind=engine)

    return (engine, create_session)


@pytest.fixture()
def connection(engine_sessionmaker):
    engine, _ = engine_sessionmaker
    connection = engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture()
def session(project, engine_sessionmaker, connection):
    """Creates a new database session for a test."""
    _, Session = engine_sessionmaker

    try:
        session = Session(bind=connection)
        yield session
    finally:
        session.close()
