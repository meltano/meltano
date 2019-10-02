from meltano.core.db import project_engine
from meltano.api.models import db


class TestApp:
    def test_core_registered(self, app, project):
        engine, _ = project_engine(project)

        # ensure both the API and the meltano.core
        # are on the same database
        with app.app_context():
            assert engine.url == db.engine.url
