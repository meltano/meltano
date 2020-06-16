import os
import click
import shutil
import logging
from functools import singledispatch
from typing import List, Dict
from pathlib import Path

from meltano.core.utils import truthy
from meltano.core.plugin import PluginType
from meltano.core.plugin.meltano_file import MeltanoFilePlugin
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from .project import Project
from .venv_service import VenvService


class ProjectInitServiceError(Exception):
    pass


class ProjectInitService:
    def __init__(self, project_name):
        self.project_name = project_name.lower()

    def init(self, activate=True, engine_uri=None, add_discovery=False) -> Project:
        try:
            os.mkdir(self.project_name)
        except Exception as e:
            raise ProjectInitServiceError
        click.secho(f"Created", fg="blue", nl=False)
        click.echo(f" {self.project_name}")

        self.project = Project(self.project_name)
        self.create_files(add_discovery=add_discovery)

        if activate:
            Project.activate(self.project)

        if engine_uri:
            engine_uri = engine_uri.replace(
                "$MELTANO_PROJECT_ROOT", str(self.project.root)
            )
            self.create_system_database(engine_uri)

        return self.project

    def create_files(self, add_discovery=False):
        click.secho(f"Creating project files...", fg="blue")

        plugin = MeltanoFilePlugin("meltano", discovery=add_discovery)
        for path in plugin.create_files(self.project):
            click.secho(f"Created", fg="blue", nl=False)
            click.echo(f" {self.project_name}/{path}")

    def create_system_database(self, engine_uri):
        click.secho(f"Creating system database...", fg="blue")
        # register the system database connection
        engine, _ = project_engine(self.project, engine_uri, default=True)

        migration_service = MigrationService(engine)
        migration_service.upgrade()
        migration_service.seed(self.project)

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

        click.secho("Meltano sends anonymous usage data that help improve the product.")

        click.secho("> ", fg="bright_black", nl=False)

        click.echo("You can opt-out for new, existing, or all projects.")

        click.secho("> ", fg="bright_black", nl=False)

        click.secho(
            "https://meltano.com/docs/environment-variables.html#anonymous-usage-data",
            fg="cyan",
        )

    def join_with_project_base(self, filename):
        return os.path.join(".", self.project_name, filename)
