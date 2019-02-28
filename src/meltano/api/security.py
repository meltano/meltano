from functools import wraps
from datetime import date
from flask import request, redirect, jsonify
from flask_login import current_user, login_user
from flask_security import (
    Security,
    AnonymousUser,
    auth_required,
    SQLAlchemyUserDatastore,
)
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, verify_jwt_refresh_token_in_request
)
from flask_security.utils import (
    login_user,
    get_identity_attributes,
    _datastore,
    get_message,
    hash_password,
)
from flask_security.forms import LoginForm, RegisterForm, ConfirmRegisterForm
from flask_jwt_extended import JWTManager, jwt_required
from flask_principal import identity_loaded, Permission, Need
from wtforms import StringField
from wtforms.validators import Required, ValidationError, Length

from .models import db, User, Role, RolePermissions


SEED_ROLES = [
    {
        "name": "admin",
        "_permissions": [
            {"type": "view:design", "context": "*"},
            {"type": "view:reports", "context": "*"},
            {"type": "modify:acl", "context": "*"},
        ],
    },
    {"name": "regular", "_permissions": []},
]

SEED_USERS = [
    {
        "username": "regular",
        "email": "regular@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),
        "_roles": {"regular"},
    },
    {
        "username": "admin",
        "email": "admin@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),
        "_roles": {"admin"},
    },
]


username_required = Required(message="USERNAME_NOT_PROVIDED")
username_validator = Length(min=6, max=32, message="USERNAME_INVALID")


def unique_username(form, field):
    if _datastore.get_user(field.data) is not None:
        msg = get_message("USERNAME_ALREADY_TAKEN", username=field.data)[0]
        raise ValidationError(msg)


class MeltanoLoginForm(LoginForm):
    email = StringField("Username or Email Address", validators=[Required()])


class UniqueUsernameMixin:
    username = StringField(
        "Username", validators=[username_required, username_validator, unique_username]
    )


class MeltanoConfirmRegisterForm(ConfirmRegisterForm, UniqueUsernameMixin):
    pass


class MeltanoRegisterFrom(RegisterForm, UniqueUsernameMixin):
    pass


class FreeUser(AnonymousUser):
    """FreeUser is free to do everything and has no limits."""

    def has_role(*args):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def id(self):
        return self.get_id()

    def get_id(self):
        return -1

    @property
    def roles(self):
        return set(Role.query.all())

    @roles.setter
    def roles(self, _):
        pass

    def get_auth_token(self):
        return None


users = SQLAlchemyUserDatastore(db, User, Role)

# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def create_dev_user():
    db.create_all()

    for role in SEED_ROLES:
        role = role.copy()
        role_name = role.pop("name")
        permissions = [RolePermissions(**perm) for perm in role.pop("_permissions")]

        role = users.find_or_create_role(role_name, **role, permissions=permissions)

    for user in SEED_USERS:
        user = user.copy()
        if users.get_user(user["email"]):
            continue

        roles = [users.find_or_create_role(r) for r in user.pop("_roles")]
        user["password"] = hash_password(user["password"])
        users.create_user(**user, roles=roles)

    db.session.commit()


def api_auth_required(f):
    auth_decorated = jwt_required(f)

    @wraps(f)
    def decorated():
        if request.method == "OPTIONS":
            return f()
        else:
            return auth_decorated()

    return decorated


def unauthorized_callback():
    """
    Meltano is mainly an API, so let's return plain 401
    instead of redirecting anywhere.
    """

    return "Unauthorized", 401


def _identity_loaded_hook(sender, identity):
    """
    Meltano uses a resource permission scheme.
    This hook will add the specific Permission
    to the current identity.
    """

    # each permission is a Need(permission_type, context),
    # i.e. ("view:design", "finance.*")
    permissions = [Need(perm.type, perm.context)
                   for role in current_user.roles
                   for perm in role.permissions]

    for perm in permissions:
        identity.provides.add(perm)


def init_app(app, project):
    options = {
        "login_form": MeltanoLoginForm,
        "register_form": MeltanoRegisterFrom,
        "confirm_register_form": MeltanoConfirmRegisterForm,
    }

    if app.env != "production":
        options["anonymous_user"] = FreeUser

    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)
    identity_loaded.connect_via(app)(_identity_loaded_hook)
    jwt = JWTManager(app)

    @jwt.user_loader_callback_loader
    def jwt_user_load(identity):
        user = users.find_user(id=identity["id"])
        login_user(user)

        return user

    bp = app.blueprints['security']

    # we need to add two JWT routes for the API

    @bp.route("/refresh_token")
    def refresh_token():
        if not verify_jwt_refresh_token_in_request():
            redirect(url_for(".login"))

        auth_identity = {
            "id": current_user.id,
            "username": current_user.username,
        }

        token = create_access_token(identity=auth_identity)
        return jsonify(auth_token=token)


    @bp.route("/bootstrap")
    def bootstrap_app():
        """Fire off the application with the current user logged in"""
        auth_identity = {
            "id": current_user.id,
            "username": current_user.username,
        }

        access_token = create_access_token(identity=auth_identity)
        refresh_token = create_refresh_token(identity=auth_identity)

        return redirect(f"http://localhost:8080?auth_token={access_token}&refresh_token={refresh_token}")

    app.register_blueprint(bp)
