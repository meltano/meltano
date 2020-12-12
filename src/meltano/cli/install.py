import click
from meltano.core.plugin import PluginType
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.tracking import GoogleAnalyticsTracker

from . import cli
from .params import pass_project
from .utils import CliError, add_related_plugins, install_plugins


@cli.command()
@click.argument(
    "plugin_type", type=click.Choice(PluginType.cli_arguments()), required=False
)
@click.argument("plugin_name", nargs=-1, required=False)
@click.option("--include-related", is_flag=True)
@pass_project(migrate=True)
def install(project, plugin_type, plugin_name, include_related):
    """
    Installs all the dependencies of your project based on the meltano.yml file.
    Read more at https://www.meltano.com/docs/command-line-interface.html.
    """
    plugins_service = ProjectPluginsService(project)

    if plugin_type:
        plugin_type = PluginType.from_cli_argument(plugin_type)
        plugins = plugins_service.get_plugins_of_type(plugin_type)
        if plugin_name:
            plugins = [p for p in plugins if p.name in plugin_name]
    else:
        plugins = list(plugins_service.plugins())

    if include_related:
        add_service = ProjectAddService(project, plugins_service=plugins_service)
        related_plugins = add_related_plugins(project, plugins, add_service=add_service)
        plugins.extend(related_plugins)

    # We will install the plugins in reverse order, since dependencies
    # are listed after their dependents in `related_plugins`, but should
    # be installed first.
    plugins.reverse()

    click.echo(f"Installing {len(plugins)} plugins...")

    success = install_plugins(project, plugins)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_install()

    if not success:
        raise CliError("Failed to install plugin(s)")
