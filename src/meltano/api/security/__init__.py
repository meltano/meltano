from __future__ import annotations

from flask_login import user_logged_in
from flask_principal import identity_loaded

from meltano.core.project_settings_service import ProjectSettingsService

from .auth import (  # noqa: WPS450
    _identity_loaded_hook,
    _user_logged_in_hook,
    unauthorized_callback,
)


def setup_security(app, project):
    from meltano.api.security.forms import (
        MeltanoConfirmRegisterForm,
        MeltanoLoginForm,
        MeltanoRegisterFrom,
    )
    from meltano.api.security.identity import FreeUser, users

    options = {
        "login_form": MeltanoLoginForm,
        "register_form": MeltanoRegisterFrom,
        "confirm_register_form": MeltanoConfirmRegisterForm,
    }

    settings_service = ProjectSettingsService(project)
    if not settings_service.get("ui.authentication"):
        options["anonymous_user"] = FreeUser
    # Else: use Flask's built-in AnonymousUser, which is not deemed to be
    # authenticated and has no roles.

    from flask_security import Security

    security = Security()
    # normally one would setup the extension accordingly, but it
    # seems Security.init_app() overwrites all the configuration
    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)
    user_logged_in.connect_via(app)(_user_logged_in_hook)
    identity_loaded.connect_via(app)(_identity_loaded_hook)
