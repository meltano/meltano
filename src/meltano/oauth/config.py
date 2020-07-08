import os
from secrets import token_hex

from meltano.api.config import ProjectSettings as APIProjectSettings

# session are used internally to verify the tokens
SECRET_KEY = token_hex(64)


class ProjectSettings(APIProjectSettings):
    settings_map = {
        "SERVER_NAME": "ui.server_name",
        "SESSION_COOKIE_DOMAIN": "ui.session_cookie_domain",
        # Flask-Authlib
        "FACEBOOK_CLIENT_ID": "oauth_service.facebook.client_id",
        "FACEBOOK_CLIENT_SECRET": "oauth_service.facebook.client_secret",
        "GOOGLE_ADWORDS_CLIENT_ID": "oauth_service.google_adwords.client_id",
        "GOOGLE_ADWORDS_CLIENT_SECRET": "oauth_service.google_adwords.client_secret",
    }
