#!/usr/bin/env python3
from pathlib import Path
from alembic.script import ScriptDirectory


MIGRATION_DIR = Path("src/meltano/migrations")
LOCK_PATH = MIGRATION_DIR.joinpath("db.lock")

scripts = ScriptDirectory(str(MIGRATION_DIR))

with LOCK_PATH.open("w") as lock:
    HEAD = scripts.get_current_head()
    lock.write(HEAD)

print(f"Meltano database frozen at {HEAD}.")
