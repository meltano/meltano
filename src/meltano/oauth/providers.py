from flask import Blueprint, url_for, redirect, render_template, jsonify
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

    @oauthBP.route("/")
    def login():
        redirect_uri = url_for(".authorize", _external=True)

        return OAuth.facebook.authorize_redirect(redirect_uri, auth_type="rerequest")

    @oauthBP.route("/authorize")
    def authorize():
        token = OAuth.facebook.authorize_access_token()

        return render_template("token.html", token=token)

    app.register_blueprint(oauthBP)
