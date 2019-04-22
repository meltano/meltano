import json
import pytest
from flask import url_for


def assert_has_items(entry, count):
    return len(entry["items"]) == count


def test_index(api, app):
    with app.test_request_context():
        res = api.get(url_for("repos.index"))

    payload = res.json

    assert_has_items(payload["tables"], 3)
    assert_has_items(payload["topics"], 1)
    assert_has_items(payload["dashboards"], 0)
    assert_has_items(payload["documents"], 1)


def test_models(api, app):
    with app.test_request_context():
        res = api.get(url_for("repos.models"))

    payload = res.json

    # we have topic
    assert payload.keys()

    # each topics has designs
    for topic_def in payload.values():
        assert topic_def["designs"]


def test_design_read(api, app):
    with app.test_request_context():
        res = api.get(
            url_for("repos.design_read", topic_name="carbon", design_name="region")
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
