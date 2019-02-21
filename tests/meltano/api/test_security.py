import pytest
import gitlab

from unittest import mock
from sqlalchemy.orm import joinedload
from meltano.api.security import AnonymousUser, FreeUser, users
from meltano.api.auth import gitlab_token_identity, OAuthError
from meltano.api.models import db, OAuth, User
from flask_login import current_user
from flask_security import login_user, logout_user


def gitlab_client():
    client_mock = mock.Mock()
    client_mock.auth.return_value = None
    user = mock.Mock(username="gitlabfan", email="valid@test.com", state="active", id=1)

    type(client_mock).user = mock.PropertyMock(return_value=user)

    return client_mock


class TestSecurity:
    @pytest.mark.parametrize(
        "flask_env,current_user_cls",
        [("development", FreeUser), ("production", AnonymousUser)],
    )
    def test_auth_mode(self, monkeypatch, create_app, flask_env, current_user_cls):
        monkeypatch.setenv("FLASK_ENV", flask_env)

        app = create_app()
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), current_user_cls)

    @mock.patch("gitlab.Gitlab", return_value=gitlab_client())
    @pytest.mark.usefixtures("app_context")
    def test_gitlab_token_identity_creates_user(self, gitlab, create_app):
        app = create_app(ENV="production")

        token = {
            "access_token": "thisisavalidtoken",
            "id_token": "thisisavalidJWT",
            "created_at": 1548789020,
        }

        # test automatic user creation
        with app.test_request_context("/oauth/authorize"):
            identity = gitlab_token_identity(token)

            assert (
                db.session.query(OAuth)
                .options(joinedload(OAuth.user))
                .filter(
                    OAuth.access_token == token["access_token"]
                    and OAuth.id_token == token["id_token"]
                    and OAuth.provider_user_id == user.id
                    and OAuth.provider_id == "gitlab"
                    and User.email == user.email
                )
                .first()
            )
            db.session.rollback()

    @mock.patch("gitlab.Gitlab", return_value=gitlab_client())
    @pytest.mark.usefixtures("app_context")
    def test_gitlab_token_identity_maps_user(self, gitlab, create_app):
        app = create_app(ENV="production")

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

    def test_roles_from_acl(self, app_context):
        assert users.get_user("admin@meltano.com").roles == ["admin"]
        assert users.get_user("regular@meltano.com").roles == ["regular"]

        # no permissions for `@gitlabfan`
        users.create_user(username="gitlabfan", email="gitlabfan@meltano.com")
        assert len(users.get_user("gitlabfan").roles) == 0
