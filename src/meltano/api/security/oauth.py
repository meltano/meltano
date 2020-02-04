import json
import base64
import gitlab
from authlib.flask.client import OAuth as OAuthClient
from flask import Blueprint, url_for, redirect, current_app, jsonify
from flask_security import current_user, AnonymousUser
from flask_security.utils import login_user, do_flash, url_for_security
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from .identity import users, FreeUser
from meltano.api.models.oauth import db, OAuth
from meltano.core.utils import compose


class OAuthError(Exception):
    pass


def base64_pad(s):
    padding = 4 - (len(s) % 4)
    return s + ("=" * padding)


jwt_decode = compose(json.loads, base64.urlsafe_b64decode, base64_pad)


def setup_oauth_gitlab(oauth):
    oauth.register(
        "gitlab",
        access_token_url="https://gitlab.com/oauth/token",
        client_kwargs={"scope": "openid read_user"},
        authorize_url="https://gitlab.com/oauth/authorize",
    )

    oauthBP = Blueprint("OAuth.GitLab", __name__, url_prefix="/oauth/gitlab")

    @oauthBP.route("/login")
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        return oauth.gitlab.authorize_redirect(redirect_uri)

    @oauthBP.route("/authorize")
    def authorize():
        token = oauth.gitlab.authorize_access_token()

        try:
            identity = gitlab_token_identity(token)
            login_user(identity.user, remember=False)

            return redirect(url_for("root.default"))
        except OAuthError as e:
            do_flash(str(e))
            return redirect(url_for_security("login"))

    oauth.app.register_blueprint(oauthBP)


def setup_oauth(app):
    oauth = OAuthClient(app)
    setup_oauth_gitlab(oauth)


def gitlab_token_identity(token):
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
        current_user._get_current_object(), FreeUser
    ):
        # map the identity to the current_user
        identity.user = current_user
        db.session.add(identity)
    elif not token_user:
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
