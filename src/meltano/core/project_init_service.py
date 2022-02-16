"""New Project Initialization Service."""
import os

import click

from .db import project_engine
from .migration_service import MigrationError, MigrationService
from .plugin.meltano_file import MeltanoFilePlugin
from .project import Project
from .project_settings_service import ProjectSettingsService, SettingValueStore


class ProjectInitServiceError(Exception):
    """Project Initialization Service Exception."""


class ProjectInitService:
    """New Project Initialization Service."""

    def __init__(self, project_name):
        """Create a new ProjectInitService instance.

        Args:
            project_name: The name of the project to create
        """
        self.project_name = project_name.lower()

    def init(self, activate: bool = True, add_discovery: bool = False) -> Project:
        """Initialise Meltano Project.

        Args:
            activate: Activate newly created project
            add_discovery: Add discovery.yml file to created project

        Returns:
            A new Project instance

        Raises:
            ProjectInitServiceError: Directory already exists
        """
        try:
            os.mkdir(self.project_name)
        except Exception as exp:  # noqa: F841
            raise ProjectInitServiceError(
                f"Directory {self.project_name} already exists."
            )
        click.secho("Created", fg="blue", nl=False)
        click.echo(f" {self.project_name}")

        self.project = Project(self.project_name)
        self.settings_service = ProjectSettingsService(self.project)

        self.create_files(add_discovery=add_discovery)
        self.set_send_anonymous_usage_stats()

        if activate:
            Project.activate(self.project)

        self.create_system_database()

        return self.project

    def create_files(self, add_discovery=False):
        """Create project files.

        Args:
            add_discovery: Add discovery.yml file to created project
        """
        click.secho("Creating project files...", fg="blue")

        plugin = MeltanoFilePlugin(discovery=add_discovery)
        for path in plugin.create_files(self.project):
            click.secho("Created", fg="blue", nl=False)
            click.echo(f" {self.project_name}/{path}")

    def set_send_anonymous_usage_stats(self):
        """Set Anonymous Usage Stats flag."""
        # Ensure the value is explicitly stored in `meltano.yml`
        self.settings_service.set(
            "send_anonymous_usage_stats",
            self.settings_service.get("send_anonymous_usage_stats"),
            store=SettingValueStore.MELTANO_YML,
        )

    def create_system_database(self):
        """Create Meltano System DB.

        Raises:
            ProjectInitServiceError: Database initialization failed
        """
        click.secho("Creating system database...", fg="blue")

        # register the system database connection
        engine, _ = project_engine(self.project, default=True)

        try:
            migration_service = MigrationService(engine)
            migration_service.upgrade()
            migration_service.seed(self.project)
        except MigrationError as err:
            raise ProjectInitServiceError(str(err)) from err

    def echo_instructions(self):
        """Echo Next Steps to Click CLI."""
        click.secho("\nProject ", nl=False)
        click.secho(self.project_name, fg="magenta", nl=False)
        click.echo(" has been created.\n")

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
        click.secho("\tcd ", nl=False)
        click.secho(self.project_name, fg="magenta")
        click.echo("\tVisit ", nl=False)
        click.secho("https://meltano.com/", fg="cyan", nl=False)
        click.echo(" to learn where to go from here")

        click.echo()
        click.secho("> ", fg="bright_black", nl=False)
        click.secho(
            "Meltano sends anonymous usage data that helps improve the product."
        )
        click.secho("> ", fg="bright_black", nl=False)
        click.echo("You can opt-out for new, existing, or all projects.")
        click.secho("> ", fg="bright_black", nl=False)
        click.secho(
            "https://docs.meltano.com/reference/settings#send-anonymous-usage-stats",
            fg="cyan",
        )
        click.echo()

    def join_with_project_base(self, filename):
        """Join Path to Project base.

        Args:
            filename: File name to join with project base

        Returns:
            Joined base path and passed filename
        """
        return os.path.join(".", self.project_name, filename)
