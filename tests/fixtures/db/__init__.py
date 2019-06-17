import pytest


@pytest.fixture(autouse=True)
def engine_uri_env(monkeypatch, engine_uri):
    monkeypatch.setenv("SQL_ENGINE_URI", engine_uri)
