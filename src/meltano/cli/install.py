import click

from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.plugin import PluginType
from meltano.core.project_plugins_service import ProjectPluginsService

from . import cli
from .params import pass_project
from .utils import CliError, install_plugins


@cli.command(short_help="Install project dependencies.")
@click.argument(
    "plugin_type", type=click.Choice(PluginType.cli_arguments()), required=False
)
@click.argument("plugin_name", nargs=-1, required=False)
@click.option(
    "--clean",
    is_flag=True,
    help="Completely reinstall a plugin rather than simply upgrading if necessary.",
)
@click.option(
    "--parallelism",
    "-p",
    type=click.INT,
    default=None,
    help="Limit the number of plugins to install in parallel. Defaults to the number of cores.",
)
@pass_project(migrate=True)
def install(project, plugin_type, plugin_name, clean, parallelism):
    """
    Install all the dependencies of your project based on the meltano.yml file.

    \b\nRead more at https://www.meltano.com/docs/command-line-interface.html#install
    """
    plugins_service = ProjectPluginsService(project)

    if plugin_type:
        plugin_type = PluginType.from_cli_argument(plugin_type)
        plugins = plugins_service.get_plugins_of_type(plugin_type)
        if plugin_name:
            plugins = [p for p in plugins if p.name in plugin_name]
    else:
        plugins = list(plugins_service.plugins())

    click.echo(f"Installing {len(plugins)} plugins...")

    success = install_plugins(project, plugins, parallelism=parallelism, clean=clean)

    tracker = LegacyTracker(project)
    tracker.track_meltano_install()

    if not success:
        raise CliError("Failed to install plugin(s)")
