import logging
import os
import warnings
from typing import Generator

import pytest
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import close_all_sessions, sessionmaker


@pytest.fixture(scope="session", autouse=True)
def engine_uri_env(engine_uri: str) -> None:
    """Use the correct meltano database URI for these tests."""
    os.environ["MELTANO_DATABASE_URI"] = engine_uri


@pytest.fixture
def un_engine_uri(monkeypatch) -> Generator:
    """When we want to test functionality that doesn't use the current DB URI."""
    with monkeypatch.context() as m:
        m.delenv("MELTANO_DATABASE_URI")
        yield


@pytest.fixture(scope="class", autouse=True)
def vacuum_db(engine_sessionmaker):
    try:
        yield
    finally:
        logging.debug("Cleaning system database...")
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
def connection(engine_sessionmaker):  # noqa: WPS442
    engine, _ = engine_sessionmaker
    connection = engine.connect()  # noqa: WPS442
    transaction = connection.begin()

    try:
        yield connection
    finally:
        with warnings.catch_warnings():
            # Ignore warnings about rolling back the same transaction twice
            warnings.filterwarnings(
                "ignore", "transaction already deassociated from connection", SAWarning
            )
            transaction.rollback()
        connection.close()


@pytest.fixture()
def session(project, engine_sessionmaker, connection):  # noqa: WPS442
    """Create a new database session for a test."""
    _, create_session = engine_sessionmaker

    session = create_session(bind=connection)  # noqa: WPS442
    try:
        yield session
    finally:
        session.close()
