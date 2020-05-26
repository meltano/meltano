import os
import logging
import warnings
import meltano
import importlib


workers = int(os.getenv("WORKERS", 4))
timeout = 600


def on_reload(arbiter):
    importlib.reload(meltano)
    logging.info(f"Meltano version reloaded to {meltano.__version__}")
