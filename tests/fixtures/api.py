import pytest
from unittest import mock
from contextlib import contextmanager
from flask import request_started
from flask_security.utils import login_user, logout_user

import meltano.api.app
from meltano.api.security.identity import create_dev_user
from meltano.api.models import db


def _cleanup(app):
    with app.app_context():
        db.drop_all()


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


@pytest.fixture()
def app(create_app):
    return create_app()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def create_app(request, add_model, project):
    def _factory(**kwargs):
        config = {
            "TESTING": True,
            "LOGIN_DISABLED": False,
            "ENV": "test",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            **kwargs,
        }  # in-memory

        app = meltano.api.app.create_app(config)
        request.addfinalizer(lambda: _cleanup(app))

        with app.app_context():
            db.drop_all()
            db.create_all()
            create_dev_user()

        return app

    return _factory


@pytest.fixture
def api(app):
    return app.test_client()
