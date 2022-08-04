from __future__ import annotations

from datetime import date

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from meltano.api.models.security import Role, User, db

users = SQLAlchemyUserDatastore(db, User, Role)


SEED_USERS = [
    {
        "username": "rob",
        "email": "rob@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),  # noqa: WPS432
        "_roles": {"regular"},
    },
    {
        "username": "alice",
        "email": "alice@meltano.com",
        "password": "meltano",
        "confirmed_at": date(2000, 1, 1),  # noqa: WPS432
        "_roles": {"admin"},
    },
]


class FreeUser:
    """A user that is free to do everything without limits.

    Even though this class overrides `flask_security`'s `AnonymousUser` it
    doesn't inherit from `AnonymousUser` to bypass some type check regarding
    the loading of the identity.
    """

    def has_role(*args):
        return True

    @property
    def username(self):
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def id(self):
        return self.get_id()

    def get_id(self):
        return None

    @property
    def roles(self):
        return set(Role.query.all())

    @roles.setter
    def roles(self, _):
        return None

    def get_auth_token(self):
        return None


def create_dev_user():
    for user in SEED_USERS:
        user = user.copy()
        if users.get_user(user["email"]):
            continue

        roles = [users.find_or_create_role(r) for r in user.pop("_roles")]
        user["password"] = hash_password(user["password"])
        users.create_user(**user, roles=roles)

    db.session.commit()
