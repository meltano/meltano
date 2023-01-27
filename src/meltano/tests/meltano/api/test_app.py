from __future__ import annotations

import pytest

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


class TestAppSMTPDefault:
    DEFAULTS = {
        "MAIL_SERVER": "localhost",
        "MAIL_PORT": 1025,
        "MAIL_DEFAULT_SENDER": '"Meltano" <bot@meltano.com>',
        "MAIL_USE_TLS": False,
        "MAIL_USERNAME": None,
        "MAIL_PASSWORD": None,
        "MAIL_DEBUG": False,
    }

    def test_config_smtp_default(self, app):
        # ensure it is the defaults when not set
        assert self.DEFAULTS.items() <= app.config.items()


class TestAppSMTP:
    ENV = {
        "MELTANO_MAIL_SERVER": "smtp.localdomain",
        "MELTANO_MAIL_PORT": "1337",
        "MELTANO_MAIL_DEFAULT_SENDER": '"Doctor Who" <dr.who@localdomain.com>',
        "MELTANO_MAIL_USE_TLS": "1",
        "MELTANO_MAIL_USERNAME": "username",
        "MELTANO_MAIL_PASSWORD": "password",
        "MELTANO_MAIL_DEBUG": "0",
    }

    EXPECTED = {
        "MAIL_SERVER": "smtp.localdomain",
        "MAIL_PORT": 1337,
        "MAIL_DEFAULT_SENDER": '"Doctor Who" <dr.who@localdomain.com>',
        "MAIL_USE_TLS": True,
        "MAIL_USERNAME": "username",
        "MAIL_PASSWORD": "password",
        "MAIL_DEBUG": False,
    }

    @pytest.fixture
    def app(self, create_app, monkeypatch):
        # ensure the environment is properly loaded
        for env, value in self.ENV.items():
            monkeypatch.setenv(env, value)

        return create_app()

    def test_config_smtp(self, app):
        assert self.EXPECTED.items() <= app.config.items()
