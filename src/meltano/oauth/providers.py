import logging
from flask import Blueprint, request, url_for, redirect, render_template, jsonify
from authlib.flask.client import OAuth as OAuthClient


OAuth = OAuthClient()


def facebook(app):
    OAuth.register(
        "facebook",
        access_token_url="https://graph.facebook.com/v5.0/oauth/access_token",
        client_kwargs={"scope": "ads_read ads_management manage_pages"},
        authorize_url="https://www.facebook.com/v5.0/dialog/oauth",
    )

    oauthBP = Blueprint("OAuth.Facebook", __name__, url_prefix="/facebook")

    @oauthBP.route("/", strict_slashes=False)
    def login():
        redirect_uri = url_for(".authorize", _external=True)

        return OAuth.facebook.authorize_redirect(
            redirect_uri, display="popup", auth_type="rerequest"
        )

    @oauthBP.route("/authorize")
    def authorize():
        token = OAuth.facebook.authorize_access_token()

        return render_template("token.html", token=token["access_token"])

    app.register_blueprint(oauthBP)


def google_adwords(app):
    OAuth.register(
        "google_adwords",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        client_kwargs={"scope": "https://www.googleapis.com/auth/adwords"},
        access_token_url="https://oauth2.googleapis.com/token",
    )

    oauthBP = Blueprint("OAuth.GoogleAdwords", __name__, url_prefix="/google-adwords")

    @oauthBP.route("/", strict_slashes=False)
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        # `consent` prompt is required to have a refresh_token
        # `offline` access_type is required to have a refresh_token
        redirect = OAuth.google_adwords.authorize_redirect(
            redirect_uri, prompt="consent", access_type="offline"
        )
        return redirect

    @oauthBP.route("/authorize")
    def authorize():
        token = OAuth.google_adwords.authorize_access_token()

        return render_template("token.html", token=token["refresh_token"])

    app.register_blueprint(oauthBP)
