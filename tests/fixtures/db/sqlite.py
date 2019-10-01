import pytest
import os
import sqlalchemy
import contextlib

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData


@pytest.fixture(scope="session")
def engine_uri():
    return "sqlite:///pytest_meltano.db"


@pytest.fixture()
def engine_sessionmaker(project, engine_uri):
    return project_engine(project, engine_uri, default=True)


@pytest.fixture()
def session(request, engine_sessionmaker, vacuum):
    """Creates a new database session for a test."""
    engine, create_session = engine_sessionmaker
    session = create_session()

    yield session

    # teardown
    session.close()
    vacuum()
