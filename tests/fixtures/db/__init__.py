import pytest
import os
import contextlib
import sqlalchemy

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def create_session(engine):
    def _factory(**kwargs):
        Session = sessionmaker(bind=engine)
        return Session(**kwargs)

    return _factory
