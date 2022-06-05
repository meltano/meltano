
from flask_login import user_logged_in
from flask_principal import identity_loaded
from flask_security import Security

from meltano.core.project_settings_service import ProjectSettingsService

from .auth import (
    _identity_loaded_hook,
    _user_logged_in_hook,
    unauthorized_callback,
)
from .forms import MeltanoConfirmRegisterForm, MeltanoLoginForm, MeltanoRegisterFrom
from .identity import FreeUser, users

# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def setup_security(app, project):
    options = {
        "login_form": MeltanoLoginForm,
        "register_form": MeltanoRegisterFrom,
        "confirm_register_form": MeltanoConfirmRegisterForm,
    }

    settings_service = ProjectSettingsService(project)
    if not settings_service.get("ui.authentication"):
        # the FreeUser is free to do everything and has all
        # roles and permissions automatically.
        options["anonymous_user"] = FreeUser
    else:
        # Use Flask's built-in AnonymousUser which is not deemed to be authenticated
        # and has no roles
        pass

    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)
    user_logged_in.connect_via(app)(_user_logged_in_hook)
    identity_loaded.connect_via(app)(_identity_loaded_hook)
