#!/usr/bin/env python3

"""Script to freeze the Meltano database - executed by the Makefile."""

from __future__ import annotations

from alembic.script import ScriptDirectory

from meltano.migrations import LOCK_PATH, MIGRATION_DIR

scripts = ScriptDirectory(str(MIGRATION_DIR))

with LOCK_PATH.open("w") as lock:
    HEAD = scripts.get_current_head()
    lock.write(HEAD)

print(f"Meltano database frozen at {HEAD}.")
