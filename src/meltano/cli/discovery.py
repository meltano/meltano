import os
import json
import click
from urllib.parse import urlparse
from . import cli
from ..support.plugin_discovery_service import PluginDiscoveryService as pds

@cli.command()
@click.argument("plugin_type", type=click.Choice([pds.EXTRACTORS, pds.LOADERS, pds.ALL]))
def discover(plugin_type):
    discover_service = pds()
    discover_service.discover(plugin_type)
