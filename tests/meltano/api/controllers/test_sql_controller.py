import pytest
import re

from unittest import mock
from flask import url_for
from support.payload_builder import PayloadBuilder


@pytest.fixture()
def compile_models(api):
    api.get("/repos/sync")


def assertIsSQL(value: str) -> bool:
    assert (
        re.match(r"SELECT.*FROM.*(JOIN.*)*(GROUP BY.*)?(LIMIT \d+)?", value),
        f"{value} is not a SQL query.",
    )


def assertListEquivalence(xs: list, ys: list):
    assert len(xs) == len(ys), "Both list should have the same size."
    assert set(xs) == set(ys)


@pytest.mark.usefixtures("project", "add_model", "add_connection")
class TestSqlController:
    @pytest.fixture
    def post(self, app, api, engine_sessionmaker):
        engine, _ = engine_sessionmaker

        @mock.patch(
            "meltano.api.controllers.sql.SqlHelper.get_db_engine", return_value=engine
        )
        def _post(payload, engine_mock):
            return api.post(self.url(app, "carbon", "region"), json=payload)

        return _post

    @classmethod
    def url(cls, app, topic, design):
        with app.test_request_context():
            return url_for("sql.get_sql", topic_name=topic, design_name=design)

    def test_get_sql(self, post, payload_builder_factory):
        self.assert_empty_query(post, payload_builder_factory())
        self.assert_column_query(post, payload_builder_factory())
        self.assert_aggregate_query(post, payload_builder_factory())
        self.assert_timeframe_query(post, payload_builder_factory())

    @pytest.fixture
    def payload_builder_factory(self):
        def _factory():
            return PayloadBuilder("region", run=False, dialect="pytest")

        return _factory

    def assert_empty_query(self, post, payload_builder):
        """with no columns no query should be generated"""

        res = post(payload_builder.payload)
        assert res.status_code == 200, res.data
        assert res.json["sql"] == ""

    def assert_column_query(self, post, payload_builder):
        """with columns they should be included in the query"""

        payload_builder.columns("name").columns("forecast", join="entry").columns(
            "perc", "fuel", join="generationmix"
        )
        res = post(payload_builder.payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])
        assertListEquivalence(
            res.json["column_headers"], ["Name", "Forecast", "Percent (%)", "Fuel Type"]
        )
        assertListEquivalence(
            res.json["column_names"], ["name", "forecast", "perc", "fuel"]
        )

    def assert_aggregate_query(self, post, payload_builder):
        """with aggregates they should be included in the query"""

        payload_builder.columns("name").aggregates("count")
        res = post(payload_builder.payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert "region.count" in res.json["aggregates"]
        assertListEquivalence(res.json["column_names"], ["name", "count"])

    def assert_timeframe_query(self, post, payload_builder):
        payload = {
            "name": "region",
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
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200, res.data
        assertIsSQL(res.json["sql"])
        assertListEquivalence(
            res.json["column_headers"],
            ["Name", "Forecast", "entry.From (Week)", "Percent (%)", "Fuel Type"],
        )
        assertListEquivalence(
            res.json["column_names"],
            ["name", "forecast", "entry.from.week", "perc", "fuel"],
        )
