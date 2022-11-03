"""New Project Initialization Service."""
from __future__ import annotations

import abc
import os
import uuid
from pathlib import Path
from typing import Iterable

import click

from .cli_messages import GREETING
from .db import project_engine
from .plugin.meltano_file import MeltanoFilePlugin
from .project import Project
from .project_settings_service import ProjectSettingsService, SettingValueStore


class ProjectDirectoryCheck(abc.ABC):
    """Abstract class for a project directory "check"."""

    def __init__(self, project_directory: Path):
        """Create a new `ProjectDirectoryCheck` instance.

        Args:
            project_directory: The target project directory
        """
        self.project_directory = project_directory
        self.project_files = [
            self.project_directory / file
            for file in MeltanoFilePlugin().file_contents(None).keys()
        ]

    @property
    @abc.abstractmethod
    def descriptor(self) -> str:
        """Descriptor of the check used in `message`."""

    @property
    @abc.abstractmethod
    def results(self) -> Iterable:
        """Results of the check.

        Raises:
            NotImplementedError: Not yet implemented
        """
        raise NotImplementedError

    def __str__(self):
        """Summary message of the check.

        Returns:
            Summary message, including results overview
        """
        results_str = ", ".join(map(str, self.results))
        return f"Found {len(self.results)} {self.descriptor}: {results_str}"

    def __bool__(self):
        """Infer truthiness from the results of the check.

        Returns:
            `False` if `results` is empty, else `True`
        """
        return bool(self.results)


class ConflictingFilesCheck(ProjectDirectoryCheck):
    """Check for conflicts between files in the project directory and those that would be created for a new Meltano project."""

    @property
    def results(self):
        """Results of the check.

        Returns:
            Conflicting files, if any
        """
        return [
            file
            for file in self.project_directory.rglob("*")
            if file in self.project_files
        ]

    @property
    def descriptor(self):
        """Descriptor of the check used in `message`.

        Returns:
            Singular or plural descriptor for conflicting files
        """
        return f"conflicting file{'' if len(self.results) == 1 else 's'}"


class ProjectInitServiceError(Exception):
    """Project Initialization Service Exception."""


class ProjectInitService:  # noqa: WPS214
    """New Project Initialization Service."""

    def __init__(self, project_directory: os.PathLike):
        """Create a new ProjectInitService instance.

        Args:
            project_directory: The directory path to create the project at
        """
        self.project_directory = Path(project_directory)

        try:
            self.project_directory = self.project_directory.relative_to(Path.cwd())
        except ValueError:
            pass

    def init(self, activate: bool = True, add_discovery: bool = False) -> Project:
        """Initialise Meltano Project.

        Args:
            activate: Activate newly created project
            add_discovery: Add discovery.yml file to created project

        Returns:
            A new Project instance

        Raises:
            ProjectInitServiceError: Could not create the Meltano project
        """
        self.check_project_directory()

        try:
            self.project_directory.mkdir(exist_ok=True)
        except PermissionError as ex:
            raise ProjectInitServiceError(
                f"Permission denied to create '{self.project_directory}'."
            ) from ex
        except Exception as ex:
            raise ProjectInitServiceError(
                f"Could not create directory '{self.project_directory}'. {ex}"
            ) from ex

        project = Project(self.project_directory)

        self.create_dot_meltano_dir(project)
        self.create_files(project, add_discovery=add_discovery)

        self.settings_service = ProjectSettingsService(project)
        self.settings_service.set(
            "project_id",
            str(uuid.uuid4()),
            store=SettingValueStore.MELTANO_YML,
        )
        self.set_send_anonymous_usage_stats()
        if activate:
            Project.activate(project)

        self.create_system_database(project)

        return project

    def check_project_directory(self):
        """Check if the directory can support a new Meltano project.

        Raises:
            ProjectInitServiceError: Conflicting files present
        """
        check = ConflictingFilesCheck(self.project_directory)

        if not check:
            return

        raise ProjectInitServiceError(
            "\n".join(
                (
                    f"Could not create project '{self.project_directory}'",
                    str(check),
                )
            )
        )

    def create_dot_meltano_dir(self, project: Project):
        """Create .meltano directory.

        Args:
            project: Meltano project context
        """
        # explicitly create the .meltano directory if it doesn't exist
        click.secho("Creating .meltano folder", fg="blue")
        os.makedirs(project.meltano_dir(), exist_ok=True)
        click.secho("created", fg="blue", nl=False)
        click.echo(f" .meltano in {project.sys_dir_root}")

    def create_files(self, project: Project, add_discovery=False):
        """Create project files.

        Args:
            project: Meltano project context
            add_discovery: Add discovery.yml file to created project
        """
        click.secho("Creating project files...", fg="blue")

        if project.root != Path.cwd():
            click.echo(f"  {self.project_directory}/")

        plugin = MeltanoFilePlugin(discovery=add_discovery)
        for path in plugin.create_files(project):
            click.secho("   |--", fg="blue", nl=False)
            click.echo(f" {path}")

    def set_send_anonymous_usage_stats(self):
        """Set Anonymous Usage Stats flag."""
        # If set to false store explicitly in `meltano.yml`
        if not self.settings_service.get("send_anonymous_usage_stats"):
            self.settings_service.set(
                "send_anonymous_usage_stats",
                self.settings_service.get("send_anonymous_usage_stats"),
                store=SettingValueStore.MELTANO_YML,
            )

    def create_system_database(self, project: Project):
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
            migration_service.seed(project)
            click.secho("  Done!", fg="blue")
        except MigrationError as err:
            raise ProjectInitServiceError(str(err)) from err

    def echo_instructions(self, project: Project):
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
