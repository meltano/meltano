import pytest

import meltano.api.app
from meltano.api.models import db


@pytest.fixture()
def app(create_app):
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(scope="session")
def create_app():
    def _factory(config={}):
        config = {
            **config,
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }  # in-memory

        return meltano.api.app.create_app(config)

    return _factory


@pytest.fixture
def api(app):
    return app.test_client()
