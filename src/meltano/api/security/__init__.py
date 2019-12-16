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
        uri = app.config["MELTANO_UI_URL"]

        if not app.config["MELTANO_AUTHENTICATION"]:
            return redirect(uri)

        auth_identity = {"id": current_user.id, "username": current_user.username}
        access_token = create_access_token(identity=auth_identity)

        # split the token into two separate tokens
        # header.payload | signature
        header, payload, signature = access_token.split(".")

        # set the signature in a secure cookie
        res = make_response(redirect(uri + f"?auth_token={header}.{payload}"))
        set_access_cookies(res, access_token)

        # res.set_cookie("jwt_signature",
        #                value=signature,
        #                secure=False, # True for production,
        #                httponly=True)

        return res

    app.register_blueprint(bp)
