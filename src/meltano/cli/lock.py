"""Lock command."""

from __future__ import annotations

import typing as t

import click
import structlog

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import CliError, PartialInstrumentedCmd
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLockService,
)
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

    lock_service = PluginLockService(project)

    try:
        with project.plugins.use_preferred_source(DefinitionSource.ANY):
            # Make it a list so source preference is not lazily evaluated.
            plugins = list(project.plugins.plugins())
    except Exception:
        tracker.track_command_event(CliEvent.aborted)
        raise

    if plugin_name:
        plugins = [plugin for plugin in plugins if plugin.name in plugin_name]

    if plugin_type is not None:
        plugins = [plugin for plugin in plugins if plugin.type == plugin_type]

    tracked_plugins: list[tuple[ProjectPlugin, str | None]] = []

    if not plugins:
        tracker.track_command_event(CliEvent.aborted)
        errmsg = "No matching plugin(s) found"
        raise CliError(errmsg)

    click.echo(f"Locking {len(plugins)} plugin(s)...")
    for plugin in plugins:
        descriptor = f"{plugin.type.descriptor} {plugin.name}"
        if plugin.is_custom():
            click.secho(f"{descriptor.capitalize()} is a custom plugin", fg="yellow")
        elif plugin.inherit_from is not None:
            click.secho(
                f"{descriptor.capitalize()} is an inherited plugin",
                fg="yellow",
            )
        else:
            # The lock service will fetch from Hub internally
            try:
                lock_service.save(plugin, exists_ok=update, fetch_from_hub=True)
            except LockfileAlreadyExistsError as err:
                relative_path = err.path.relative_to(project.root)
                click.secho(
                    f"Lockfile exists for {descriptor} at {relative_path}",
                    fg="red",
                )
                continue

            tracked_plugins.append((plugin, None))
            click.secho(f"Locked definition for {descriptor}", fg="green")

    tracker.add_contexts(PluginsTrackingContext(tracked_plugins))
    tracker.track_command_event(CliEvent.completed)
