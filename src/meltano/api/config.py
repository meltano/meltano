import os
import logging
import datetime

from meltano.core.utils import truthy


# Flask
# -----------------
THREADS_PER_PAGE = 1
PROFILE = truthy(os.getenv("FLASK_PROFILE"))

## Change this value in production
SECRET_KEY = "thisisnotapropersecretkey"

# Meltano
# -----------------
MELTANO_AUTHENTICATION = truthy(os.getenv("MELTANO_AUTHENTICATION"))
MELTANO_UI_URL = os.getenv("MELTANO_UI_URL", "/")
MELTANO_READONLY = truthy(os.getenv("MELTANO_READONLY"))
AIRFLOW_DISABLED = truthy(os.getenv("MELTANO_DISABLE_AIRFLOW"))

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

JSON_SCHEME_HEADER = "X-JSON-SCHEME"
VERSION_HEADER = "X-MELTANO-VERSION"

# Flask-SQLAlchemy
# -----------------
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv("MELTANO_DATABASE_URI")

# Flask-security
# -----------------

# Change this value in production
# A better approach would be to have individual salts hashed resource
SECURITY_PASSWORD_SALT = "b4c124932584ad6e69f2774a0ae5c138"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_REGISTERABLE = False
SECURITY_CHANGEABLE = True
SECURITY_RECOVERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_URL_PREFIX = "/auth"
SECURITY_USER_IDENTITY_ATTRIBUTES = ("username", "email")
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

SECURITY_MSG_USERNAME_NOT_PROVIDED = ("You must provide a username.", "error")
SECURITY_MSG_USERNAME_INVALID = (
    "Username must be at least 6 characters long.",
    "error",
)
SECURITY_MSG_USERNAME_ALREADY_TAKEN = ("This username is already taken.", "error")

# Flask-Mail
# -----------------

# Change these configuration for your SMTP server
MAIL_SERVER = "localhost"
MAIL_PORT = 587
MAIL_DEFAULT_SENDER = '"Meltano" <bot@metlano.com>'

# Flask-Authlib
# -----------------

GITLAB_CLIENT_ID = os.getenv("OAUTH_GITLAB_APPLICATION_ID")
GITLAB_CLIENT_SECRET = os.getenv("OAUTH_GITLAB_SECRET")

# Flask-RESTful
# -----------------

RESTFUL_JSON = {}

# Flask-Executor
# -----------------

EXECUTOR_PROPAGATE_EXCEPTIONS = True


# Flask-CORS
# -----------------

CORS_EXPOSE_HEADERS = [VERSION_HEADER]
CORS_ALLOW_HEADERS = ["CONTENT-TYPE", JSON_SCHEME_HEADER]


class Production(object):
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


def ensure_secure_setup(app):
    secure_variables = ["SERVER_NAME", "SECRET_KEY", "SECURITY_PASSWORD_SALT"]

    facts = []
    for var in secure_variables:
        if app.config[var] is None:
            facts.append(f"\t- '{var}': variable is unset.")
        elif app.config[var] == globals().get(var):
            facts.append(f"\t- '{var}': variable has test value.")

    if facts:
        facts_msg = "\n".join(facts)
        logging.warning(
            "The following variables are insecure and should be regenerated:\n"
            f"{facts_msg}\n\n"
            "Use `meltano ui setup` command to generate new secrets."
        )
