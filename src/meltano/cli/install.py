"""CLI command `meltano install`."""
from __future__ import annotations

import click

from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.tracking import CliEvent, PluginsTrackingContext

from . import cli
from .params import pass_project
from .utils import CliError, InstrumentedCmd, install_plugins


@cli.command(cls=InstrumentedCmd, short_help="Install project dependencies.")
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
@click.pass_context
@pass_project(migrate=True)
def install(
    project: Project,
    ctx: click.Context,
    plugin_type: str,
    plugin_name: str,
    clean: bool,
    parallelism: int,
):
    """
    Install all the dependencies of your project based on the meltano.yml file.

    \b\nRead more at https://www.meltano.com/docs/command-line-interface.html#install
    """
    tracker = ctx.obj["tracker"]
    legacy_tracker = ctx.obj["legacy_tracker"]

    plugins_service = ProjectPluginsService(project)

    try:
        if plugin_type:
            plugin_type = PluginType.from_cli_argument(plugin_type)
            plugins = plugins_service.get_plugins_of_type(plugin_type)
            if plugin_name:
                plugins = [plugin for plugin in plugins if plugin.name in plugin_name]
        else:
            plugins = list(plugins_service.plugins())
    except Exception:
        tracker.track_command_event(CliEvent.aborted)
        raise

    click.echo(f"Installing {len(plugins)} plugins...")
    tracker.add_contexts(
        PluginsTrackingContext([(candidate, None) for candidate in plugins])
    )
    tracker.track_command_event(CliEvent.inflight)

    success = install_plugins(project, plugins, parallelism=parallelism, clean=clean)

    legacy_tracker.track_meltano_install()

    if not success:
        tracker.track_command_event(CliEvent.failed)
        raise CliError("Failed to install plugin(s)")
    tracker.track_command_event(CliEvent.completed)
