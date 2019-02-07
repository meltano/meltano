import pytest
import re

from flask import url_for


@pytest.fixture()
def compile_models(api):
    api.get("/repos/sync")


def assertIsSQL(value: str) -> bool:
    assert (
        re.match(r"SELECT.*FROM.*(JOIN.*)*(GROUP BY.*)?(LIMIT \d+)?", value),
        f"{value} is not a SQL query.",
    )


@pytest.mark.usefixtures("compile_models")
class TestSqlController:
    @pytest.fixture
    def post(self, app, api):
        def _post(payload):
            return api.post(self.url(app, "carbon", "region"), json=payload)

        return _post

    @classmethod
    def url(cls, app, model, design):
        with app.test_request_context():
            return url_for("sql.get_sql", model_name=model, design_name=design)

    def test_get_sql(self, post):
        self.assert_empty_query(post)
        self.assert_column_query(post)
        self.assert_timeframe_query(post)

    def assert_empty_query(self, post):
        """with no columns no query should be generated"""

        payload = {
            "table": "region",
            "columns": [],
            "aggregates": [],
            "timeframes": [],
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

    def assert_column_query(self, post):
        """with columns they should be included in the query"""

        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
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

    def assert_timeframe_query(self, post):
        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
            "joins": [
                {
                    "name": "entry",
                    "columns": ["forecast"],
                    "timeframes": [
                        {
                            "name": "from",
                            "periods": [{"label": "Week", "selected": True}],
                        },
                        {"name": "to", "periods": []},
                    ],
                },
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
        assert 'EXTRACT(\'Week\' FROM "entry"."from") "from.week"' in res.json["sql"]
        assert re.search(r'GROUP BY.*"from.week"', res.json["sql"])
