import pytest
import os
import contextlib
import sqlalchemy

from meltano.core.db import DB, SystemModel
from sqlalchemy import MetaData


@pytest.fixture(scope="session")
def db_setup(request):
    args = {
        "database": "pytest",
        "host": os.getenv("PG_ADDRESS"),
        "port": os.getenv("PG_PORT", 5432),
        "user": os.getenv("PG_USERNAME"),
        "password": os.getenv("PG_PASSWORD"),
    }
    DB.setup(**args)
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        DB.create_database("pytest")
    DB.default.ensure_schema_exists("meltano")

    # Create the base models
    SystemModel.metadata.create_all(DB.default.engine)

    truncate_tables(DB.default.engine, schema="meltano")


@pytest.fixture(scope="function")
def db(request, db_setup):
    def teardown():
        truncate_tables(DB.default, schema="meltano")

    request.addfinalizer(teardown)
    return DB.default


@pytest.fixture(scope="function")
def session(request, db):
    """Creates a new database session for a test."""
    session = db.create_session()

    request.addfinalizer(session.rollback)

    return session


def truncate_tables(db, schema):
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    con = db.engine.connect()
    trans = con.begin()
    con.execute("SET session_replication_role TO 'replica';")

    meta = MetaData(bind=db.engine, schema=schema)
    meta.reflect()
    for table in meta.sorted_tables:
        con.execute(table.delete())

    con.execute("SET session_replication_role TO 'origin';")
    trans.commit()
