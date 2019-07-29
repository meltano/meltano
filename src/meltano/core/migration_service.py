import os
import click
from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic import command

from meltano.migrations import MIGRATION_DIR, LOCK_PATH


class MigrationUneededException(Exception):
    """Occurs when no migrations are needed."""

    pass


class MigrationService:
    def __init__(self, engine):
        self.engine = engine

    def ensure_migration_needed(self, script, context, target_revision):
        current_head = context.get_current_revision()

        for rev in script.iterate_revisions(current_head, "base"):
            if rev.revision == target_revision:
                raise MigrationUneededException

    def upgrade(self):
        conn = self.engine.connect()
        cfg = Config()

        # this connection is used in `env.py` for the migrations
        cfg.attributes["connection"] = conn
        cfg.set_main_option("script_location", str(MIGRATION_DIR))
        script = ScriptDirectory.from_config(cfg)
        # let's make sure we actually need to migrate
        context = MigrationContext.configure(conn)

        try:
            # try to find the locked version
            HEAD = LOCK_PATH.open().read().strip()
            self.ensure_migration_needed(script, context, HEAD)

            click.secho(f"Upgrading database to {HEAD}")
            command.upgrade(cfg, HEAD)
        except FileNotFoundError:
            raise click.ClickException(
                "Cannot upgrade the system database, revision lock not found."
            )
        except MigrationUneededException:
            click.secho(f"System database up-to-date.")
        except Exception:
            click.secho(
                f"Cannot upgrade the system database. It might be corrupted or was created before database migrations where introduced (v0.34.0)",
                fg="yellow",
            )
        finally:
            conn.close()
