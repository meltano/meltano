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
@click.argument("plugin_names", nargs=-1, required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_names):
    """Remove a plugin from your project."""
    plugins_service = ProjectPluginsService(project)
    plugin_remove_service = PluginRemoveService(project)

    for plugin_name in plugin_names:

        plugin = ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
        plugin_descriptor = f"{plugin.type.singular} '{plugin.name}'"

        try:
            plugins_service.remove_from_file(plugin)
        except PluginNotFoundError:
            click.secho(
                f"Could not find {plugin_descriptor} in meltano.yml - attempting to remove plugin installation",
                fg="yellow",
            )

        plugin_remove_service.remove_plugin(plugin)
