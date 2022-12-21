"""Defines `meltano remove` command."""
from __future__ import annotations

import click

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_location_remove import (
    DbRemoveManager,
    PluginLocationRemoveManager,
)
from meltano.core.plugin_remove_service import PluginRemoveService

from . import cli
from .params import pass_project
from .utils import InstrumentedCmd


@cli.command(cls=InstrumentedCmd, short_help="Remove plugins from your project.")
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_names", nargs=-1, required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_names):
    """
    Remove plugins from your project.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#remove
    """
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
        removal_manager_status_cb=removal_manager_status_update,
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


def removal_manager_status_update(removal_manager: PluginLocationRemoveManager):
    """Print remove status message for a plugin location."""
    plugin_descriptor = removal_manager.plugin_descriptor
    location = removal_manager.location
    message = removal_manager.remove_message

    if removal_manager.plugin_error:
        click.secho(
            f"Error removing plugin {plugin_descriptor} from {location}: {message}",
            fg="red",
        )

    elif removal_manager.plugin_not_found:
        click.secho(
            f"Could not find {plugin_descriptor} in {location} to remove", fg="yellow"
        )

    elif removal_manager.plugin_removed:

        msg = f"Removed {plugin_descriptor} from {location}"

        if isinstance(removal_manager, DbRemoveManager):
            msg = f"Reset {plugin_descriptor} plugin settings in the {location}"

        click.secho(msg, fg="green")
