from flask import Blueprint, url_for, redirect, current_app, jsonify
from authlib.flask.client import OAuth as OAuthClient


OAuth = OAuthClient()


def facebook(app):
    OAuth.register(
        "facebook",
        access_token_url="https://graph.facebook.com/v5.0/oauth/access_token",
        client_kwargs={"scopes": "ads_read ads_management"},
        authorize_url="https://www.facebook.com/v5.0/dialog/oauth",
    )

    oauthBP = Blueprint("OAuth.Facebook", __name__, url_prefix="/oauth/facebook")

    @oauthBP.route("/login")
    def login():
        redirect_uri = url_for(".authorize", _external=True)
        return OAuth.facebook.authorize_redirect(redirect_uri)

    @oauthBP.route("/authorize")
    def authorize():
        token = OAuth.facebook.authorize_access_token()

        return jsonify(token)

    app.register_blueprint(oauthBP)
