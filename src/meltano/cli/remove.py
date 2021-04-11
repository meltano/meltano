import click
from meltano.core.plugin import PluginType
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

    plugin = ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
    plugins_service.remove_from_file(plugin)
    plugin_remove_service = PluginRemoveService(project)
    plugin_remove_service.remove_plugin(plugin)
