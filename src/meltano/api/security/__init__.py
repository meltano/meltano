import urllib.parse
from datetime import timedelta
from functools import wraps
from flask import current_app, request, redirect, jsonify, make_response
from flask_login import current_user
from flask_security import Security, login_required
from flask_security.utils import login_user
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    set_access_cookies,
    get_jwt_identity,
    verify_jwt_refresh_token_in_request,
)
from flask_jwt_extended import JWTManager
from flask_principal import identity_loaded, Identity

from .identity import users, FreeUser, create_dev_user
from .forms import MeltanoLoginForm, MeltanoRegisterFrom, MeltanoConfirmRegisterForm
from .auth import unauthorized_callback, _identity_loaded_hook, api_auth_required


# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def setup_security(app, project):
    options = {
        "login_form": MeltanoLoginForm,
        "register_form": MeltanoRegisterFrom,
        "confirm_register_form": MeltanoConfirmRegisterForm,
    }

    if not app.config["MELTANO_AUTHENTICATION"]:
        # the FreeUser is free to do everything and has all
        # roles and permissions automatically.
        options["anonymous_user"] = FreeUser

    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)
    identity_loaded.connect_via(app)(_identity_loaded_hook)

    jwt = JWTManager(app)

    @jwt.user_loader_callback_loader
    def jwt_user_load(identity):
        user = users.find_user(id=identity["id"])

        # this sets the current user and extends the session
        login_user(user)

        return user

    bp = app.blueprints["security"]

    @bp.route("/bootstrap")
    @login_required
    def bootstrap_app():
        """Fire off the application with the current user logged in"""
        uri = urllib.parse.urlparse(app.config["MELTANO_UI_URL"])

        if not app.config["MELTANO_AUTHENTICATION"]:
            return redirect(urllib.parse.urlunparse(uri))

        auth_identity = {"id": current_user.id, "username": current_user.username}
        access_token = create_access_token(identity=auth_identity)

        # Split the token into its parts (header, payload, signature)
        # this enable us to send the public portion of the token
        # (header.payload) to the frontend without fearing a XSS
        # attacks: the token lacks the signature and therefore cannot
        # be used for authentication.
        #
        # However, it is still possible on the front-end to use its
        # payload to adapt the UI according to the capabilities found
        # inside the token.
        #
        # Even if the token would be tampered with, thus enabling more
        # features, these would only be cosmetic and the backend would
        # not authorize such actions.
        header, payload, signature = access_token.split(".")

        # add the `auth_token` parameter
        params = urllib.parse.parse_qs(uri.query)
        params["auth_token"] = f"{header}.{payload}"
        uri._replace(query=urllib.parse.urlencode(params, doseq=True))
        res = make_response(redirect(urllib.parse.urlunparse(uri)))

        # set the signature in a secure cookie
        set_access_cookies(res, access_token)

        return res

    app.register_blueprint(bp)
