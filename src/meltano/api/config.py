import os
import datetime

TRUTHY = ("True", "true", "1", "yes", "on")

# Flask
# -----------------
THREADS_PER_PAGE = 1
PROFILE = os.getenv("FLASK_PROFILE") in TRUTHY
ENV = os.getenv("FLASK_ENV", "development")

## Change this value in production
SECRET_KEY = "483be43cf29204e24d85cf711e36ea978a4d0ab316d8ecd7ae1ce5ecff3e29c1"

# Meltano
# -----------------
LOG_PATH = os.getenv("MELTANO_LOG_PATH", "meltano.log")
MELTANO_AUTHENTICATION = os.getenv("MELTANO_AUTHENTICATION") in TRUTHY
MELTANO_UI_URL = os.getenv("MELTANO_UI_URL", "")

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

# Flask-SQLAlchemy
# -----------------
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv("MELTANO_API_DATABASE_URI")

# Flask-security
# -----------------

# Change this value in production
# A better approach would be to have individual salts hashed resource
SECURITY_PASSWORD_SALT = "b4c124932584ad6e69f2774a0ae5c138"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_REGISTERABLE = True
SECURITY_CHANGEABLE = False
SECURITY_RECOVERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_URL_PREFIX = "/auth"
SECURITY_USER_IDENTITY_ATTRIBUTES = ("username", "email")

SECURITY_SEND_REGISTER_EMAIL = False

SECURITY_MSG_USERNAME_NOT_PROVIDED = ("You must provide a username.", "error")
SECURITY_MSG_USERNAME_INVALID = (
    "Username must be at least 6 characters long.",
    "error",
)
SECURITY_MSG_USERNAME_ALREADY_TAKEN = ("This username is already taken.", "error")

# Flask-JWT-Extended
# ------------------
JWT_SECRET_KEY = SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)

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
