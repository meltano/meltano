import os
from dotenv import load_dotenv

load_dotenv()

# Flask
# -----------------
THREADS_PER_PAGE = 1
PROFILE = os.getenv("FLASK_PROFILE", False) in ("True", "true", "1")

# Change this value in production
SECRET_KEY = "483be43cf29204e24d85cf711e36ea978a4d0ab316d8ecd7ae1ce5ecff3e29c1"
JWT_SECRET_KEY = SECRET_KEY

# Meltano
# -----------------
LOG_PATH = os.getenv("MELTANO_LOG_PATH", "meltano.log")
ENV = os.getenv("FLASK_ENV", "development")

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

MELTANO_UI_URL = os.getenv("MELTANO_UI_URL", "")

# Flask-SQLAlchemy
# -----------------
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = "sqlite:///meltano.db"

# Flask-security
# -----------------

# Change this value in production
SECURITY_PASSWORD_SALT = "b4c124932584ad6e69f2774a0ae5c138"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_REGISTERABLE = True
SECURITY_CHANGEABLE = False
SECURITY_RECOVERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_URL_PREFIX = "/auth"
SECURITY_USER_IDENTITY_ATTRIBUTES = ("username", "email")

SECURITY_SEND_REGISTER_EMAIL = False

LOGIN_URL = SECURITY_URL_PREFIX + "/login"
LOGOUT_URL = SECURITY_URL_PREFIX + "/logout"
REGISTER_URL = SECURITY_URL_PREFIX + "/register"
RESET_URL = SECURITY_URL_PREFIX + "/reset"
CHANGE_URL = SECURITY_URL_PREFIX + "/change"
CONFIRM_URL = SECURITY_URL_PREFIX + "/confirm"

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
