"""OAuth setup and utilities."""

from __future__ import annotations

import base64
import json

import gitlab
from authlib.integrations.flask_client import OAuth as OAuthClient
from flask import Blueprint, Flask, redirect, url_for
from flask_security import current_user
from flask_security.utils import do_flash, login_user, url_for_security
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from meltano.api.models.oauth import OAuth, db
from meltano.core.utils import compose

from .identity import FreeUser, users


class OAuthError(Exception):
    """Base exception class for OAuth exceptions."""


def base64_pad(unpadded: str) -> str:
    """Add padding to a base64-encoded string.

    Args:
        unpadded: The unpadded base64-encoded string.

    Returns:
        The padded base64-encoded string.
    """
    padding = 4 - (len(unpadded) % 4)
    return unpadded + ("=" * padding)


jwt_decode = compose(json.loads, base64.urlsafe_b64decode, base64_pad)


def setup_oauth_gitlab(oauth: OAuthClient) -> None:
    """Register OAuth for GitLab.

    Args:
        oauth: The `OAuthClient` which has a Flask app for which the OAuth
            blueprint will be registered.
    """
    oauth.register(  # noqa: S106
        "gitlab",
        access_token_url="https://gitlab.com/oauth/token",
        client_kwargs={"scope": "openid read_user"},
        authorize_url="https://gitlab.com/oauth/authorize",
    )

    oauth_bp = Blueprint("OAuth-GitLab", __name__, url_prefix="/oauth/gitlab")

    @oauth_bp.route("/login")
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        return oauth.gitlab.authorize_redirect(redirect_uri)

    @oauth_bp.route("/authorize")
    def authorize():
        token = oauth.gitlab.authorize_access_token()

        try:
            identity = gitlab_token_identity(token)
            login_user(identity.user, remember=False)
            return redirect(url_for("root.default"))
        except OAuthError as ex:
            do_flash(str(ex))
            return redirect(url_for_security("login"))

    oauth.app.register_blueprint(oauth_bp)


def setup_oauth(app: Flask) -> None:
    """Set up OAuth for the given Flask app.

    Args:
        app: The Flask app for which OAuth should be setup.
    """
    setup_oauth_gitlab(OAuthClient(app))


def gitlab_token_identity(token: dict[str, str]) -> OAuth:
    """Get an OAuth identity from a GitLab token.

    Args:
        token: A dictionary with the token keyed by 'access_token'.

    Raises:
        OAuthError: Unable to get the identity for the given token.

    Returns:
        The `OAuth` instance derived from the provided token.
    """
    # TODO: having to do another GET to grab the user info
    #       is subpar, but the returned JWT lacks the user's email
    #
    # It seems like validating the JWT token is not
    # currently working as the GitLab JWKs endpoint is unstable
    # See https://gitlab.com/gitlab-com/support-forum/issues/3666
    client = gitlab.Gitlab("http://gitlab.com", oauth_token=token["access_token"])
    client.auth()

    if client.user.state != "active":
        raise OAuthError("This account is not active.")

    token_user_email = users.get_user(client.user.email)
    token_user_username = users.get_user(client.user.username)

    if (
        token_user_email
        and token_user_username
        and token_user_email != token_user_username
    ):
        raise OAuthError(
            "This identity is already claimed by another user, please login."
        )
    else:
        token_user = token_user_email or token_user_username

    identity = None
    try:
        identity = (
            db.session.query(OAuth)
            .options(joinedload(OAuth.user))
            .filter_by(provider_id="gitlab", provider_user_id=client.user.id)
            .one()
        )
    except NoResultFound:
        identity = OAuth.from_token("gitlab", client.user.id, token)

    if current_user.is_authenticated and not isinstance(
        current_user._get_current_object(),  # noqa: WPS437
        FreeUser,
    ):
        # map the identity to the current_user
        identity.user = current_user
        db.session.add(identity)
    elif not token_user:  # noqa: WPS504
        # no user has claimed this email yet
        # reserve it
        token_user = users.create_user(
            username=client.user.username, email=client.user.email
        )
        identity.user = token_user
        db.session.add(identity)
    elif identity.user == token_user:
        # we have a match, a user with this email and identity
        # TODO: update the identity if need be
        pass
    else:
        raise OAuthError("This identity is already claimed by another user.")

    return identity
