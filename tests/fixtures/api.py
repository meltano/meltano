import pytest

import meltano.api.app
from meltano.api.models import db


@pytest.fixture()
def app(create_app):
    return create_app()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def api_db(request, app):
    db.drop_all()
    db.create_all()

    yield db

    db.drop_all()


@pytest.fixture()
def create_app():
    def _factory():
        config = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"}  # in-memory

        app = meltano.api.app.create_app(config)

        return app

    return _factory


@pytest.fixture
def api(app):
    return app.test_client()
