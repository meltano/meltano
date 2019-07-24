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
        self.alembic_cfg = self.build_alembic_config()

    def build_alembic_config(self):
        cfg = Config(attributes={"configure_logger": False})
        cfg.set_main_option("script_location", str(MIGRATION_DIR))
        cfg.set_main_option("sqlalchemy.url", str(self.engine.url))

        return cfg

    def upgrade(self):
        try:
            HEAD = LOCK_PATH.open().read()
            click.secho(f"Upgrading database to {HEAD}")
            command.upgrade(self.alembic_cfg, HEAD)
        except FileNotFoundError:
            raise click.ClickException(
                "Cannot upgrade the system database, revision lock not found."
            )
