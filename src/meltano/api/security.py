from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    AnonymousUser,
    auth_required,
)
from flask_security.utils import login_user
from functools import wraps

from .models import db, User, Role

users = SQLAlchemyUserDatastore(db, User, Role)

DEV_USER = {"email": "dev@meltano.com", "password": "meltano"}


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


# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def create_dev_user():
    db.create_all()
    if not users.get_user(DEV_USER["email"]):
        users.create_user(**DEV_USER)

    db.session.commit()


def api_auth_required(f):
    return auth_required("token", "session")(f)
