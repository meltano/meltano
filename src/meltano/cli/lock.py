"""Lock command."""

from __future__ import annotations

import typing as t

import click
import structlog

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd
from meltano.core.project_plugins_service import DefinitionSource
from meltano.core.tracking.contexts import CliEvent, PluginsTrackingContext

if t.TYPE_CHECKING:
    from meltano.core.plugin import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.tracking import Tracker


__all__ = ["lock"]
logger = structlog.get_logger(__name__)


@click.command(cls=PartialInstrumentedCmd, short_help="Lock plugin definitions.")
@click.option(
    "--plugin-type",
    type=PluginTypeArg(),
    help="Lock only the plugins of the given type.",
)
@click.argument("plugin_name", nargs=-1, required=False)
@click.option("--update", "-u", is_flag=True, help="Update the lock file.")
@click.pass_context
@pass_project()
def lock(
    project: Project,
    ctx: click.Context,
    *,
    plugin_type: PluginType | None,
    plugin_name: tuple[str, ...],
    update: bool,
) -> None:
    """Lock plugin definitions.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#lock
    """  # noqa: D301
    tracker: Tracker = ctx.obj["tracker"]

    plugins = list(project.plugins.plugins(ensure_parent=False))
    if plugin_name:
        plugins = [plugin for plugin in plugins if plugin.name in plugin_name]

    if plugin_type is not None:
        plugins = [plugin for plugin in plugins if plugin.type == plugin_type]

    tracked_plugins: list[tuple[ProjectPlugin, str | None]] = []

    if not plugins:
        tracker.track_command_event(CliEvent.aborted)
        errmsg = "No matching plugin(s) found"
        raise CliError(errmsg)

    preferred_source = DefinitionSource.HUB if update else DefinitionSource.ANY
    for plugin in plugins:
        descriptor = f"{plugin.type.descriptor} {plugin.name}"
        if plugin.is_custom():
            logger.warning("Custom %s does not need to be locked", descriptor)
        elif plugin.inherit_from is not None:
            logger.warning("Inherited %s does not need to be locked", descriptor)
        else:
            plugin.parent = None
            with project.plugins.use_preferred_source(preferred_source):
                plugin = project.plugins.ensure_parent(plugin)
                tracked_plugins.append((plugin, None))

    tracker.add_contexts(PluginsTrackingContext(tracked_plugins))
    tracker.track_command_event(CliEvent.completed)
