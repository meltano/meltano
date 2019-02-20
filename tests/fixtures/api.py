import pytest

import meltano.api.app
from meltano.api.security import create_dev_user
from meltano.api.models import db


def _cleanup(app):
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def app(create_app):
    return create_app()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def create_app(request, project):
    def _factory(**config):
        config = {
            "TESTING": True,
            "ENV": "development",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            **config,
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
