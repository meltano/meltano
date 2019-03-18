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


@pytest.mark.usefixtures("project", "add_model")
class TestSqlController:
    @pytest.fixture
    def post(self, app, api):
        def _post(payload):
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
        }

        res = post(payload)
        assert res.status_code == 200, res.data
        assertIsSQL(res.json["sql"])
        assert 'EXTRACT(\'Week\' FROM "entry"."from") "from.week"' in res.json["sql"]
        assert re.search(r'GROUP BY.*"from.week"', res.json["sql"])

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
        }

        res = post(payload)

        assert res.status_code == 200
        assert (
            'SELECT "region"."dnoregion" "region.dnoregion" FROM "region" "region" GROUP BY "region.dnoregion" LIMIT 3;'
            in res.json["sql"]
        )

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
        }

        res = post(payload)

        assert res.status_code == 200
        sql = 'SELECT "region"."dnoregion" "region.dnoregion","entry"."forecast" "entry.forecast" FROM "region" "region" JOIN "entry" "entry" ON "region"."id"="entry"."region_id" GROUP BY "region.dnoregion","entry.forecast" LIMIT 3;'
        assert sql in res.json["sql"]

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
        }

        res = post(payload)

        assert res.status_code == 200
        sql = 'SELECT "region"."dnoregion" "region.dnoregion","entry"."forecast" "entry.forecast","generationmix"."fuel" "generationmix.fuel","generationmix"."perc" "generationmix.perc" FROM "region" "region" JOIN "entry" "entry" ON "region"."id"="entry"."region_id" JOIN "generationmix" "generationmix" ON "entry"."id"="generationmix"."entry_id" GROUP BY "region.dnoregion","entry.forecast","generationmix.fuel","generationmix.perc" LIMIT 3;'
        assert sql in res.json["sql"]

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
        }

        res = post(payload)

        assert res.status_code == 200
        sql = 'SELECT "region"."dnoregion" "region.dnoregion","generationmix"."fuel" "generationmix.fuel","generationmix"."perc" "generationmix.perc" FROM "region" "region" JOIN "entry" "entry" ON "region"."id"="entry"."region_id" JOIN "generationmix" "generationmix" ON "entry"."id"="generationmix"."entry_id" GROUP BY "region.dnoregion","generationmix.fuel","generationmix.perc" LIMIT 3;'
        assert sql in res.json["sql"]
