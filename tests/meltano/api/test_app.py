import pytest
from meltano.core.db import project_engine
from meltano.api.models import db


class TestApp:
    @pytest.fixture
    def session(self):
        # disable the `session` fixture not to override
        # the `db.session`
        pass

    def test_core_registered(self, engine_sessionmaker, app):
        engine, _ = engine_sessionmaker

        # ensure both the API and the meltano.core
        # are on the same database
        assert engine.url == db.engine.url
