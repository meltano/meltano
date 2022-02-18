from contextlib import contextmanager
from unittest import mock

import pytest
from flask import request_started
from flask_security.utils import login_user, logout_user
from sqlalchemy import MetaData

import meltano.api.app
from meltano.api.models import db as _db
from meltano.api.security.identity import create_dev_user
from meltano.core.migration_service import MigrationService


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


@pytest.fixture(scope="class")
def create_app(request, project, vacuum_db):
    def _factory(**kwargs):
        config = {"TESTING": True, "LOGIN_DISABLED": False, "ENV": "test", **kwargs}

        app = meltano.api.app.create_app(config)

        # let's push an application context so the
        # `current_app` is ready in each test
        ctx = app.app_context()
        ctx.push()

        # let's make sure to pop the context at the end
        request.addfinalizer(lambda: ctx.pop())

        return app

    return _factory


@pytest.fixture()
def api(app):
    return app.test_client()


@pytest.fixture()
def seed_users(app, session):
    create_dev_user()
