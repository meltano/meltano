import re
from unittest import mock

import pytest
from flask import url_for

from support.payload_builder import PayloadBuilder

STATUS_OK = 200


@pytest.fixture()
def compile_models(api):
    api.get("/repos/sync")


def assert_is_sql(value: str) -> bool:
    assert re.match(
        r"SELECT.*FROM.*(JOIN.*)*(GROUP BY.*)?(LIMIT \d+)?", value
    ), f"{value} is not a SQL query."


def assert_list_equivalence(xs: list, ys: list):
    assert len(xs) == len(ys), "Both list should have the same size."
    assert set(xs) == set(ys)


@pytest.mark.usefixtures("project", "add_model", "elt_schedule")
class TestSqlController:

    STATUS_OK = 200

    @pytest.fixture
    def post(self, app, api, engine_sessionmaker):
        engine, _ = engine_sessionmaker

        @mock.patch(
            "meltano.api.controllers.sql.SqlHelper.get_db_engine", return_value=engine
        )
        def _post(payload, engine_mock):
            with app.test_request_context():
                return api.post(
                    self.url(app, "model-carbon-intensity", "carbon", "region"),
                    json=payload,
                )

        return _post

    @classmethod
    def url(cls, app, namespace, topic, design):
        return url_for(
            "sql.get_sql", namespace=namespace, topic_name=topic, design_name=design
        )

    def test_get_sql(self, post, payload_builder_factory):
        self.assert_empty_query(post, payload_builder_factory())
        self.assert_column_query(post, payload_builder_factory())
        self.assert_aggregate_query(post, payload_builder_factory())
        self.assert_timeframe_query(post, payload_builder_factory())

    @pytest.fixture
    def payload_builder_factory(self):
        def _factory():
            return PayloadBuilder("region", run=False, loader="target-mock")

        return _factory

    def assert_empty_query(self, post, payload_builder):
        """With no columns, aggregates or timeframes the response is No Content."""
        res = post(payload_builder.payload)
        assert res.status_code == 204  # noqa: WPS432

    def assert_column_query(self, post, payload_builder):
        """With columns they should be included in the query."""
        payload_builder.columns("name").columns("forecast", join="entry").columns(
            "perc", "fuel", join="generationmix"
        )
        res = post(payload_builder.payload)

        assert res.status_code == STATUS_OK
        assert_is_sql(res.json["sql"])

        # tests the label names
        assert_list_equivalence(
            [attr["attribute_label"] for attr in res.json["query_attributes"]],
            ["Region Name", "Forecast", "Percent (%)", "Fuel Type"],
        )

        # tests the column names
        assert_list_equivalence(
            [attr["attribute_name"] for attr in res.json["query_attributes"]],
            ["name", "forecast", "perc", "fuel"],
        )

    def assert_aggregate_query(self, post, payload_builder):
        """With aggregates they should be included in the query."""
        payload_builder.columns("name").aggregates("count")
        res = post(payload_builder.payload)

        assert res.status_code == STATUS_OK
        assert_is_sql(res.json["sql"])

        assert any(
            attr["id"] == "region.count" for attr in res.json["aggregates"]
        ), res.json

        assert_list_equivalence(
            [attr["attribute_name"] for attr in res.json["query_attributes"]],
            ["name", "count"],
        )

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
                    "aggregates": [],
                    "timeframes": [
                        {
                            "name": "from",
                            "periods": [{"label": "Week", "selected": True}],
                        },
                        {"name": "to", "periods": []},
                    ],
                },
                {
                    "name": "generationmix",
                    "columns": ["perc", "fuel"],
                    "aggregates": [],
                    "timeframes": [],
                },
            ],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "loader": "target-mock",
        }

        res = post(payload)

        assert res.status_code == STATUS_OK, res.data
        assert_is_sql(res.json["sql"])

        # tests label
        assert_list_equivalence(
            [attr["attribute_label"] for attr in res.json["query_attributes"]],
            ["Region Name", "Forecast", "From: Week", "Percent (%)", "Fuel Type"],
        )

        # tests column name
        assert_list_equivalence(
            [attr["attribute_name"] for attr in res.json["query_attributes"]],
            ["name", "forecast", "from.week", "perc", "fuel"],
        )
