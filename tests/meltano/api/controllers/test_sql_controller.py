import pytest
import re

from unittest import mock
from flask import url_for


@pytest.fixture()
def compile_models(api):
    api.get("/repos/sync")


def assertIsSQL(value: str) -> bool:
    assert (
        re.match(r"SELECT.*FROM.*(JOIN.*)*(GROUP BY.*)?(LIMIT \d+)?", value),
        f"{value} is not a SQL query.",
    )


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

    def test_get_sql(self, post):
        self.assert_empty_query(post)
        self.assert_column_query(post)
        self.assert_aggregate_query(post)
        self.assert_timeframe_query(post)
        self.assert_join_graph_no_dependencies(post)
        self.assert_join_graph_one_dependency(post)
        self.assert_join_graph_two_dependency(post)
        self.assert_join_graph_derived_dependency(post)
        self.assert_no_join(post)
        self.assert_filters_no_join_query(post)
        self.assert_filters_hda_query(post)

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
            "dialect": "pytest",
        }

        res = post(payload)
        assert res.status_code == 200, res.data
        assert res.json["sql"] == ""

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
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])
        assert '"region.dnoregion"' in res.json["sql"]
        assert '"entry.forecast"' in res.json["sql"]
        assert '"generationmix.perc"' in res.json["sql"]
        assert '"generationmix.fuel"' in res.json["sql"]

    def assert_aggregate_query(self, post):
        """with aggregates they should be included in the query"""

        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": ["count"],
            "timeframes": [],
            "joins": [
                {"name": "entry", "columns": [], "aggregates": [], "timeframes": []},
                {"name": "generationmix", "columns": [], "aggregates": []},
            ],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])
        assert "region.count" in res.json["aggregates"]
        assert (
            '"region.dnoregion",COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region"'
            in res.json["sql"]
        )

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
            "dialect": "pytest",
        }

        res = post(payload)
        assert res.status_code == 200, res.data
        assertIsSQL(res.json["sql"])
        assert (
            'EXTRACT(\'WEEK\' FROM "entry"."from") "entry.from.week"' in res.json["sql"]
        )
        assert re.search(r'GROUP BY.*"entry.from.week"', res.json["sql"])

    def assert_join_graph_no_dependencies(self, post):
        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
            "joins": [],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert 'SELECT "region"."dnoregion" "region.dnoregion"' in res.json["sql"]
        assert 'FROM "region" "region"' in res.json["sql"]
        assert 'GROUP BY "region.dnoregion"' in res.json["sql"]
        assert 'ORDER BY "region.dnoregion" ASC' in res.json["sql"]

    def assert_join_graph_one_dependency(self, post):
        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
            "joins": [{"name": "entry", "columns": ["forecast"]}],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert (
            'SELECT "region"."dnoregion" "region.dnoregion","entry"."forecast" "entry.forecast"'
            in res.json["sql"]
        )
        assert 'FROM "region" "region"' in res.json["sql"]
        assert (
            'JOIN "entry" "entry" ON "region"."id"="entry"."region_id"'
            in res.json["sql"]
        )
        assert 'GROUP BY "region.dnoregion","entry.forecast"' in res.json["sql"]
        assert 'ORDER BY "region.dnoregion" ASC,"entry.forecast" ASC' in res.json["sql"]

    def assert_join_graph_two_dependency(self, post):
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
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert (
            'SELECT "region"."dnoregion" "region.dnoregion","entry"."forecast" "entry.forecast","generationmix"."perc" "generationmix.perc","generationmix"."fuel" "generationmix.fuel"'
            in res.json["sql"]
        )
        assert 'FROM "region" "region"' in res.json["sql"]
        assert (
            'JOIN "entry" "entry" ON "region"."id"="entry"."region_id" JOIN "generationmix" "generationmix" ON "entry"."id"="generationmix"."entry_id"'
            in res.json["sql"]
        )
        assert (
            'GROUP BY "region.dnoregion","entry.forecast","generationmix.perc","generationmix.fuel"'
            in res.json["sql"]
        )
        assert (
            'ORDER BY "region.dnoregion" ASC,"entry.forecast" ASC,"generationmix.perc" ASC,"generationmix.fuel" ASC'
            in res.json["sql"]
        )

    def assert_join_graph_derived_dependency(self, post):
        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
            "joins": [
                {"name": "entry", "columns": []},
                {"name": "generationmix", "columns": ["perc", "fuel"]},
            ],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert (
            'SELECT "region"."dnoregion" "region.dnoregion","generationmix"."perc" "generationmix.perc","generationmix"."fuel" "generationmix.fuel"'
            in res.json["sql"]
        )
        assert 'FROM "region" "region"' in res.json["sql"]
        assert (
            'JOIN "entry" "entry" ON "region"."id"="entry"."region_id" JOIN "generationmix" "generationmix" ON "entry"."id"="generationmix"."entry_id"'
            in res.json["sql"]
        )
        assert (
            'GROUP BY "region.dnoregion","generationmix.perc","generationmix.fuel"'
            in res.json["sql"]
        )
        assert (
            'ORDER BY "region.dnoregion" ASC,"generationmix.perc" ASC,"generationmix.fuel" ASC'
            in res.json["sql"]
        )

    def assert_no_join(self, post):
        payload = {
            "table": "region",
            "columns": ["name"],
            "aggregates": [],
            "timeframes": [],
            "joins": [],
            "order": None,
            "limit": 3,
            "filters": {},
            "run": False,
            "dialect": "pytest",
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        sql = 'SELECT "region"."dnoregion" "region.dnoregion" FROM "region" "region" GROUP BY "region.dnoregion" ORDER BY "region.dnoregion" ASC LIMIT 3;'
        assert sql in res.json["sql"]

    def assert_filters_no_join_query(self, post):
        payload = {
            "table": "region",
            "columns": ["name", "short_name"],
            "aggregates": ["count"],
            "timeframes": [],
            "joins": [],
            "order": None,
            "limit": 3,
            "filters": {
                "columns": [
                    {
                        "table_name": "region",
                        "name": "name",
                        "expression": "equal_to",
                        "value": "East of England",
                    },
                    {
                        "table_name": "region",
                        "name": "short_name",
                        "expression": "like",
                        "value": "%East%",
                    },
                ],
                "aggregates": [
                    {
                        "table_name": "region",
                        "name": "count",
                        "expression": "greater_than",
                        "value": 50,
                    }
                ],
            },
            "dialect": "pytest",
            "run": False,
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert (
            'SELECT "region"."dnoregion" "region.dnoregion","region"."shortname" "region.shortname",COALESCE(COUNT("region"."id"),0) "region.count"'
            in res.json["sql"]
        )
        assert 'FROM "region" "region"' in res.json["sql"]
        assert (
            'WHERE "region"."dnoregion"=\'East of England\' AND "region"."shortname" LIKE \'%East%\''
            in res.json["sql"]
        )
        assert 'GROUP BY "region.dnoregion","region.shortname"' in res.json["sql"]
        assert 'HAVING COALESCE(COUNT("region"."id"),0)>50 ' in res.json["sql"]
        assert (
            'ORDER BY "region.dnoregion" ASC,"region.shortname" ASC' in res.json["sql"]
        )

    def assert_filters_hda_query(self, post):
        payload = {
            "table": "region",
            "columns": ["name", "short_name"],
            "aggregates": ["count"],
            "timeframes": [],
            "joins": [
                {"name": "entry", "columns": ["forecast"]},
                {
                    "name": "generationmix",
                    "columns": ["perc", "fuel"],
                    "aggregates": ["avg_perc"],
                },
            ],
            "order": None,
            "limit": 3,
            "filters": {
                "columns": [
                    {
                        "table_name": "region",
                        "name": "name",
                        "expression": "less_than",
                        "value": "L",
                    },
                    {
                        "table_name": "entry",
                        "name": "forecast",
                        "expression": "is_null",
                        "value": "",
                    },
                    {
                        "table_name": "generationmix",
                        "name": "fuel",
                        "expression": "is_not_null",
                        "value": "",
                    },
                    {
                        "table_name": "generationmix",
                        "name": "perc",
                        "expression": "greater_or_equal_than",
                        "value": "10",
                    },
                ],
                "aggregates": [
                    {
                        "table_name": "region",
                        "name": "count",
                        "expression": "less_or_equal_than",
                        "value": 50,
                    },
                    {
                        "table_name": "generationmix",
                        "name": "avg_perc",
                        "expression": "greater_than",
                        "value": 15,
                    },
                ],
            },
            "dialect": "pytest",
            "run": False,
        }

        res = post(payload)

        assert res.status_code == 200
        assertIsSQL(res.json["sql"])

        assert (
            'WHERE "region"."dnoregion"<\'L\' AND "entry"."forecast" IS NULL AND "generationmix"."perc">=\'10\' AND NOT "generationmix"."fuel" IS NULL'
            in res.json["sql"]
        )
        assert 'HAVING COALESCE(COUNT("region.id"),0)<=50' in res.json["sql"]
        assert 'HAVING COALESCE(AVG("generationmix.perc"),0)>15' in res.json["sql"]
