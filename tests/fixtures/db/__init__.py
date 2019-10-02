import pytest
from sqlalchemy import create_engine, MetaData
from meltano.core.migration_service import MigrationService
from meltano.core.db import project_engine


@pytest.fixture(autouse=True)
def engine_uri_env(monkeypatch, engine_uri):
    monkeypatch.setenv("MELTANO_DATABASE_URI", engine_uri)


@pytest.fixture(scope="session", autouse=True)
def migrate(engine_uri):
    engine = create_engine(engine_uri)

    # migrate the database up
    MigrationService(engine).upgrade()
    engine.dispose()


@pytest.fixture(scope="session")
def vacuum_db(engine_uri):
    def _vacuum(project):
        engine = create_engine(engine_uri)

        # ensure we delete all the tables
        metadata = MetaData(bind=engine)
        metadata.reflect()
        metadata.drop_all()

        # migrate back up
        migration_service = MigrationService(engine)
        migration_service.upgrade()
        migration_service.seed(project)

    return _vacuum


@pytest.fixture()
def engine_sessionmaker(project, engine_uri):
    # create the engine
    engine, sessionmaker = project_engine(project, engine_uri, default=True)

    return (engine, sessionmaker)


@pytest.fixture()
def session(project, engine_sessionmaker, vacuum_db):
    """Creates a new database session for a test."""
    engine, sessionmaker = engine_sessionmaker
    session = sessionmaker()

    try:
        yield session
    finally:
        # teardown
        session.close()
        vacuum_db(project)
