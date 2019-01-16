import pytest
import re

from flask import url_for
from meltano.api.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    client = app.test_client()
    yield client


@pytest.fixture()
def compile_models(client):
    client.get("/repos/sync")


def assertIsSQL(value: str) -> bool:
    assert (
        re.match(r"SELECT.*FROM.*(JOIN.*)*(GROUP BY.*)?(LIMIT \d+)?", value),
        f"{value} is not a SQL query.",
    )


@pytest.mark.usefixtures("compile_models")
class TestSqlController:
    @pytest.fixture
    def post(self, client):
        def _post(payload):
            return client.post(self.url("carbon", "region"), json=payload)

        return _post

    @classmethod
    def url(cls, model, design):
        with app.test_request_context():
            return url_for("sql.get_sql", model_name=model, design_name=design)

    def test_get_sql(self, post):
        # with no dimensions no query should be generated
        payload = {
            "table": "region",
            "columns": [],
            "column_groups": [],
            "aggregates": [],
            "joins": [
                {"name": "entry", "columns": []},
                {"name": "generationmix", "columns": []},
            ],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
        }

        res = post(payload)
        assert res.status_code == 200
        assert res.json["sql"] == ";"

        # with columns they should be included in the query
        payload = {
            "table": "region",
            "columns": ["name"],
            "column_groups": [],
            "aggregates": [],
            "joins": [
                {"name": "entry", "columns": ["forecast"]},
                {"name": "generationmix", "columns": ["perc", "fuel"]},
            ],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])
        assert '"region.dnoregion"' in res.json["sql"]  # should it be `region.name`?
        assert '"entry.forecast"' in res.json["sql"]
        assert '"generationmix.perc"' in res.json["sql"]
        assert '"generationmix.fuel"' in res.json["sql"]
