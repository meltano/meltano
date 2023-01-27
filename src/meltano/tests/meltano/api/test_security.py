from __future__ import annotations

from datetime import datetime
from http import HTTPStatus

import mock
import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa: WPS436
from flask import url_for
from flask_login import current_user
from flask_security import AnonymousUser, login_user
from freezegun import freeze_time
from sqlalchemy.orm import joinedload

from meltano.api.models.oauth import OAuth
from meltano.api.models.security import User, db
from meltano.api.security.identity import FreeUser, users
from meltano.api.security.oauth import OAuthError, gitlab_token_identity
from meltano.core.project import PROJECT_READONLY_ENV, Project
from meltano.core.project_settings_service import ProjectSettingsService

STATUS_READONLY = 499


def gitlab_client():
    client_mock = mock.Mock()
    client_mock.auth.return_value = None
    user = mock.Mock(username="gitlabfan", email="valid@test.com", state="active", id=1)

    type(client_mock).user = mock.PropertyMock(return_value=user)

    return client_mock


class TestFreeUser:
    def test_all_roles(self):
        assert len(FreeUser().roles) == 2

        role = users.find_or_create_role("this_is_a_test")

        assert FreeUser().has_role(role)


@pytest.mark.usefixtures("seed_users")
class TestNothingEnabled:
    @pytest.fixture(scope="class")
    def app(self, create_app):
        return create_app()

    @pytest.fixture(autouse=True)
    def patch_hub(self, meltano_hub_service):
        with mock.patch(
            "meltano.core.project_plugins_service.MeltanoHubService",
            return_value=meltano_hub_service,
        ):
            yield

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), FreeUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.OK
            assert res.json["anonymous"] is True
            assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == HTTPStatus.CREATED
            assert res.data == b"Meltano update in progress."

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.OK
            assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == HTTPStatus.OK
            assert res.json["name"] == "tap-gitlab"


@pytest.mark.usefixtures("seed_users")
class TestProjectReadonlyEnabled:
    @pytest.fixture(scope="class")
    def project(self, project):
        Project.deactivate()

        monkeypatch = MonkeyPatch()
        monkeypatch.setenv(PROJECT_READONLY_ENV, "true")

        yield project

        monkeypatch.undo()

    @pytest.fixture(autouse=True)
    def patch_hub(self, meltano_hub_service):
        with mock.patch(
            "meltano.core.project_plugins_service.MeltanoHubService",
            return_value=meltano_hub_service,
        ):
            yield

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), FreeUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.OK
            assert res.json["anonymous"] is True
            assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == HTTPStatus.CREATED
            assert res.data == b"Meltano update in progress."

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.OK
            assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == STATUS_READONLY
            assert b"deployed as read-only" in res.data

    def test_pipeline_schedules_save(
        self, app, api, tap, target, project_plugins_service
    ):
        with app.test_request_context():
            with mock.patch(
                "meltano.core.schedule_service.ProjectPluginsService",
                return_value=project_plugins_service,
            ):
                res = api.post(
                    url_for("orchestrations.save_pipeline_schedule"),
                    json={
                        "name": "mock-to-mock",
                        "extractor": "tap-mock",
                        "loader": "target-mock",
                        "transform": "skip",
                        "interval": "@once",
                    },
                )

                assert res.status_code == STATUS_READONLY
                assert b"deployed as read-only" in res.data


@pytest.mark.usefixtures("seed_users")
class TestReadonlyEnabled:
    @pytest.fixture(scope="class")
    def app(self, create_app):
        monkeypatch = MonkeyPatch()
        monkeypatch.setitem(ProjectSettingsService.config_override, "ui.readonly", True)

        yield create_app()

        monkeypatch.undo()

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), FreeUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.OK
            assert res.json["anonymous"] is True
            assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == STATUS_READONLY
            assert b"read-only mode" in res.data

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.OK
            assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == STATUS_READONLY
            assert b"read-only mode" in res.data


