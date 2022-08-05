from __future__ import annotations

from flask import url_for


def test_get_default(api, app):
    with app.test_request_context():
        app_response = api.get(url_for("root.default"))
        res = api.get("/this/is__/a/__test")

        assert app_response.data == res.data


def test_get_health(api, app):
    with app.test_request_context():
        res = api.get(url_for("api_root.health"))

        assert res.status_code == 200
        assert res.json["healthy"]
