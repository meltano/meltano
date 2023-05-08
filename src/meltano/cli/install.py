"""CLI command `meltano install`."""

from __future__ import annotations

import typing as t

import click
import structlog

from meltano.cli.params import pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd, install_plugins
from meltano.core.block.parser import BlockParser
from meltano.core.plugin import PluginType
from meltano.core.schedule_service import ScheduleService
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

logger = structlog.getLogger(__name__)


@click.command(cls=PartialInstrumentedCmd, short_help="Install project dependencies.")
@click.argument(
    "plugin_type",
    type=click.Choice(PluginType.cli_arguments()),
    required=False,
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
    help=(
        "Limit the number of plugins to install in parallel. "
        "Defaults to the number of cores."
    ),
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Ignore the required Python version declared by the plugins.",
)
@click.option(
    "--schedule",
    "-s",
    "schedule_name",
    help="Install all plugins from the given schedule.",
)
@click.pass_context
@pass_project(migrate=True)
def install(  # noqa: C901
    project: Project,
    ctx: click.Context,
    plugin_type: str,
    plugin_name: str,
    clean: bool,
    parallelism: int,
    force: bool,
    schedule_name: str,
):
    """
    Install all the dependencies of your project based on the meltano.yml file.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#install
    """
    tracker: Tracker = ctx.obj["tracker"]
    try:
        if plugin_type:
            plugin_type = PluginType.from_cli_argument(plugin_type)
            plugins = project.plugins.get_plugins_of_type(plugin_type)
            if plugin_name:
                plugins = [plugin for plugin in plugins if plugin.name in plugin_name]
        else:
            plugins = list(project.plugins.plugins())

        if schedule_name:
            schedule_plugins = _get_schedule_plugins(
                ctx.obj["project"],
                schedule_name,
            )
            plugins = list(set(plugins) & set(schedule_plugins))
    except Exception:
        tracker.track_command_event(CliEvent.aborted)
        raise

    click.echo(f"Installing {len(plugins)} plugins...")
    tracker.add_contexts(
        PluginsTrackingContext([(candidate, None) for candidate in plugins]),
    )
    tracker.track_command_event(CliEvent.inflight)

    success = install_plugins(
        project,
        plugins,
        parallelism=parallelism,
        clean=clean,
        force=force,
    )
    if not success:
        tracker.track_command_event(CliEvent.failed)
        raise CliError("Failed to install plugin(s)")
    tracker.track_command_event(CliEvent.completed)


def _get_schedule_plugins(project: Project, schedule_name: str):
    schedule_service = ScheduleService(project)
    schedule_obj = schedule_service.find_schedule(schedule_name)
    schedule_plugins = set()
    if schedule_obj.elt_schedule:
        for plugin_name in (schedule_obj.extractor, schedule_obj.loader):
            schedule_plugins.add(project.plugins.find_plugin(plugin_name))
    else:
        task_sets = schedule_service.task_sets_service.get(schedule_obj.job)
        for blocks in task_sets.flat_args_per_set:
            parser = BlockParser(logger, project, blocks)
            for plugin in parser.plugins:
                schedule_plugins.add(
                    project.plugins.find_plugin(plugin.info.get("name"))
                    if plugin.type == PluginType.MAPPERS
                    else plugin,
                )
    return schedule_plugins
