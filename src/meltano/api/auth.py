from authlib.flask.client import OAuth as OAuthClient
from flask import Blueprint, url_for, redirect, current_app
from flask_security import current_user, AnonymousUser
from flask_security.utils import login_user, do_flash, url_for_security
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from .security import users
from .models import db, OAuth
from meltano.core.utils import compose

import json
import base64
import gitlab


def base64_pad(s):
    padding = 4 - (len(s) % 4)
    return s + ("=" * padding)


jwt_decode = compose(json.loads, base64.urlsafe_b64decode, base64_pad)


application_id = "823737b8779edff4193f3fcb9a47988cf4932dbc428e77706f04b206c44ad61b"
secret = "def4bec76d470c7684b549946df0cb656c73712046abea3dd6dd89fdb32db662"

oauth = OAuthClient()
oauth.register(
    "gitlab",
    client_id=application_id,
    client_secret=secret,
    access_token_url="https://gitlab.com/oauth/token",
    client_kwargs={"scope": "openid read_user"},
    authorize_url="https://gitlab.com/oauth/authorize",
)


oauthBP = Blueprint("OAuth", __name__, url_prefix="/oauth")


@oauthBP.route("/login")
def login():
    redirect_uri = url_for(".authorize", _external=True)
    return oauth.gitlab.authorize_redirect(redirect_uri)


@oauthBP.route("/authorize")
def authorize():
    token = oauth.gitlab.authorize_access_token()

    # TODO: having to do another GET to grab the user info
    #       is subpar, but the returned JWT lacks the user's email
    #
    # It seems like validating the JWT token is not
    # currently working as the GitLab JWKs endpoint is unstable
    # See https://gitlab.com/gitlab-com/support-forum/issues/3666
    client = gitlab.Gitlab("http://gitlab.com", oauth_token=token["access_token"])
    client.auth()

    if client.user.state != "active":
        raise "Account is no longer active."

    user = current_user.is_authenticated and current_user
    token_user = users.get_user(client.user.email)

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

    if current_user.is_authenticated:
        # map the identity to the current_user
        identity.user = current_user
        db.session.add(identity)
    elif not token_user:
        # no user has claimed this email yet
        # reserve it
        token_user = users.create(email=client.user.email)
        identity.user = token_user
        db.session.add(identity)
    elif identity.user == token_user:
        # we have a match, a user with this email and identity
        # TODO: update the identity if need be
        pass
    else:
        do_flash("This identity is already claimed by another user.")
        return redirect(url_for_security("login"))

    db.session.commit()
    login_user(identity.user, remember=False)

    return redirect(url_for("root.analyze"))
