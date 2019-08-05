import pytest
from sqlalchemy import create_engine
from meltano.core.migration_service import MigrationService


@pytest.fixture(autouse=True)
def engine_uri_env(monkeypatch, engine_uri):
    monkeypatch.setenv("SQL_ENGINE_URI", engine_uri)


@pytest.fixture(scope="session", autouse=True)
def migrate(engine_uri):
    engine = create_engine(engine_uri)
    MigrationService(engine).upgrade()
    engine.dispose()
