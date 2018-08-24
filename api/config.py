import os


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)


# the values of those depend on your setup
POSTGRES_URL = get_env_variable("MELTANO_ANALYSIS_POSTGRES_URL")
POSTGRES_USER = get_env_variable("MELTANO_ANALYSIS_POSTGRES_USER")
POSTGRES_PASSWORD = get_env_variable("MELTANO_ANALYSIS_POSTGRES_PASSWORD")
POSTGRES_DB = get_env_variable("MELTANO_ANALYSIS_POSTGRES_DB")
LOG_PATH = get_env_variable('MELTANO_ANALYSIS_LOG_PATH')
ENV = 'development'

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, 'static/tmp')
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

user, pw, url, db = POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_URL, POSTGRES_DB
SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{pw}@{url}/{db}'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_ECHO=True

THREADS_PER_PAGE = 2

SECRET_KEY = "damnitjanice"
