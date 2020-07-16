import logging
from fnmatch import fnmatch
from functools import wraps
from datetime import datetime

from flask import current_app, request, jsonify
from flask_security import auth_required
from flask_login import current_user
from flask_principal import Permission, Need
from werkzeug.exceptions import Forbidden

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.api.models import db
from .identity import FreeUser

HTTP_READONLY_CODE = 499


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
                scope
                for scope in identity.provides
                if fnmatch(need.method, scope.method)
            )
            logging.debug(f"Found include scope {scopes} in {identity}")

            scoped = self.in_scope(need, scopes)
            needs_scoped.append(scoped)

        for excluded in self.excludes:
            # excluded
            scopes = (
                scope
                for scope in identity.provides
                if fnmatch(excluded.method, scope.method)
            )
            logging.debug(f"Found exclude scope {scopes} in {identity}")

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


def passes_authentication_checks():
    project = Project.find()
    settings_service = ProjectSettingsService(project)

    if not settings_service.get("ui.authentication"):
        logging.debug(f"Authentication not required because it's disabled")
        return True

    if current_user.is_authenticated:
        logging.debug(f"Authenticated as '{current_user.username}'")
        return True

    if settings_service.get("ui.anonymous_readonly") and current_user.is_anonymous:
        # The `@roles_required("admin")` and `@block_if_readonly` checks
        # will take care of enforcing authentication as appropriate
        logging.debug(
            f"Authentication not required because anonymous users have read-only access"
        )
        return True

    return False


def block_if_api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS" or passes_authentication_checks():
            return f(*args, **kwargs)

        return "Authentication is required to access this resource.", 401

    return decorated


def block_if_readonly(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        project = Project.find()
        settings_service = ProjectSettingsService(project)

        if settings_service.get("ui.readonly"):
            return (
                jsonify(
                    {"error": True, "code": "Meltano UI is running in read-only mode"}
                ),
                HTTP_READONLY_CODE,
            )

        if settings_service.get("ui.anonymous_readonly") and current_user.is_anonymous:
            return (
                jsonify(
                    {
                        "error": True,
                        "code": "Meltano UI is running in read-only mode until you sign in",
                    }
                ),
                HTTP_READONLY_CODE,
            )

        return f(*args, **kwargs)

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


def _user_logged_in_hook(sender, user):
    """
    Update the audit columns for the User
    """
    user.last_login_at = datetime.utcnow()
    user.last_activity_at = datetime.utcnow()
    user.login_count += 1
