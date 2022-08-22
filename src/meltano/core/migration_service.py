"""Migration and system db management."""
from __future__ import annotations

import logging
from contextlib import closing

import click
import sqlalchemy
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from meltano.api.models.security import Role, RolePermissions
from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.migrations import LOCK_PATH, MIGRATION_DIR

SPLAT = "*"


class MigrationError(Exception):
    """Generic class for migration errors."""


class MigrationUneededException(Exception):
    """Occurs when no migrations are needed."""


class MigrationService:
    """Migration service."""

    def __init__(self, engine: Engine) -> None:
        """Initialize the migration service.

        Args:
            engine: The sqlalchemy engine to use for the migration and checks.
        """
        self.engine = engine

    def ensure_migration_needed(
        self, script: ScriptDirectory, context: MigrationContext, target_revision: str
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

    def upgrade(  # noqa: WPS213, WPS231 too many expression and too complex
        self, silent: bool = False
    ) -> None:
        """Upgrade to the latest revision.

        Args:
            silent: If true, don't print anything.

        Raises:
            MigrationError: If the upgrade fails.
        """
        conn = self.engine.connect()
        cfg = Config()

        # this connection is used in `env.py` for the migrations
        cfg.attributes["connection"] = conn
        cfg.set_main_option("script_location", str(MIGRATION_DIR))
        script = ScriptDirectory.from_config(cfg)
        # let's make sure we actually need to migrate

        migration_logger = logging.getLogger("alembic.runtime.migration")
        original_log_level = migration_logger.getEffectiveLevel()
        if silent:
            migration_logger.setLevel(logging.ERROR)

        context = MigrationContext.configure(conn)

        try:  # noqa: WPS229
            # try to find the locked version
            head = LOCK_PATH.open().read().strip()
            self.ensure_migration_needed(script, context, head)

            if not silent:
                click.secho(f"Upgrading database to {head}")
            command.upgrade(cfg, head)

            if silent:
                migration_logger.setLevel(original_log_level)
        except FileNotFoundError:
            raise MigrationError(
                "Cannot upgrade the system database, revision lock not found."
            )
        except MigrationUneededException:
            if not silent:
                click.secho("System database up-to-date.")
        except Exception as err:
            logging.exception(str(err))
            raise MigrationError(
                "Cannot upgrade the system database. It might be corrupted or was created before database migrations where introduced (v0.34.0)"
            )
        finally:
            conn.close()

    def seed(self, project: Project) -> None:
        """Seed the database with the default roles and permissions.

        Args:
            project: The project to seed the database for.
        """
        _, session_maker = project_engine(project)
        with closing(session_maker()) as session:
            self._create_user_role(session)
            session.commit()

    def _create_user_role(self, session: Session) -> None:
        """Actually perform the database seeding creating users/roles.

        Args:
            session: The session to use.
        """
        if not session.query(Role).filter_by(name="admin").first():

            session.add(
                Role(
                    name="admin",
                    description="Meltano Admin",
                    permissions=[
                        RolePermissions(type="view:design", context=SPLAT),
                        RolePermissions(type="view:reports", context=SPLAT),
                        RolePermissions(type="modify:acl", context=SPLAT),
                    ],
                )
            )

        if not session.query(Role).filter_by(name="regular").first():
            session.merge(Role(name="regular", description="Meltano User"))

        # add the universal permissions to Admin
        admin = session.query(Role).filter_by(name="admin").one()
        try:
            session.query(RolePermissions).filter_by(
                role=admin, type=SPLAT, context=SPLAT
            ).one()
        except sqlalchemy.orm.exc.NoResultFound:
            admin.permissions.append(RolePermissions(type=SPLAT, context=SPLAT))
