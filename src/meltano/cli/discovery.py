import os
import json
import click
from urllib.parse import urlparse
from . import cli
from meltano.support.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginDiscoveryInvalidJSONError,
)


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice(
        [
            PluginDiscoveryService.EXTRACTORS,
            PluginDiscoveryService.LOADERS,
            PluginDiscoveryService.ALL,
        ]
    ),
)
def discover(plugin_type):
    discover_service = PluginDiscoveryService()
    try:
        discover_service.discover(plugin_type)
    except PluginDiscoveryInvalidJSONError:
        click.Abort()
