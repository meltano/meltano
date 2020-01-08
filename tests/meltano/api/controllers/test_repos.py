import json
import pytest
from flask import url_for


def assert_has_items(entry, count):
    return len(entry["items"]) == count


@pytest.mark.usefixtures("add_model", "seed_users")
class TestRepos:
    def test_index(self, api, app):
        with app.test_request_context():
            res = api.get(url_for("repos.index"))

        payload = res.json

        assert_has_items(payload["tables"], 3)
        assert_has_items(payload["topics"], 1)
        assert_has_items(payload["dashboards"], 0)
        assert_has_items(payload["documents"], 1)

    def test_models(self, api, app):
        with app.test_request_context():
            res = api.get(url_for("repos.models"))

        payload = res.json

        # we have topics
        topic_identifiers = payload.keys()
        assert topic_identifiers
        assert "model-carbon-intensity/carbon" in topic_identifiers
        assert "model-gitlab/gitlab" in topic_identifiers

        # each topic has a name, a namespace and designs
        for topic_def in payload.values():
            assert topic_def["namespace"]
            assert topic_def["name"]
            assert topic_def["designs"]

    def test_design_read(self, api, app):
        with app.test_request_context():
            res = api.get(
                url_for(
                    "repos.design_read",
                    namespace="model-carbon-intensity",
                    topic_name="carbon",
                    design_name="region",
                )
            )

        json_data = json.loads(res.data)

        assert "description" in json_data
        assert "from" in json_data
        assert "graph" in json_data
        assert "joins" in json_data
        assert "label" in json_data
        assert "name" in json_data
        assert "related_table" in json_data

        assert json_data["from"] == "region"
        assert json_data["name"] == "region"
