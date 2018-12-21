import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("MELTANO_LOG_PATH", "meltano.log")
ENV = "development"

API_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMP_FOLDER = os.path.join(API_ROOT_DIR, "static/tmp")
PROJECT_ROOT_DIR = os.path.dirname(API_ROOT_DIR)

# SQLALCHEMY_ECHO=True

THREADS_PER_PAGE = 2

SECRET_KEY = "damnitjanice"
