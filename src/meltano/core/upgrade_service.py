"""Meltano upgrade service."""

from __future__ import annotations

import asyncio
import os
import pathlib
import subprocess
import sys
import typing as t

import click

from meltano.core._packaging import editable_installation
from meltano.core.error import MeltanoError
from meltano.core.plugin_install_service import PluginInstallReason, install_plugins
from meltano.core.project_plugins_service import PluginType
from meltano.core.state_service import StateService

if t.TYPE_CHECKING:
    from meltano.core.project import Project


def _check_editable_installation(*, force: bool) -> None:
    if not force and (editable_location := editable_installation()):
        raise AutomaticPackageUpgradeError(
            reason="it is installed from source",
            instructions=f"navigate to `{editable_location}` and run `git pull`",
        )


def _check_docker_installation() -> None:
    if pathlib.Path("/.dockerenv").exists():
        raise AutomaticPackageUpgradeError(
            reason="it is installed inside Docker",
            instructions=(
                "pull the latest Docker image using "
                "`docker pull meltano/meltano` and recreate any containers "
                "you may have created"
            ),
        )


def _check_in_nox_session() -> None:
    if os.getenv("NOX_CURRENT_SESSION"):  # pragma: no branch
        raise AutomaticPackageUpgradeError(
            reason="it is installed inside a Nox session",
            instructions="",
        )


class UpgradeError(Exception):
    """The Meltano upgrade fails."""


class AutomaticPackageUpgradeError(Exception):
    """An automatic upgrade of Meltano fails."""

    def __init__(self, reason: str, instructions: str):
        """Initialize the `AutomaticPackageUpgradeError`.

        Args:
            reason: The reason the exception occurred.
            instructions: Instructions for how to manually resolve the exception.
        """
        self.reason = reason
        self.instructions = instructions


class UpgradeService:
    """Meltano upgrade service."""

    def _upgrade_package(self, pip_url: str | None, *, force: bool) -> bool:
        _check_editable_installation(force=force)
        _check_docker_installation()
        _check_in_nox_session()

        pip_url = pip_url or "meltano"
        run = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", pip_url],
            stderr=subprocess.PIPE,
            text=True,
        )

        if run.returncode != 0:
            raise UpgradeError("Failed to upgrade `meltano`.", run)  # noqa: EM101, TRY003

        return True

    def upgrade_package(
        self,
        pip_url: str | None = None,
        *,
        force: bool = False,
    ) -> bool:
        """Upgrade the Meltano package.

        Args:
            pip_url: The pip URL to use when upgrading the Meltano package.
            force: Whether editable installations from source should be overwritten.

        Returns:
            Whether the upgrade was successful.
        """
        click.secho("Upgrading `meltano` package...", fg="blue")

        try:
            self._upgrade_package(pip_url=pip_url, force=force)
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

    def update_files(self, *, project: Project) -> None:
        """Update the files managed by Meltano inside the current project.

        Args:
            project: The Meltano project.

        Raises:
            MeltanoError: Failed to upgrade plugins.
        """
        click.secho("Updating files managed by plugins...", fg="blue")

        file_plugins = project.plugins.get_plugins_of_type(PluginType.FILES)
        if not file_plugins:
            click.echo("Nothing to update")
            return

        success = asyncio.run(
            install_plugins(
                project,
                file_plugins,
                reason=PluginInstallReason.UPGRADE,
            ),
        )
        if not success:
            raise MeltanoError("Failed to upgrade plugin(s)")  # noqa: EM101, TRY003

    def migrate_database(self, *, project: Project) -> None:
        """Migrate the Meltano database.

        Args:
            project: The Meltano project.

        Raises:
            UpgradeError: The migration failed.
        """
        click.secho("Applying migrations to system database...", fg="blue")

        from meltano.core.db import project_engine
        from meltano.core.migration_service import MigrationError, MigrationService

        engine, _ = project_engine(project)

        try:
            migration_service = MigrationService(engine)
            migration_service.upgrade()
        except MigrationError as err:
            raise UpgradeError(str(err)) from err

    def migrate_state(self, *, project: Project) -> None:
        """Move cloud state files to deduplicated prefix paths.

        Args:
            project: The Meltano project.

        See: https://github.com/meltano/meltano/issues/7938
        """
        from meltano.core.state_store.filesystem import CloudStateStoreManager

        state_service = StateService(project=project)
        manager = state_service.state_store_manager
        if isinstance(manager, CloudStateStoreManager):
            click.secho("Applying migrations to project state...", fg="blue")
            for filepath in manager.list_all_files(with_prefix=False):
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

    def upgrade(
        self,
        *,
        project: Project,
        skip_package: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """Upgrade Meltano.

        Note: this is not actually called as part of the `meltano upgrade` command
        but is useful for testing and debugging upgrade logic.

        Args:
            project: The Meltano project.
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

        self.update_files(project=project)
        click.echo()
        self.migrate_database(project=project)
        click.echo()
        self.migrate_state(project=project)
        click.echo()
        click.secho(
            "Meltano and your Meltano project have been upgraded!"
            if package_upgraded
            else "Your Meltano project has been upgraded!",
            fg="green",
        )
