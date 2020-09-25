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
        plugin_types = list(PluginType)
    else:
        plugin_types = [PluginType.from_cli_argument(plugin_type)]

    for i, plugin_type in enumerate(plugin_types):
        if i > 0:
            click.echo()

        click.secho(f"{str(plugin_type).capitalize()}", fg="green")

        for plugin_def in discover_service.get_plugins_of_type(plugin_type):
            click.echo(plugin_def.name, nl=False)

            if len(plugin_def.variants) > 1:
                click.echo(f", variants: {plugin_def.list_variant_names()}")
            else:
                click.echo()

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_discover(plugin_type=plugin_type)
