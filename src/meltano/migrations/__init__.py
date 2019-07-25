from pathlib import Path

# the `scripts/alembic_freeze.py` refers to these paths
# we need to make sure they match
MIGRATION_DIR = Path(__path__[0])
LOCK_PATH = MIGRATION_DIR.joinpath("db.lock")
