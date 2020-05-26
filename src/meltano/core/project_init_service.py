import os
import yaml
import click
import shutil
import logging
from functools import singledispatch
from typing import List, Dict
from pathlib import Path

from meltano.core.utils import truthy
import meltano.core.bundle as bundle
from meltano.core.plugin import PluginType
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.config_service import ConfigService, PluginMissingError
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from .project import Project
from .venv_service import VenvService


class ProjectInitServiceError(Exception):
    pass


@singledispatch
def visit(node, executor):
    pass


@visit.register(dict)
def _(node: Dict, target_path: Path = None):
    created = []

    logging.debug(f"{target_path}")
    for name, definition in node.items():
        directory = target_path.joinpath(os.path.dirname(name))

        # always create the base directory
        os.makedirs(directory, exist_ok=True)

        # recurse for the nested definition
        created += visit(definition, target_path.joinpath(name))

    return created


@visit.register(str)
def _(node: str, target_path: Path):
    """
    Create the file using either the raw content or a bundled file.
    """
    logging.debug(f"{target_path}")
    if node.startswith("bundle://"):
        # copy from the bundle
        _, path = node.split("bundle://")
        path = bundle.find(path)

        logging.debug(f"{path} → {target_path}")
        if path.is_dir():
            shutil.copytree(path, target_path)
        else:
            shutil.copy(path, target_path)
    else:
        # write the content
        with target_path.open("w") as target:
            target.write(node)

    return [target_path]


class ProjectInitService:
    def __init__(self, project_name):
        self.initialize_file = bundle.find("initialize.yml")
        self.project_name = project_name.lower()

    def init(self, activate=True, engine_uri=None) -> Project:
        try:
            os.mkdir(self.project_name)
        except Exception as e:
            raise ProjectInitServiceError
        click.secho(f"Created", fg="blue", nl=False)
        click.echo(f" {self.project_name}")

        self.project = Project(self.project_name)
        self.create_files()

        if activate:
            Project.activate(self.project)

        if engine_uri:
            engine_uri = engine_uri.replace(
                "$MELTANO_PROJECT_ROOT", str(self.project.root)
            )
            self.create_system_database(engine_uri)

        return self.project

    def create_files(self):
        click.secho(f"Creating project files...", fg="blue")
        default_project_yaml = yaml.safe_load(open(self.initialize_file))
        for path in visit(default_project_yaml, Path(self.project_name)):
            click.secho(f"Created", fg="blue", nl=False)
            click.echo(f" {path}")

    def create_system_database(self, engine_uri):
        click.secho(f"Creating system database...", fg="blue")
        # register the system database connection
        engine, _ = project_engine(self.project, engine_uri, default=True)

        migration_service = MigrationService(engine)
        migration_service.upgrade()
        migration_service.seed(self.project)

    def install_plugin(self, plugin_type, plugin_name):
        try:
            self.config_service.find_plugin(plugin_name)
        except PluginMissingError:
            plugin = self.add_service.add(plugin_type, plugin_name)
            self.install_service.install_plugin(plugin)

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
