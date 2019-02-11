import pytest
import os
import sqlalchemy
import contextlib

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def engine(project):
    engine_uri = "sqlite://"
    engine, _ = project_engine(project, engine_uri)
    return engine


@pytest.fixture()
def session(request, engine, create_session):
    """Creates a new database session for a test."""
    session = create_session()

    def _cleanup():
        session.close()

        meta = MetaData(bind=engine)
        meta.reflect()

        with engine.connect() as con:
            for table in reversed(meta.sorted_tables):
                con.execute(table.delete())

    request.addfinalizer(_cleanup)
    return session
