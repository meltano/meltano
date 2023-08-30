"""Meltano upgrade service."""

from __future__ import annotations

import os
import subprocess
import sys

import click
from sqlalchemy.engine import Engine

import meltano
from meltano.cli.utils import PluginInstallReason, install_plugins
from meltano.core.error import MeltanoError
from meltano.core.project import Project
from meltano.core.project_plugins_service import PluginType
from meltano.core.state_service import StateService
from meltano.core.state_store.filesystem import CloudStateStoreManager


class UpgradeError(Exception):
    """The Meltano upgrade fails."""


class AutomaticPackageUpgradeError(Exception):
    """An automatic upgrade of Meltano fails."""

    def __init__(self, reason: str, instructions: str):
        """Initialize the `AutomaticPackageUpgradeError`.

        Args:
            reason: The reason the exception occured.
            instructions: Instructions for how to manually resolve the exception.
        """
        self.reason = reason
        self.instructions = instructions


class UpgradeService:  # noqa: WPS214
    """Meltano upgrade service."""

    def __init__(self, engine: Engine, project: Project):
        """Initialize the Meltano upgrade service.

        Args:
            engine: The SQLAlchemy engine to be used for the upgrade.
            project: The Meltano project.
        """
        self.project = project
        self.engine = engine

    def _upgrade_package(self, pip_url: str | None, force: bool) -> bool:
        fail_reason = None
        instructions = ""

        meltano_file_path = "/src/meltano/__init__.py"
        editable = meltano.__file__.endswith(meltano_file_path)
        if editable and not force:
            meltano_dir = meltano.__file__[: -len(meltano_file_path)]
            fail_reason = "it is installed from source"
            instructions = f"navigate to `{meltano_dir}` and run `git pull`"

        elif os.path.exists("/.dockerenv"):
            fail_reason = "it is installed inside Docker"
            instructions = (
                "pull the latest Docker image using "
                "`docker pull meltano/meltano` and recreate any containers "
                "you may have created"
            )

        elif os.getenv("NOX_CURRENT_SESSION") == "tests":
            fail_reason = "it is installed inside a Nox test session"
            instructions = ""

        if fail_reason:
            raise AutomaticPackageUpgradeError(
                reason=fail_reason,
                instructions=instructions,
            )

        pip_url = pip_url or "meltano"
        run = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", pip_url],
            stderr=subprocess.PIPE,
            text=True,
        )

        if run.returncode != 0:
            raise UpgradeError("Failed to upgrade `meltano`.", run)

        return True

    def upgrade_package(self, pip_url: str | None = None, force: bool = False) -> bool:
        """Upgrade the Meltano package.

        Args:
            pip_url: The pip URL to use when upgrading the Meltano package.
            force: Whether editable installations from source should be overwritten.

        Returns:
            Whether the upgrade was successful.
        """
        click.secho("Upgrading `meltano` package...", fg="blue")

        try:
            self._upgrade_package(pip_url, force)
        except AutomaticPackageUpgradeError as err:
            msg = click.style(
                "The `meltano` package could not be upgraded automatically",
                fg="red",
            )
            click.echo(f"{msg} because {err.reason}.")
            if err.instructions:
                click.echo(f"To upgrade manually, {err.instructions}.")
            return False

        click.echo("The `meltano` package has been upgraded.")
        click.echo()
        return True

    def update_files(self):
        """Update the files managed by Meltano inside the current project.

        Raises:
            MeltanoError: Failed to upgrade plugins.
        """
        click.secho("Updating files managed by plugins...", fg="blue")

        file_plugins = self.project.plugins.get_plugins_of_type(PluginType.FILES)
        if not file_plugins:
            click.echo("Nothing to update")
            return

        success = install_plugins(
            self.project,
            file_plugins,
            reason=PluginInstallReason.UPGRADE,
        )
        if not success:
            raise MeltanoError("Failed to upgrade plugin(s)")

    def migrate_database(self):
        """Migrate the Meltano database.

        Raises:
            UpgradeError: The migration failed.
        """
        click.secho("Applying migrations to system database...", fg="blue")

        from meltano.core.migration_service import MigrationError, MigrationService

        try:
            migration_service = MigrationService(self.engine)
            migration_service.upgrade()
        except MigrationError as err:
            raise UpgradeError(str(err)) from err

    def migrate_state(self):
        """Move cloud state files to deduplicated prefix paths.

        See: https://github.com/meltano/meltano/issues/7938
        """
        state_service = StateService(project=self.project)
        manager = state_service.state_store_manager
        if isinstance(manager, CloudStateStoreManager):
            click.secho("Applying migrations to project state...", fg="blue")
            for filepath in state_service.state_store_manager.list_all_files():
                parts = filepath.split(manager.delimiter)
                if (
                    parts[-1] == "state.json"
                    and filepath.count(manager.prefix.strip(manager.delimiter)) > 1
                ):
                    duplicated_substr = manager.delimiter.join(
                        [
                            manager.prefix.strip(manager.delimiter),
                            manager.prefix.strip(manager.delimiter),
                        ],
                    )
                    new_path = filepath.replace(duplicated_substr, manager.prefix)
                    new_path = new_path.replace(
                        manager.delimiter * 2,
                        manager.delimiter,
                    )
                    manager.copy_file(filepath, new_path)
                    click.secho(f"Copied state from {filepath} to {new_path}")

    def upgrade(self, skip_package: bool = False, **kwargs):  # noqa: WPS213
        """Upgrade Meltano.

        Note: this is not actually called as part of the `meltano upgrade` command
        but is useful for testing and debugging upgrade logic.

        Args:
            skip_package: Whether the Meltano package should be upgraded.
            kwargs: Keyword arguments for `UpgradeService.upgrade_package`.
        """
        package_upgraded = False
        if not skip_package:
            package_upgraded = self.upgrade_package(**kwargs)

            if not package_upgraded:
                click.echo(
                    "Then, run `meltano upgrade --skip-package` to upgrade "
                    "your project based on the latest version.",
                )
                return

            click.echo()

        self.update_files()
        click.echo()
        self.migrate_database()
        click.echo()
        self.migrate_state()
        click.echo()
        click.secho(
            "Meltano and your Meltano project have been upgraded!"
            if package_upgraded
            else "Your Meltano project has been upgraded!",
            fg="green",
        )
