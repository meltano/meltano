"""Defines `meltano remove` command."""
import click
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_remove_service import (
    PluginLocationRemoveStatus,
    PluginRemoveService,
)

from . import cli
from .params import pass_project


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_names", nargs=-1, required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_names):
    """Remove a plugin from your project."""
    plugins = [
        ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
        for plugin_name in plugin_names
    ]

    remove_plugins(project, plugins)


def remove_plugins(project, plugins):
    """Invoke PluginRemoveService and output CLI removal overview."""
    remove_service = PluginRemoveService(project)

    num_removed, total = remove_service.remove_plugins(
        plugins,
        plugin_status_cb=remove_plugin_status_update,
        location_status_cb=remove_location_status_update,
    )

    click.echo()
    fg = "green"
    if num_removed < total:
        fg = "yellow"

    if len(plugins) > 1:
        click.secho(f"Fully removed {num_removed}/{total} plugins", fg=fg)
        click.echo()


def remove_plugin_status_update(plugin):
    """Print remove status message for a plugin."""
    plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"

    click.echo()
    click.secho(f"Removing {plugin_descriptor}...")
    click.echo()


def remove_location_status_update(plugin, location_remove_state):
    """Print remove status message for a plugin location."""
    plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"

    if location_remove_state.status is PluginLocationRemoveStatus.ERROR:
        click.secho(
            f"Error removing plugin {plugin_descriptor} from {location_remove_state.location}: {location_remove_state.message}",
            fg="red",
        )

    elif location_remove_state.status is PluginLocationRemoveStatus.NOT_FOUND:
        click.secho(
            f"Could not find {plugin_descriptor} in {location_remove_state.location} to remove",
            fg="yellow",
        )

    elif location_remove_state.status is PluginLocationRemoveStatus.REMOVED:
        click.secho(
            f"Removed {plugin_descriptor} from {location_remove_state.location}",
            fg="green",
        )