@pytest.mark.usefixtures("seed_users")
class TestAuthenticationEnabled:
    @pytest.fixture(scope="class")
    def app(self, create_app):
        monkeypatch = MonkeyPatch()
        monkeypatch.setitem(
            ProjectSettingsService.config_override, "ui.authentication", True
        )

        yield create_app()

        monkeypatch.undo()

    @mock.patch("gitlab.Gitlab", return_value=gitlab_client())
    def test_gitlab_token_identity_creates_user(self, gitlab, app):
        token = {
            "access_token": "thisisavalidtoken",
            "id_token": "thisisavalidJWT",
            "created_at": 1548789020,
        }

        # test automatic user creation
        with app.test_request_context("/oauth/authorize"):
            identity = gitlab_token_identity(token)  # noqa: F841

            assert (
                db.session.query(OAuth)
                .options(joinedload(OAuth.user))
                .filter(
                    OAuth.access_token == token["access_token"]  # noqa: WPS222
                    and OAuth.id_token == token["id_token"]
                    and OAuth.provider_user_id == user.id  # noqa: F821
                    and OAuth.provider_id == "gitlab"
                    and User.email == user.email  # noqa: F821
                )
                .first()
            )

    @mock.patch("gitlab.Gitlab", return_value=gitlab_client())
    def test_gitlab_token_identity_maps_user(self, gitlab, app):
        token = {
            "access_token": "thisisavalidtoken",
            "id_token": "thisisavalidJWT",
            "created_at": 1548789020,
        }

        # test automatic user mapping
        with app.test_request_context("/oauth/authorize"):
            # let's create a user with the same email, that is currently logged
            user = users.create_user(email="valid@test.com")

            # but only if the user is currently logged (to prevent hi-jacking)
            with pytest.raises(OAuthError):
                identity = gitlab_token_identity(token)

            # the new identity should be mapped to the existing user
            login_user(user)
            identity = gitlab_token_identity(token)
            assert identity.user == user

    @freeze_time("2000-01-01")
    def test_login_audit_columns(self, app):
        with app.test_request_context():
            alice = users.get_user("alice")
            login_count = alice.login_count

            login_user(alice)

            # time is frozen, so it should work
            assert alice.last_login_at == datetime.utcnow()
            assert alice.login_count == login_count + 1

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), AnonymousUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_identity_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("api_root.identity"))

                assert res.status_code == HTTPStatus.OK
                assert res.json["username"] == "alice"
                assert res.json["anonymous"] is False
                assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location.startswith(url_for("security.login"))

    def test_bootstrap_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("root.bootstrap"))

                assert res.status_code == HTTPStatus.FOUND
                assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_upgrade_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(url_for("api_root.upgrade"))

                assert res.status_code == HTTPStatus.CREATED
                assert res.data == b"Meltano update in progress."

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_plugins_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("plugins.all"))

                assert res.status_code == HTTPStatus.OK
                assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_plugins_add_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(
                    url_for("plugins.add"),
                    json={"plugin_type": "extractors", "name": "tap-gitlab"},
                )

                assert res.status_code == HTTPStatus.OK
                assert res.json["name"] == "tap-gitlab"


@pytest.mark.usefixtures("seed_users")
class TestAuthenticationAndReadonlyEnabled:
    @pytest.fixture(scope="class")
    def app(self, create_app):
        monkeypatch = MonkeyPatch()

        config_override = ProjectSettingsService.config_override
        monkeypatch.setitem(config_override, "ui.authentication", True)
        monkeypatch.setitem(config_override, "ui.readonly", True)

        yield create_app()

        monkeypatch.undo()

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), AnonymousUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_identity_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("api_root.identity"))

                assert res.status_code == HTTPStatus.OK
                assert res.json["username"] == "alice"
                assert res.json["anonymous"] is False
                assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location.startswith(url_for("security.login"))

    def test_bootstrap_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("root.bootstrap"))

                assert res.status_code == HTTPStatus.FOUND
                assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_upgrade_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(url_for("api_root.upgrade"))

                assert res.status_code == STATUS_READONLY
                assert b"read-only mode" in res.data

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_plugins_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("plugins.all"))

                assert res.status_code == HTTPStatus.OK
                assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == HTTPStatus.UNAUTHORIZED
            assert res.data == b"Authentication is required to access this resource."

    def test_plugins_add_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(
                    url_for("plugins.add"),
                    json={"plugin_type": "extractors", "name": "tap-gitlab"},
                )

                assert res.status_code == STATUS_READONLY
                assert b"read-only mode" in res.data


@pytest.mark.usefixtures("seed_users")
class TestAuthenticationAndAnonymousReadonlyEnabled:
    @pytest.fixture(scope="class")
    def app(self, create_app):
        monkeypatch = MonkeyPatch()

        config_override = ProjectSettingsService.config_override
        monkeypatch.setitem(config_override, "ui.authentication", True)
        monkeypatch.setitem(config_override, "ui.anonymous_readonly", True)

        yield create_app()

        monkeypatch.undo()

    def test_current_user(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), AnonymousUser)

    def test_identity(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("api_root.identity"))

            assert res.status_code == HTTPStatus.OK
            assert res.json["anonymous"] is True
            assert res.json["can_sign_in"] is True

    def test_identity_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("api_root.identity"))

                assert res.status_code == HTTPStatus.OK
                assert res.json["username"] == "alice"
                assert res.json["anonymous"] is False
                assert res.json["can_sign_in"] is False

    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("root.bootstrap"))

            assert res.status_code == HTTPStatus.FOUND
            assert res.location == url_for("root.default")

    def test_bootstrap_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("root.bootstrap"))

                assert res.status_code == HTTPStatus.FOUND
                assert res.location == url_for("root.default")

    def test_upgrade(self, app, api):
        with app.test_request_context():
            res = api.post(url_for("api_root.upgrade"))

            assert res.status_code == HTTPStatus.FORBIDDEN
            assert res.data == b"You do not have the required permissions."

    def test_upgrade_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(url_for("api_root.upgrade"))

                assert res.status_code == HTTPStatus.CREATED
                assert res.data == b"Meltano update in progress."

    def test_plugins(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("plugins.all"))

            assert res.status_code == HTTPStatus.OK
            assert "extractors" in res.json

    def test_plugins_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("plugins.all"))

                assert res.status_code == HTTPStatus.OK
                assert "extractors" in res.json

    def test_plugins_add(self, app, api):
        with app.test_request_context():
            res = api.post(
                url_for("plugins.add"),
                json={"plugin_type": "extractors", "name": "tap-gitlab"},
            )

            assert res.status_code == STATUS_READONLY
            assert b"read-only mode until you sign in" in res.data

    def test_plugins_add_authenticated(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.post(
                    url_for("plugins.add"),
                    json={"plugin_type": "extractors", "name": "tap-gitlab"},
                )

                assert res.status_code == HTTPStatus.OK
                assert res.json["name"] == "tap-gitlab"
