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
@project
@click.argument(
    "plugin_type",
    type=click.Choice(
        [
            PluginType.EXTRACTORS,
            PluginType.LOADERS,
            PluginType.TRANSFORMERS,
            PluginType.MODELS,
            PluginType.TRANSFORMS,
            PluginType.ORCHESTRATORS,
            PluginType.ALL,
        ]
    ),
)
def discover(project, plugin_type):
    discover_service = PluginDiscoveryService(project)
    try:
        discovery_dict = discover_service.discover(plugin_type)

        for plugin_type, plugins in discovery_dict.items():
            click.secho(plugin_type, fg="green")
            for plugin in plugins:
                click.echo(plugin)

        tracker = GoogleAnalyticsTracker(project)
        tracker.track_meltano_discover(plugin_type=plugin_type)
    except Exception as e:
        click.secho("Cannot list available plugins.", fg="red")
        raise click.ClickException(str(e))
