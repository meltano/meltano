import pytest
from sqlalchemy import create_engine, MetaData
from meltano.core.migration_service import MigrationService


@pytest.fixture(autouse=True)
def engine_uri_env(monkeypatch, engine_uri):
    monkeypatch.setenv("MELTANO_DATABASE_URI", engine_uri)


@pytest.fixture(scope="session", autouse=True)
def migrate(engine_uri):
    engine = create_engine(engine_uri)
    MigrationService(engine).upgrade()
    engine.dispose()


@pytest.fixture(scope="session")
def vacuum_db(engine_uri):
    def _vacuum():
        engine = create_engine(engine_uri)

        # ensure we delete all the tables
        metadata = MetaData(bind=engine)
        metadata.reflect()
        metadata.drop_all()

        # migrate back up
        migration_service = MigrationService(engine)
        migration_service.upgrade()

    return _vacuum
