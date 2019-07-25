import os
import click
from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command

from meltano.migrations import MIGRATION_DIR, LOCK_PATH


class MigrationService:
    def __init__(self, engine):
        self.engine = engine

    def upgrade(self):
        conn = self.engine.connect()
        cfg = Config()

        try:
            # try to find the locked version
            HEAD = LOCK_PATH.open().read()

            # this connection is used in `env.py` for the migrations
            cfg.attributes["connection"] = conn
            cfg.set_main_option("script_location", str(MIGRATION_DIR))

            click.secho(f"Upgrading database to {HEAD}")
            command.upgrade(cfg, HEAD)
        except FileNotFoundError:
            raise click.ClickException(
                "Cannot upgrade the system database, revision lock not found."
            )
        finally:
            conn.close()
