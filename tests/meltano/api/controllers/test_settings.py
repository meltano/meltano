import pytest
from flask import url_for
from meltano.api.security import users
from meltano.api.models.security import db, Role


class TestRoles:
    @pytest.fixture
    def app(self, create_app):
        return create_app(MELTANO_AUTHENTICATION=True)

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
            if status_code == 201:
                assert db.session.query(Role).filter_by(name="pytest").one()

    @pytest.mark.parametrize(
        "user,status_code", [("alice", 201), ("rob", 403), (None, 401)]
    )
    def test_assign_role(self, user, status_code, api, app, impersonate):
        with app.test_request_context():
            empty_user = users.create_user(username="pytest")

            # save the new user
            db.session.commit()

            with impersonate(users.get_user(user)):
                res = api.post(
                    url_for("settings.roles"),
                    json={"role": {"name": "pytest"}, "user": empty_user.username},
                )

            assert res.status_code == status_code, res.data
            if status_code == 201:
                db.session.add(empty_user)
                assert "pytest" in empty_user.roles

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

    @pytest.mark.parametrize(
        "user,status_code", [("alice", 201), ("rob", 403), (None, 401)]
    )
    def test_delete_role(self, user, status_code, api, app, impersonate):
        with app.test_request_context():
            fake_role = users.find_or_create_role(name="pytest")

            # save the new role
            db.session.commit()

            assert db.session.query(Role).filter_by(name="pytest").first()

            with impersonate(users.get_user(user)):
                res = api.delete(
                    url_for("settings.roles"), json={"role": {"name": "pytest"}}
                )

            assert res.status_code == status_code, res.data
            if res.status_code == 201:
                assert not db.session.query(Role).filter_by(name="pytest").first()

    @pytest.mark.parametrize(
        "user,status_code", [("alice", 201), ("rob", 403), (None, 401)]
    )
    def test_unassign_role(self, user, status_code, api, app, impersonate):
        with app.test_request_context():
            fake_role = users.find_or_create_role(name="pytest")
            empty_user = users.create_user(username="empty")
            users.add_role_to_user(empty_user, fake_role)

            # save the new user + role
            db.session.commit()

            # make sure the setup is valid
            assert fake_role in empty_user.roles

            with impersonate(users.get_user(user)):
                res = api.delete(
                    url_for("settings.roles"),
                    json={"role": {"name": "pytest"}, "user": empty_user.username},
                )

            assert res.status_code == status_code, res.data
            if res.status_code == 201:
                # refresh the instance
                empty_user = users.get_user(empty_user.username)
                assert fake_role not in empty_user.roles
