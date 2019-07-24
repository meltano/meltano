from pathlib import Path


MIGRATION_DIR = Path(__path__[0])
LOCK_PATH = MIGRATION_DIR.joinpath("db.lock")
