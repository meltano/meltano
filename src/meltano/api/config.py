import os
from dotenv import load_dotenv

load_dotenv()

# the values of those depend on your setup
MELTANO_POSTGRES_URL = os.getenv("MELTANO_POSTGRES_URL", "localhost")
MELTANO_POSTGRES_USER = os.getenv("MELTANO_POSTGRES_USER", "meltano")
MELTANO_POSTGRES_PASSWORD = os.getenv("MELTANO_POSTGRES_PASSWORD", "meltano")
MELTANO_POSTGRES_DB = os.getenv("MELTANO_POSTGRES_DB", "meltano")
LOG_PATH = os.getenv("MELTANO_LOG_PATH", "meltano.log")
ENV = "development"

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{MELTANO_POSTGRES_USER}:{MELTANO_POSTGRES_PASSWORD}@{MELTANO_POSTGRES_URL}/{MELTANO_POSTGRES_DB}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_ECHO=True

THREADS_PER_PAGE = 2

SECRET_KEY = "damnitjanice"
