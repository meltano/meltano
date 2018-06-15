import os

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# the values of those depend on your setup
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PASSWORD = get_env_variable("POSTGRES_PASSWORD")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
ENV = 'development'
DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PASSWORD,url=POSTGRES_URL,db=POSTGRES_DB)

SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 2

SECRET_KEY = "damnitjanice"