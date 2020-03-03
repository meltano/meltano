import os
import logging
import warnings
import meltano
import importlib


# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

workers = int(os.getenv("WORKERS", 4))
timeout = 600


def on_reload(arbiter):
    importlib.reload(meltano)
    logging.info(f"Meltano version reloaded to {meltano.__version__}")
