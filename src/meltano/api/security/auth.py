from functools import wraps

from flask import request
from flask_security import auth_required
from flask_login import current_user
from flask_jwt_extended import jwt_required
from flask_principal import Permission, Need
from .identity import FreeUser


def api_auth_required(f):
    auth_decorated = jwt_required(f)

    @wraps(f)
    def decorated():
        if request.method == "OPTIONS":
            return f()

        session_user = current_user._get_current_object()
        if isinstance(session_user, FreeUser):
            return f()

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
