import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("MELTANO_LOG_PATH", "meltano.log")
ENV = "development"

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = "sqlite:///meltano_api.db"

# Flask-security
SECURITY_PASSWORD_SALT = "b4c124932584ad6e69f2774a0ae5c138"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_REGISTERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_URL_PREFIX = "/auth"

LOGIN_URL = SECURITY_URL_PREFIX + "/login"
LOGOUT_URL = SECURITY_URL_PREFIX + "/logout"
REGISTER_URL = SECURITY_URL_PREFIX + "/register"
RESET_URL = SECURITY_URL_PREFIX + "/reset"
CHANGE_URL = SECURITY_URL_PREFIX + "/change"
CONFIRM_URL = SECURITY_URL_PREFIX + "/confirm"

# Flask-Mail
MAIL_SERVER = "localhost"
MAIL_PORT = 587
MAIL_DEFAULT_SENDER = '"Meltano" <bot@metlano.com>'

THREADS_PER_PAGE = 2
SECRET_KEY = "damnitjanice"
