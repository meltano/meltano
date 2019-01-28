import pytest
import os
import contextlib
import sqlalchemy

from meltano.core.db import DB, project_engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


def engine_uri(**db_config):
    return "postgresql://{user}:{password}@{host}:{port}/{database}".format(**db_config)


BACKEND = os.getenv("PYTEST_BACKEND", "sqlite")


if BACKEND == "postgres":

    @pytest.fixture()
    def engine(project, monkeypatch):
        database = "postgres"
        host = os.getenv("PG_ADDRESS")
        port = os.getenv("PG_PORT", 5432)
        user = os.getenv("PG_USERNAME")
        password = os.getenv("PG_PASSWORD")

        engine_uri = f"postgres://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(engine_uri, isolation_level="AUTOCOMMIT")
        with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
            DB.create_database(engine, "pytest")

        # register the current engine
        engine, _ = project_engine(project, engine_uri)
        truncate_tables(engine, schema="meltano")

        return engine

    @pytest.fixture()
    def session(request, engine, create_session):
        """Creates a new database session for a test."""

        session = create_session()

        def _cleanup():
            session.close()
            truncate_tables(engine, schema="meltano")

        request.addfinalizer(_cleanup)
        return session

    def truncate_tables(engine, schema=None):
        con = engine.connect()
        con.execute("SET session_replication_role TO 'replica';")

        with con.begin():
            meta = MetaData(bind=engine, schema=schema)
            meta.reflect()
            for table in meta.sorted_tables:
                con.execute(table.delete())

        con.execute("SET session_replication_role TO 'origin';")


elif BACKEND == "sqlite":

    @pytest.fixture()
    def engine(monkeypatch, project):
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

            with contextlib.closing(engine.connect()) as con:
                trans = con.begin()
                for table in reversed(meta.sorted_tables):
                    con.execute(table.delete())
                trans.commit()

        request.addfinalizer(_cleanup)
        return session


else:
    raise Exception(f"PYTEST_BACKEND not supported: {BACKEND}.")


@pytest.fixture()
def create_session(engine):
    def _factory(**kwargs):
        Session = sessionmaker(bind=engine)
        return Session(**kwargs)

    return _factory
