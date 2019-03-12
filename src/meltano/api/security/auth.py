import logging
from fnmatch import fnmatch
from functools import wraps

from flask import request
from flask_security import auth_required
from flask_login import current_user
from flask_jwt_extended import jwt_required
from flask_principal import Permission, Need
from werkzeug.exceptions import Forbidden
from .identity import FreeUser
from meltano.api.models import db


class ResourcePermission(Permission):
    def in_scope(self, need, scopes):
        matches = (fnmatch(need.value, scope.value) for scope in scopes)

        return any(matches)

    def allows(self, identity):
        logging.debug(f"Authorizing {self} using {identity}")
        needs_scoped = []
        for need in self.needs:
            # included
            scopes = (
                scope for scope in identity.provides if scope.method == need.method
            )

            scoped = self.in_scope(need, scopes)
            needs_scoped.append(scoped)

        for excluded in self.excludes:
            # excluded
            scopes = (
                scope for scope in identity.provides if scope.method == excluded.method
            )

            if self.in_scope(need, scopes):
                return False

        if all(needs_scoped):
            return True

        return False


def permission_for(permission_type, context):
    return ResourcePermission(Need(permission_type, context))


def permit(permission_type, context):
    if not permission_for(permission_type, context).can():
        raise Forbidden()


def api_auth_required(f):
    auth_decorated = jwt_required(f)

    @wraps(f)
    def decorated():
        if request.method == "OPTIONS":
            return f()

        session_user = current_user._get_current_object()
        if isinstance(session_user, FreeUser):
            logging.debug(f"Authentication bypassed`")
            return f()

        if session_user.is_authenticated:
            logging.debug(f"@{session_user.username} authenticated via `session`")
            return f()

        logging.debug("JWT authentication pending")
        return auth_decorated()

    return decorated


def unauthorized_callback():
    """
    Meltano is mainly an API, so let's return plain 403 (Forbidden)
    instead of redirecting anywhere.
    """

    return "You do not have the required permissions.", 403


def _identity_loaded_hook(sender, identity):
    """
    Meltano uses a resource permission scheme.
    This hook will add the specific Permission
    to the current identity.
    """

    # something weird is going on here when testing
    # SQLAlchemy complains about the roles not being
    # in a session.
    for role in current_user.roles:
        db.session.add(role)

    # each permission is a Need(permission_type, context),
    # i.e. ("view", "finance.*", "design")
    for perm in (perm for role in current_user.roles for perm in role.permissions):
        perm = Need(perm.type, perm.context)

        identity.provides.add(perm)
