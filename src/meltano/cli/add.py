import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli
from meltano.support.project_add_service import (
    ProjectAddService,
    ProjectMissingYMLFileException,
)
from meltano.support.plugin_install_service import PluginInstallService
from meltano.support.plugin_discovery_service import PluginDiscoveryService


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice(
        [
            ProjectAddService.EXTRACTOR,
            ProjectAddService.LOADER,
            ProjectAddService.WAREHOUSE,
        ]
    ),
)
@click.argument("plugin_name")
def add(plugin_type, plugin_name):
    try:
        add_service = ProjectAddService(plugin_type, plugin_name)
        add_service.add()
    except ProjectMissingYMLFileException as e:
        raise click.Abort()

    install_service = PluginInstallService()
    plugin_type = (
        PluginDiscoveryService.EXTRACTORS
        if plugin_type == ProjectAddService.EXTRACTOR
        else PluginDiscoveryService.LOADERS
    )

    try:
        install_service.install(plugin_type, plugin_name)
    except Exception as e:
        raise click.Abort()

    click.secho(f"Added and installed {plugin_type} {plugin_name}", fg="green")
