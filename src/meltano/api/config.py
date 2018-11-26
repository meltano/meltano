import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)


# the values of those depend on your setup
MELTANO_POSTGRES_URL = get_env_variable("MELTANO_POSTGRES_URL")
MELTANO_POSTGRES_USER = get_env_variable("MELTANO_POSTGRES_USER")
MELTANO_POSTGRES_PASSWORD = get_env_variable("MELTANO_POSTGRES_PASSWORD")
MELTANO_POSTGRES_DB = get_env_variable("MELTANO_POSTGRES_DB")
LOG_PATH = get_env_variable("MELTANO_ANALYZE_LOG_PATH")
ENV = "development"

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{MELTANO_POSTGRES_USER}:{MELTANO_POSTGRES_PASSWORD}@{MELTANO_POSTGRES_URL}/{MELTANO_POSTGRES_DB}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_ECHO=True

THREADS_PER_PAGE = 2

SECRET_KEY = "damnitjanice"
