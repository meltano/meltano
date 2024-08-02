"""New Project Initialization Service."""

from __future__ import annotations

import contextlib
import typing as t
import uuid
from pathlib import Path

import click

from meltano.core.cli_messages import GREETING
from meltano.core.db import project_engine
from meltano.core.plugin.meltano_file import MeltanoFilePlugin
from meltano.core.project import Project
from meltano.core.project_settings_service import SettingValueStore

if t.TYPE_CHECKING:
    import os

PROJECT_FILENAME = "meltano.yml"


class ProjectInitServiceError(Exception):
    """Project Initialization Service Exception."""


class ProjectInitService:
    """New Project Initialization Service."""

    def __init__(self, project_directory: os.PathLike):
        """Create a new ProjectInitService instance.

        Args:
            project_directory: The directory path to create the project at
        """
        self.project_directory = Path(project_directory)

        with contextlib.suppress(ValueError):
            self.project_directory = self.project_directory.relative_to(Path.cwd())

    def init(
        self,
        *,
        activate: bool = True,
        force: bool = False,
    ) -> Project:
        """Initialise Meltano Project.

        Args:
            activate: Activate newly created project
            force: Whether to overwrite `meltano.yml` in the existing directory.

        Returns:
            A new Project instance

        Raises:
            ProjectInitServiceError: Directory already exists
        """
        try:
            self.project_directory.mkdir()
        except FileExistsError as ex:
            if self.project_directory.joinpath(PROJECT_FILENAME).exists() and not force:
                msg = (
                    "A `meltano.yml` file already exists in the target directory. "
                    "Use `--force` to overwrite it."
                )
                raise ProjectInitServiceError(msg) from ex
        except PermissionError as ex:
            raise ProjectInitServiceError(
                f"Permission denied to create '{self.project_directory}'.",  # noqa: EM102
            ) from ex
        except Exception as ex:
            raise ProjectInitServiceError(
                f"Could not create directory '{self.project_directory}'. {ex}",  # noqa: EM102
            ) from ex

        project = Project(self.project_directory)

        self.create_dot_meltano_dir(project)
        self.create_files(project)

        project.settings.set(
            "project_id",
            str(uuid.uuid4()),
            store=SettingValueStore.MELTANO_YML,
        )
        self.set_send_anonymous_usage_stats(project)
        if activate:
            Project.activate(project)

        self.create_system_database(project)

        return project

    def create_dot_meltano_dir(self, project: Project) -> None:
        """Create .meltano directory.

        Args:
            project: Meltano project context
        """
        # explicitly create the .meltano directory if it doesn't exist
        click.secho("Creating .meltano folder", fg="blue")
        project.meltano_dir().mkdir(parents=True, exist_ok=True)
        click.secho("created", fg="blue", nl=False)
        click.echo(f" .meltano in {project.sys_dir_root}")

    def create_files(self, project: Project) -> None:
        """Create project files.

        Args:
            project: Meltano project context
        """
        click.secho("Creating project files...", fg="blue")

        if project.root != Path.cwd():
            click.echo(f"  {self.project_directory}/")

        plugin = MeltanoFilePlugin()

        expected_files = plugin.files_to_create(project, [])
        created_files = plugin.create_files(project)
        for path in expected_files:
            if path in created_files:
                click.secho("   |--", fg="blue", nl=False)
                click.echo(f" {path}")
            else:
                click.secho("   |--", fg="yellow", nl=False)
                click.echo(f" {path} (skipped)")

    def set_send_anonymous_usage_stats(self, project: Project) -> None:
        """Set Anonymous Usage Stats flag.

        Args:
            project: The Meltano project the setting is being set on.
        """
        # If set to false store explicitly in `meltano.yml`
        if not project.settings.get("send_anonymous_usage_stats"):
            project.settings.set(
                "send_anonymous_usage_stats",
                project.settings.get("send_anonymous_usage_stats"),
                store=SettingValueStore.MELTANO_YML,
            )

    def create_system_database(self, project: Project) -> None:
        """Create Meltano System DB.

        Args:
            project: Meltano project context

        Raises:
            ProjectInitServiceError: Database initialization failed
        """
        click.secho("Creating system database...", fg="blue", nl=False)

        # register the system database connection
        engine, _ = project_engine(project, default=True)

        from meltano.core.migration_service import MigrationError, MigrationService

        try:
            migration_service = MigrationService(engine)
            migration_service.upgrade(silent=True)
            click.secho("  Done!", fg="blue")
        except MigrationError as err:
            raise ProjectInitServiceError(str(err)) from err

    def echo_instructions(self, project: Project) -> None:
        """Echo Next Steps to Click CLI.

        Args:
            project: Meltano project context
        """
        click.secho(GREETING, nl=False)
        click.echo("Your project has been created!\n")

        click.echo("Meltano Environments initialized with ", nl=False)
        click.secho("dev", fg="bright_green", nl=False)
        click.echo(", ", nl=False)
        click.secho("staging", fg="bright_yellow", nl=False)
        click.echo(", and ", nl=False)
        click.secho("prod", fg="bright_red", nl=False)
        click.echo(".")
        click.echo("To learn more about Environments visit: ", nl=False)
        click.secho(
            "https://docs.meltano.com/concepts/environments",
            fg="cyan",
        )

        click.echo("\nNext steps:")

        if project.root != Path.cwd():
            click.secho("  cd ", nl=False)
            click.secho(self.project_directory, fg="magenta")

        click.echo("  Visit ", nl=False)
        click.secho(
            "https://docs.meltano.com/getting-started/part1",
            fg="cyan",
            nl=False,
        )
        click.echo(" to learn where to go from here")
