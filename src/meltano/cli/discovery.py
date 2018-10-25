import os
import json
import click
from urllib.parse import urlparse

from . import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginDiscoveryInvalidError,
)


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice([PluginType.EXTRACTORS, PluginType.LOADERS, PluginType.ALL]),
)
def discover(plugin_type):
    discover_service = PluginDiscoveryService()
    try:
        discovery_dict = discover_service.discover(plugin_type)
        for key, value in discovery_dict.items():
            click.secho(key, fg="green")
            click.echo(value)
    except PluginDiscoveryInvalidError:
        click.secho(PluginDiscoveryInvalidError.invalid_message, fg="red")
        raise click.Abort()
