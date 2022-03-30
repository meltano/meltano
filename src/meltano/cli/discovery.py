"""Discoverable Plugins CLI."""

import click

from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.tracking import GoogleAnalyticsTracker

from . import cli
from .params import pass_project


@cli.command(short_help="List the available discoverable plugins and their variants.")
@click.argument(
    "plugin_type", type=click.Choice([*list(PluginType), "all"]), default="all"
)
@pass_project()
def discover(project, plugin_type):
    """
    List the available discoverable plugins and their variants.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#discover
    """
    discover_service = PluginDiscoveryService(project)
    if plugin_type == "all":
        plugin_types = list(PluginType)
    else:
        plugin_types = [PluginType.from_cli_argument(plugin_type)]

    for idx, discovered_plugin_type in enumerate(plugin_types):
        if idx > 0:
            click.echo()

        click.secho(f"{str(discovered_plugin_type).capitalize()}", fg="green")

        for plugin_def in discover_service.get_plugins_of_type(discovered_plugin_type):
            click.echo(plugin_def.name, nl=False)

            if len(plugin_def.variants) > 1:
                click.echo(f", variants: {plugin_def.variant_labels}")
            else:
                click.echo()

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_discover(plugin_type=plugin_type)
