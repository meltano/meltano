"""Discoverable Plugins CLI."""

from __future__ import annotations

import click

from meltano.core.hub import MeltanoHubService
from meltano.core.plugin import PluginType
from meltano.core.project import Project

from . import cli
from .params import pass_project
from .utils import InstrumentedCmd


@cli.command(
    cls=InstrumentedCmd,
    short_help="List the available plugins in Meltano Hub and their variants.",
)
@click.argument(
    "plugin_type", type=click.Choice([*list(PluginType), "all"]), default="all"
)
@pass_project()
@click.pass_context
def discover(ctx: click.Context, project: Project, plugin_type: str):
    """
    List the available discoverable plugins and their variants.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#discover
    """
    hub_service = MeltanoHubService(project)
    if plugin_type == "all":
        plugin_types = [
            plugin_type for plugin_type in list(PluginType) if plugin_type.discoverable
        ]
    else:
        plugin_types = [PluginType.from_cli_argument(plugin_type)]

    for idx, discovered_plugin_type in enumerate(plugin_types):
        if idx > 0:
            click.echo()

        click.secho(f"{str(discovered_plugin_type).capitalize()}", fg="green")

        try:
            plugin_type_index = hub_service.get_plugins_of_type(discovered_plugin_type)
        except Exception:
            click.secho(
                f"Can not retrieve {discovered_plugin_type} from the Hub",
                fg="yellow",
                err=True,
            )
            continue

        for plugin_name, plugin in plugin_type_index.items():
            click.echo(plugin_name, nl=False)

            if len(plugin.variants) > 1:
                click.echo(f", variants: {', '.join(plugin.variant_labels)}")
            else:
                click.echo()
