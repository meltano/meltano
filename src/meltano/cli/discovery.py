import os
import json
import click
from urllib.parse import urlparse

from . import cli
from .params import project
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    DiscoveryInvalidError,
)
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
@click.argument(
    "plugin_type", type=click.Choice([*list(PluginType), "all"]), default="all"
)
@project()
def discover(project, plugin_type):
    discover_service = PluginDiscoveryService(project)
    if plugin_type == "all":
        plugin_type = None
    else:
        plugin_type = PluginType.from_cli_argument(plugin_type)

    discovery_dict = discover_service.discover(plugin_type)

    for plugin_type, plugin_defs in discovery_dict.items():
        click.secho(plugin_type, fg="green")
        for plugin_def in plugin_defs:
            click.echo(plugin_def)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_discover(plugin_type=plugin_type)
