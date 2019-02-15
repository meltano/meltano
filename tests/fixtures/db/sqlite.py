import pytest
import os
import sqlalchemy
import contextlib

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData


@pytest.fixture()
def engine_sessionmaker(project):
    engine_uri = "sqlite://"
    return project_engine(project, engine_uri, default=True)


@pytest.fixture()
def session(request, engine_sessionmaker):
    """Creates a new database session for a test."""
    engine, create_session = engine_sessionmaker
    session = create_session()

    yield session

    # teardown
    session.close()
    meta = MetaData(bind=engine)
    meta.reflect()

    with engine.connect() as con:
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
