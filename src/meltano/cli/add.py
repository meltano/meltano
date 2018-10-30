import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli
from meltano.core.project_add_service import (
    ProjectAddService,
    PluginNotSupportedException,
)
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin import PluginType
from meltano.core.database_add_service import DatabaseAddService
from meltano.core.project import Project


@cli.group()
def add():
    pass


@add.command()
@click.option("--name", prompt="Database connection name")
@click.option("--host", prompt="Database host")
@click.option("--database", prompt="Database database")
@click.option("--schema", prompt="Database schema")
@click.option("--username", prompt="Database username")
@click.option(
    "--password", prompt="Database password", hide_input=True, confirmation_prompt=True
)
def database(name, host, database, schema, username, password):
    project = Project.find()
    database_add_service = DatabaseAddService(project)
    database_add_service.add(
        name=name,
        host=host,
        database=database,
        schema=schema,
        username=username,
        password=password,
    )
    click.secho("database yml file updated", fg="green")


@add.command()
@click.argument("plugin_name")
def extractor(plugin_name):
    project = Project.find()
    add_plugin(project, PluginType.EXTRACTORS, plugin_name)


@add.command()
@click.argument("plugin_name")
def loader(plugin_name):
    project = Project.find()
    add_plugin(project, PluginType.LOADERS, plugin_name)


def add_plugin(project: Project, plugin_type: PluginType, plugin_name: str):
    try:
        add_service = ProjectAddService(project)
        plugin = add_service.add(plugin_type, plugin_name)
        click.secho(f"{plugin_name} added to your meltano.yml config", fg="green")

        install_service = PluginInstallService(project)
        click.secho("Activating your virtual environment", fg="green")
        run_venv = install_service.create_venv(plugin)

        if run_venv["stdout"]:
            click.echo(run_venv["stdout"])
        if run_venv["stderr"]:
            click.secho(run_venv["stderr"], fg="red")

        click.secho(f"Installing {plugin_name} via pip...", fg="green")
        run_install_plugin = install_service.install_plugin(plugin)
        if run_install_plugin["stdout"]:
            click.echo(run_install_plugin["stdout"])
        if run_install_plugin["stderr"]:
            click.secho(run_install_plugin["stderr"], fg="red")

        click.secho(f"Added and installed {plugin_type} {plugin_name}", fg="green")
    except PluginNotSupportedException:
        click.secho(f"The {plugin_type} {plugin_name} is not supported", fg="red")
        raise click.Abort()
    except PluginNotFoundError as e:
        click.secho(f"{plugin_type.title()} {plugin_name} not supported", fg="red")
        raise click.Abort()
