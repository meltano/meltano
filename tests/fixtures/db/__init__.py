from __future__ import annotations

import logging
import warnings
from contextlib import closing
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa: WPS436
from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import close_all_sessions, sessionmaker
from sqlalchemy.pool import NullPool

from meltano.core.project import Project


@pytest.fixture(scope="session", autouse=True)
def engine_uri_env(engine_uri: str) -> Generator:
    """Use the correct meltano database URI for these tests."""
    # No session monkey patch yet https://github.com/pytest-dev/pytest/issues/363
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("MELTANO_DATABASE_URI", engine_uri)
    try:
        yield
    finally:
        monkeypatch.undo()


@pytest.fixture()
def un_engine_uri(monkeypatch):
    """When we want to test functionality that doesn't use the current DB URI.

    Note that this fixture must run before the project fixture as
    src/meltano/core/db.py _engines has the engine cached.
    """
    monkeypatch.delenv("MELTANO_DATABASE_URI")


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
    engine = create_engine(engine_uri, poolclass=NullPool)
    return (engine, sessionmaker(bind=engine))


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
def session(project: Project, engine_sessionmaker, connection):  # noqa: WPS442
    """Create a new database session for a test.

    Args:
        project: The `project` fixture.
        engine_sessionmaker: The `engine_sessionmaker` fixture.
        connection: The `connection` fixture.

    Yields:
        An ORM DB session for the given project, bound to the given connection.
    """
    _, create_session = engine_sessionmaker
    with closing(create_session(bind=connection)) as fixture_session:
        yield fixture_session
