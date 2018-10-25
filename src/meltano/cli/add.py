import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli
from meltano.support.project_add_service import (
    ProjectAddService,
    PluginNotSupportedException,
)
from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)
from meltano.support.plugin_discovery_service import PluginDiscoveryService
from meltano.support.database_add_service import DatabaseAddService


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
    database_add_service = DatabaseAddService()
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
    add_plugin(PluginDiscoveryService.EXTRACTORS, plugin_name)


@add.command()
@click.argument("plugin_name")
def loader(plugin_name):
    add_plugin(PluginDiscoveryService.LOADERS, plugin_name)


def add_plugin(plugin_type, plugin_name):
    try:
        add_service = ProjectAddService(plugin_type, plugin_name)
        add_service.add()
        click.secho(f"{plugin_name} added to your meltano.yml config", fg="green")
    except ProjectMissingYMLFileException as e:
        click.secho(
            "Are you in the right directory? I don't see a meltano.yml file here.",
            fg="red",
        )
        raise click.Abort()
    except PluginNotSupportedException:
        click.secho(f"The {plugin_type} {plugin_name} is not supported", fg="red")
        raise click.Abort()

    discovery_service = PluginDiscoveryService()
    install_service = PluginInstallService(plugin_type, plugin_name, discovery_service)

    try:
        click.secho("Activating your virtual environment", fg="green")
        run_venv = install_service.create_venv()

        if run_venv["stdout"]:
            click.echo(run_venv["stdout"])
        if run_venv["stderr"]:
            click.secho(run_venv["stderr"], fg="red")
    except PluginInstallServicePluginNotFoundError as e:
        click.secho(f"{plugin_type.title()} {plugin_name} not supported", fg="red")
        raise click.Abort()

    click.secho("Installing DBT...", fg="green")
    run_install_dbt = install_service.install_dbt()
    if run_install_dbt["stdout"]:
        click.echo(run_install_dbt["stdout"])
    if run_install_dbt["stderr"]:
        click.secho(run_install_dbt["stderr"], fg="red")

    click.secho(f"Installing {plugin_name} via pip...", fg="green")
    run_install_plugin = install_service.install_plugin()
    if run_install_plugin["stdout"]:
        click.echo(run_install_plugin["stdout"])
    if run_install_plugin["stderr"]:
        click.secho(run_install_plugin["stderr"], fg="red")

    click.secho(f"Added and installed {plugin_type} {plugin_name}", fg="green")
