import pytest
import hashlib
from flask import url_for


def test_get_default(api, app):
    with app.test_request_context():
        app_response = api.get(url_for("root.default"))
        res = api.get("/this/is__/a/__test")

        assert app_response.data == res.data
