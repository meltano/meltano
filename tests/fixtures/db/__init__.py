import logging
import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True)
def engine_uri_env(monkeypatch, engine_uri):
    monkeypatch.setenv("MELTANO_DATABASE_URI", engine_uri)


@pytest.fixture(scope="class", autouse=True)
def vacuum_db(engine_sessionmaker):
    engine, _ = engine_sessionmaker

    yield

    logging.debug(f"Cleaning system database...")
    metadata = MetaData(bind=engine)
    metadata.reflect()
    metadata.drop_all()
    logging.debug(f"Cleaned system database")


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
