"""OAuth providers."""

from __future__ import annotations

from authlib.integrations.flask_client import OAuth as OAuthClient
from flask import Blueprint, Flask, render_template, url_for

OAuth = OAuthClient()


def facebook(app: Flask) -> None:
    """Register OAuth for Facebook.

    Args:
        app: The Flask app for which the OAuth blueprint will be registered.
    """
    OAuth.register(  # noqa: S106
        "facebook",
        access_token_url="https://graph.facebook.com/v5.0/oauth/access_token",
        client_kwargs={"scope": "ads_read ads_management manage_pages"},
        authorize_url="https://www.facebook.com/v5.0/dialog/oauth",
    )

    oauth_bp = Blueprint("OAuth-Facebook", __name__, url_prefix="/facebook")

    @oauth_bp.route("/", strict_slashes=False)
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        return OAuth.facebook.authorize_redirect(
            redirect_uri, display="popup", auth_type="rerequest"
        )

    @oauth_bp.route("/authorize")
    def authorize():
        token = OAuth.facebook.authorize_access_token()
        return render_template("token.html", token=token["access_token"])

    app.register_blueprint(oauth_bp)


def google_adwords(app: Flask) -> None:
    """Register OAuth for Google AdWords.

    Args:
        app: The Flask app for which the OAuth blueprint will be registered.
    """
    OAuth.register(  # noqa: S106
        "google_adwords",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        client_kwargs={"scope": "https://www.googleapis.com/auth/adwords"},
        access_token_url="https://oauth2.googleapis.com/token",
    )

    oauth_bp = Blueprint("OAuth-GoogleAdwords", __name__, url_prefix="/google-adwords")

    @oauth_bp.route("/", strict_slashes=False)
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        # `consent` prompt is required to have a refresh_token
        # `offline` access_type is required to have a refresh_token
        return OAuth.google_adwords.authorize_redirect(
            redirect_uri, prompt="consent", access_type="offline"
        )

    @oauth_bp.route("/authorize")
    def authorize():
        token = OAuth.google_adwords.authorize_access_token()
        return render_template("token.html", token=token["refresh_token"])

    app.register_blueprint(oauth_bp)
