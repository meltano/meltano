from flask_security import Security, AnonymousUser, auth_required
from flask_security.datastore import SQLAlchemyDatastore, UserDatastore
from flask_security.utils import login_user, get_identity_attributes
from functools import wraps
from datetime import date

from meltano.core.compiler.acl_file import ACLFile
from .models import db, User


SEED_USERS = [
    {
        "username": "regular",
        "email": "regular@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),
    },
    {
        "username": "admin",
        "email": "admin@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),
    },
]


from flask_security.forms import LoginForm, RegisterForm, ConfirmRegisterForm
from wtforms import StringField
from wtforms.validators import Required, ValidationError, Length
from flask_security.utils import _datastore, get_message


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
    """FreeUser is free to do eveything and has no limits."""

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


class MeltanoUserDatastore(SQLAlchemyDatastore, UserDatastore):
    """
    Meltano uses the database to store the Users and OAuth
    informations.

    The Roles and mapping are fetched for the `acls.m5oc`
    file.

    See `meltano.core.compiler.acl_compiler.ACLFile` for more
    details.
    """

    def __init__(self, db, user_model, acl_file=None):
        self._acl_file = acl_file

        SQLAlchemyDatastore.__init__(self, db)
        UserDatastore.__init__(self, user_model, None)

    @property
    def acl_file(self):
        return self._acl_file

    def update_acl(self, acl_file):
        self._acl_file = acl_file

    def find_role(self, *args, **kwargs):
        name, *_ = args
        return self.acl_file.roles(name)

    def add_role_to_user(self, user, role):
        user.roles.add(role)

    def remove_role_from_user(self, user, role):
        user.roles.remove(role)

    def create_role(self, **kwargs):
        raise NotImplementedError

    def get_user(self, identifier):
        from sqlalchemy import func as alchemyFn

        user_model_query = self.user_model.query

        user = None

        # fetch by id
        if self._is_numeric(identifier):
            user = user_model_query.get(identifier)
        else:
            for attr in get_identity_attributes():
                query = alchemyFn.lower(
                    getattr(self.user_model, attr)
                ) == alchemyFn.lower(identifier)
                rv = user_model_query.filter(query).first()
                if rv is not None:
                    user = rv

        if user:
            self._assign_roles(user)

        return user

    def _is_numeric(self, value):
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        return True

    def find_user(self, **kwargs):
        query = self.user_model.query
        user = query.filter_by(**kwargs).first()
        self._assign_roles(user)

        return user

    def _assign_roles(self, user):
        if not user:
            return

        user.roles = set(
            role for role in self.acl_file.roles() if user.username in role.users
        )


users = MeltanoUserDatastore(db, User)

# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def create_dev_user():
    db.create_all()

    for user in SEED_USERS:
        if not users.get_user(user["email"]):
            users.create_user(**user)

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

    if app.env == "development":
        options["anonymous_user"] = FreeUser

    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)

    acl_file = ACLFile.load(project.run_dir("acls.m5oc").open())
    users.update_acl(acl_file)
