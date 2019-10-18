import warnings
import meltano
import importlib

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

workers = 4
timeout = 600


def on_reload(arbiter):
    importlib.reload(meltano)
    print(f"Meltano version reloaded to {meltano.__version__}")
