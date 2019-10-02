import pytest
from unittest import mock
from contextlib import contextmanager
from flask import request_started
from flask_security.utils import login_user, logout_user
from sqlalchemy import MetaData

import meltano.api.app
from meltano.core.migration_service import MigrationService
from meltano.api.security.identity import create_dev_user
from meltano.api.models import db


@pytest.fixture
def impersonate(app):
    @contextmanager
    def factory(user):
        def push(sender):
            if user:
                login_user(user)
            else:
                logout_user()

        with request_started.connected_to(push):
            yield

    return factory


@pytest.fixture(scope="class")
def app(create_app):
    return create_app()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(scope="class")
def create_app(request, project, engine_uri, vacuum_db):
    def _factory(**kwargs):
        config = {
            "TESTING": True,
            "LOGIN_DISABLED": False,
            "ENV": "test",
            "SQLALCHEMY_DATABASE_URI": engine_uri,
            **kwargs,
        }

        def _cleanup(ctx):
            db.session.rollback()

        app = meltano.api.app.create_app(config)
        app.teardown_request(_cleanup)

        with app.app_context():
            vacuum_db(project)
            create_dev_user()

        return app

    return _factory


@pytest.fixture()
def api(app):
    return app.test_client()
