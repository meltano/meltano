import pytest
from flask import url_for


class TestRoles:
    def test_delete_admin_role(self, api, app):
        with app.test_request_context():
            res = api.delete(url_for("settings.roles"), json={
                "role": "admin",
            })

        assert res.status_code == 403
