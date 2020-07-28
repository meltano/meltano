import os
import click
import shutil
import logging
from functools import singledispatch
from typing import List, Dict
from pathlib import Path

from .utils import truthy
from .project_settings_service import ProjectSettingsService, SettingValueStore
from .project import Project
from .plugin.meltano_file import MeltanoFilePlugin
from .db import project_engine
from .migration_service import MigrationService, MigrationError


class ProjectInitServiceError(Exception):
    pass


class ProjectInitService:
    def __init__(self, project_name):
        self.project_name = project_name.lower()

    def init(self, activate=True, add_discovery=False) -> Project:
        try:
            os.mkdir(self.project_name)
        except Exception as e:
            raise ProjectInitServiceError(
                f"Directory {self.project_name} already exists!"
            )
        click.secho(f"Created", fg="blue", nl=False)
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
        click.secho(f"Creating project files...", fg="blue")

        plugin = MeltanoFilePlugin("meltano", discovery=add_discovery)
        for path in plugin.create_files(self.project):
            click.secho(f"Created", fg="blue", nl=False)
            click.echo(f" {self.project_name}/{path}")

    def set_send_anonymous_usage_stats(self):
        # Ensure the value is explicitly stored in `meltano.yml`
        self.settings_service.set(
            "send_anonymous_usage_stats",
            self.settings_service.get("send_anonymous_usage_stats"),
            store=SettingValueStore.MELTANO_YML,
        )

    def create_system_database(self):
        click.secho(f"Creating system database...", fg="blue")

        # register the system database connection
        database_uri = self.settings_service.get("database_uri")
        engine, _ = project_engine(self.project, database_uri, default=True)

        try:
            migration_service = MigrationService(engine)
            migration_service.upgrade()
            migration_service.seed(self.project)
        except MigrationError as err:
            raise ProjectInitServiceError(str(err)) from err

    def echo_instructions(self):
        click.echo()
        click.secho("Project", nl=False)
        click.secho(f" {self.project_name}", fg="green", nl=False)
        click.echo(" has been created.")

        click.echo("\nNext steps:")
        click.secho("\tcd ", nl=False)
        click.secho(self.project_name, fg="green")
        click.echo("\tVisit https://meltano.com/ to learn where to go from here")

        click.echo()
        click.secho("> ", fg="bright_black", nl=False)

        click.secho(
            "Meltano sends anonymous usage data that helps improve the product."
        )

        click.secho("> ", fg="bright_black", nl=False)

        click.echo("You can opt-out for new, existing, or all projects.")

        click.secho("> ", fg="bright_black", nl=False)

        click.secho(
            "https://meltano.com/docs/settings.html#send-anonymous-usage-stats",
            fg="cyan",
        )

    def join_with_project_base(self, filename):
        return os.path.join(".", self.project_name, filename)
