from functools import wraps
from datetime import date
from flask_security import (
    Security,
    AnonymousUser,
    auth_required,
    SQLAlchemyUserDatastore,
)
from flask_security.utils import (
    login_user,
    get_identity_attributes,
    _datastore,
    get_message,
)
from flask_security.forms import LoginForm, RegisterForm, ConfirmRegisterForm
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
        users.create_user(**user, roles=roles)

    db.session.commit()


def api_auth_required(f):
    return auth_required("token", "session")(f)


def unauthorized_callback():
    """
    Meltano is mainly an API, so let's return plain 401
    instead of redirecting anywhere.
    """

    return "Unauthorized", 401


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
