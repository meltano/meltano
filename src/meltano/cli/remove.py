"""Defines `meltano remove` command."""
import click
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_remove_service import PluginRemoveService
from meltano.core.project_plugins_service import ProjectPluginsService

from . import cli
from .params import pass_project


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_name", required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_name):
    """Remove a plugin from your project."""
    plugins_service = ProjectPluginsService(project)
    plugin_remove_service = PluginRemoveService(project)

    plugin = ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
    plugin_descriptor = f"{plugin.type.singular} '{plugin.name}'"

    removed_from_meltanofile = False
    removed_installation = False

    try:
        removed_from_meltanofile = bool(plugins_service.remove_from_file(plugin))
    except PluginNotFoundError:
        click.secho(
            f"Could not find {plugin_descriptor} in meltano.yml - attempting to remove plugin installation",
            fg="yellow",
        )

    removed_installation = plugin_remove_service.remove_plugin(plugin)

    if not removed_installation:
        click.secho(
            f"Could not find an existing installation of {plugin_descriptor} to remove",
            fg="yellow",
        )

    if removed_from_meltanofile or removed_installation:
        click.secho(
            f"Removed {plugin_descriptor}",
            fg="green",
        )
