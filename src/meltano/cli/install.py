"""CLI command `meltano install`."""

from __future__ import annotations

import typing as t

import click
import structlog

from meltano.cli.params import pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd
from meltano.core.block.parser import BlockParser
from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import install_plugins
from meltano.core.schedule_service import ScheduleService
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker

ANY = "-"

logger = structlog.getLogger(__name__)


@click.command(cls=PartialInstrumentedCmd, short_help="Install project dependencies.")
@click.argument(
    "plugin_type",
    type=click.Choice((*PluginType.cli_arguments(), ANY)),
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
@run_async
async def install(
    project: Project,
    ctx: click.Context,
    *,
    plugin_type: str,
    plugin_name: str,
    clean: bool,
    parallelism: int,
    force: bool,
    schedule_name: str,
) -> None:
    """Install all the dependencies of your project based on the meltano.yml file.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#install
    """  # noqa: D301
    tracker: Tracker = ctx.obj["tracker"]
    try:
        if plugin_type and plugin_type != ANY:
            plugin_type = PluginType.from_cli_argument(plugin_type)
            plugins = project.plugins.get_plugins_of_type(plugin_type)
        else:
            plugins = [p for p in project.plugins.plugins() if not p.is_mapping()]

        if plugin_name:
            plugins = [plugin for plugin in plugins if plugin.name in plugin_name]

        if schedule_name:
            schedule_plugins = _get_schedule_plugins(
                ctx.obj["project"],
                schedule_name,
            )
            plugins = list(set(plugins) & set(schedule_plugins))
    except Exception:
        tracker.track_command_event(CliEvent.aborted)
        raise

    logger.info("Installing %d plugins", len(plugins))
    tracker.add_contexts(
        PluginsTrackingContext([(candidate, None) for candidate in plugins]),
    )
    tracker.track_command_event(CliEvent.inflight)

    success = await install_plugins(
        project,
        plugins,
        parallelism=parallelism,
        clean=clean,
        force=force,
    )
    if not success:
        tracker.track_command_event(CliEvent.failed)
        raise CliError("Failed to install plugin(s)")  # noqa: EM101
    tracker.track_command_event(CliEvent.completed)


def _get_schedule_plugins(project: Project, schedule_name: str):  # noqa: ANN202
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
