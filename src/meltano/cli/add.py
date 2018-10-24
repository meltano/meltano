import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli
from meltano.core.project_add_service import (
    ProjectAddService,
    ProjectMissingYMLFileException,
    PluginNotSupportedException,
)
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)
from meltano.core.plugin_discovery_service import PluginDiscoveryService


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice([ProjectAddService.EXTRACTOR, ProjectAddService.LOADER]),
)
@click.argument("plugin_name")
def add(plugin_type, plugin_name):
    plugin_type = (
        PluginDiscoveryService.EXTRACTORS
        if plugin_type == ProjectAddService.EXTRACTOR
        else PluginDiscoveryService.LOADERS
    )
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
