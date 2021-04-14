"""Defines `meltano remove` command."""
import click
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_remove_service import PluginRemoveService

from . import cli
from .params import pass_project
from .utils import remove_status_update


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_names", nargs=-1, required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_names):
    """Remove a plugin from your project."""
    plugin_remove_service = PluginRemoveService(project)

    plugins = [
        ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
        for plugin_name in plugin_names
    ]

    plugin_remove_service.remove_plugins(plugins, status_cb=remove_status_update)
