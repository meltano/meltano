"""Migration and system db management."""

from __future__ import annotations

import logging
import typing as t

import click
import structlog
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from meltano.migrations import LOCK_PATH, MIGRATION_DIR

if t.TYPE_CHECKING:
    from sqlalchemy.engine import Engine

logger = structlog.stdlib.get_logger(__name__)
SPLAT = "*"


class MigrationError(Exception):
    """Generic class for migration errors."""


class MigrationUneededException(Exception):
    """No migrations are needed."""


class MigrationService:
    """Migration service."""

    def __init__(self, engine: Engine) -> None:
        """Initialize the migration service.

        Args:
            engine: The sqlalchemy engine to use for the migration and checks.
        """
        self.engine = engine

    def ensure_migration_needed(
        self,
        script: ScriptDirectory,
        context: MigrationContext,
        target_revision: str,
    ) -> None:
        """Ensure that a migration of the system database is actually needed.

        Args:
            script: The alembic script directory.
            context: The migration context.
            target_revision: The desired target revision.

        Raises:
            MigrationUneededException: If no migration is needed.
        """
        current_head = context.get_current_revision()

        for rev in script.iterate_revisions(current_head, "base"):
            if rev.revision == target_revision:
                raise MigrationUneededException

    def upgrade(  # too many expression and too complex
        self,
        *,
        silent: bool = False,
    ) -> None:
        """Upgrade to the latest revision.

        Args:
            silent: If true, don't print anything.

        Raises:
            MigrationError: If the upgrade fails.
        """
        with self.engine.begin() as conn:
            cfg = Config()

            # this connection is used in `env.py` for the migrations
            cfg.attributes["connection"] = conn
            cfg.set_main_option("script_location", str(MIGRATION_DIR))
            script = ScriptDirectory.from_config(cfg)
            # let's make sure we actually need to migrate

            migration_logger = logging.getLogger("alembic.runtime.migration")  # noqa: TID251
            original_log_level = migration_logger.getEffectiveLevel()
            if silent:
                migration_logger.setLevel(logging.ERROR)

            context = MigrationContext.configure(conn)

            try:
                # try to find the locked version
                head = LOCK_PATH.read_text().strip()
                self.ensure_migration_needed(script, context, head)

                if not silent:
                    click.secho(f"Upgrading database to {head}")
                command.upgrade(cfg, head)

                if silent:
                    migration_logger.setLevel(original_log_level)
            except FileNotFoundError as ex:
                raise MigrationError(
                    "Cannot upgrade the system database, revision lock not found.",  # noqa: EM101
                ) from ex
            except MigrationUneededException:
                if not silent:
                    click.secho("System database up-to-date.")
            except Exception as ex:
                logger.exception(str(ex))
                raise MigrationError(
                    "Cannot upgrade the system database. It might be corrupted or "  # noqa: EM101
                    "was created before database migrations where introduced (v0.34.0)",
                ) from ex
