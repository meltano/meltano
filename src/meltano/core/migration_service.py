import os
import click
import logging
import sqlalchemy
from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic import command

from meltano.migrations import MIGRATION_DIR, LOCK_PATH
from meltano.core.db import project_engine
from meltano.api.models.security import Role, RolePermissions


class MigrationError(Exception):
    pass


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

    def upgrade(self, silent=False):
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

        if silent:
            migration_logger.setLevel(original_log_level)

        try:
            # try to find the locked version
            HEAD = LOCK_PATH.open().read().strip()
            self.ensure_migration_needed(script, context, HEAD)

            if not silent:
                click.secho(f"Upgrading database to {HEAD}")
            command.upgrade(cfg, HEAD)
        except FileNotFoundError:
            raise MigrationError(
                "Cannot upgrade the system database, revision lock not found."
            )
        except MigrationUneededException:
            if not silent:
                click.secho(f"System database up-to-date.")
        except Exception as err:
            logging.exception(str(err))
            click.secho(
                f"Cannot upgrade the system database. It might be corrupted or was created before database migrations where introduced (v0.34.0)",
                fg="yellow",
                err=True,
            )
        finally:
            conn.close()

    def seed(self, project):
        _, Session = project_engine(project)
        session = Session()
        try:
            if not session.query(Role).filter_by(name="admin").first():
                session.add(
                    Role(
                        name="admin",
                        description="Meltano Admin",
                        permissions=[
                            RolePermissions(type="view:design", context="*"),
                            RolePermissions(type="view:reports", context="*"),
                            RolePermissions(type="modify:acl", context="*"),
                        ],
                    )
                )

            if not session.query(Role).filter_by(name="regular").first():
                session.merge(Role(name="regular", description="Meltano User"))

            # add the universal permissions to Admin
            admin = session.query(Role).filter_by(name="admin").one()
            try:
                session.query(RolePermissions).filter_by(
                    role=admin, type="*", context="*"
                ).one()
            except sqlalchemy.orm.exc.NoResultFound:
                admin.permissions.append(RolePermissions(type="*", context="*"))

            session.commit()
        finally:
            session.close()
