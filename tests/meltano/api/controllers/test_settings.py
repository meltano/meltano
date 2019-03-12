import pytest
from flask import url_for
from meltano.api.security import users


@pytest.fixture
def app(create_app):
    return create_app(MELTANO_AUTHENTICATION=True)


class TestRoles:
    @pytest.mark.parametrize(
        "user,status_code", [("alice", 201), ("rob", 403), (None, 401)]
    )
    def test_create_role(self, user, status_code, api, app, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user(user)):
                res = api.post(
                    url_for("settings.roles"), json={"role": {"name": "pytest"}}
                )

        assert res.status_code == status_code, res.data

    @pytest.mark.parametrize(
        "user,status_code", [("alice", 403), ("rob", 403), (None, 401)]
    )
    def test_delete_admin_role(self, user, status_code, api, app, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user(user)):
                res = api.delete(
                    url_for("settings.roles"), json={"role": {"name": "admin"}}
                )

        assert res.status_code == status_code, res.data
