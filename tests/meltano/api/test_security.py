import pytest
import gitlab
import urllib
from unittest import mock
from sqlalchemy.orm import joinedload
from meltano.api.security import FreeUser, users
from meltano.api.security.oauth import gitlab_token_identity, OAuthError
from meltano.api.models.security import db, User
from meltano.api.models.oauth import OAuth

from flask import url_for
from flask_login import current_user
from flask_security import login_user, logout_user, AnonymousUser


def gitlab_client():
    client_mock = mock.Mock()
    client_mock.auth.return_value = None
    user = mock.Mock(username="gitlabfan", email="valid@test.com", state="active", id=1)

    type(client_mock).user = mock.PropertyMock(return_value=user)

    return client_mock


class TestSecurity:
    @pytest.fixture
    def app(self, create_app):
        return create_app(MELTANO_AUTHENTICATION=True)

    def test_auth_mode(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), AnonymousUser)

    @mock.patch("gitlab.Gitlab", return_value=gitlab_client())
    def test_gitlab_token_identity_creates_user(self, gitlab, app):
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

    @pytest.mark.usefixtures("app_context")
    def test_bootstrap(self, app, api, impersonate):
        with app.test_request_context():
            with impersonate(users.get_user("alice")):
                res = api.get(url_for("security.bootstrap_app"))
                url = urllib.parse.urlparse(res.location)
                query = urllib.parse.parse_qs(url.query)

                assert res.status_code == 302
                assert url.netloc == "localhost"
                assert query["auth_token"]

    @pytest.mark.usefixtures("app_context")
    def test_bootstrap_unauthenticated(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("security.bootstrap_app"))
            url = urllib.parse.urlparse(res.location)

            assert res.status_code == 302
            assert res.location.startswith(url_for("security.login", _external=True))


class TestSingleUser:
    @pytest.fixture
    def app(self, create_app):
        return create_app(MELTANO_AUTHENTICATION=False)

    @pytest.mark.usefixtures("app_context")
    def test_free_user_all_roles(self):
        assert len(FreeUser().roles) == 2

        role = users.find_or_create_role("this_is_a_test")

        assert role in FreeUser().roles

    def test_auth_mode(self, app):
        with app.test_request_context("/"):
            assert isinstance(current_user._get_current_object(), FreeUser)

    @pytest.mark.usefixtures("app_context")
    def test_bootstrap(self, app, api):
        with app.test_request_context():
            res = api.get(url_for("security.bootstrap_app"))

            assert res.status_code == 302
            assert res.location == url_for("root.default", _external=True)
