"""Lock command."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click
import structlog

from meltano.core.plugin import PluginType
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLockService,
)
from meltano.core.project_plugins_service import DefinitionSource, ProjectPluginsService
from meltano.core.tracking import CliContext, CliEvent, PluginsTrackingContext, Tracker

from . import cli
from .params import pass_project

if TYPE_CHECKING:
    from meltano.core.project import Project


__all__ = ["lock"]
logger = structlog.get_logger(__name__)


@cli.command(short_help="Lock plugin definitions.")
@click.argument(
    "plugin-type",
    type=click.Choice(PluginType.cli_arguments()),
    required=False,
)
@click.argument("plugin_name", nargs=-1, required=False)
@click.option("--update", "-u", is_flag=True, help="Update the lock file.")
@pass_project()
def lock(
    project: Project,
    plugin_type: str | None,
    plugin_name: tuple[str, ...],
    update: bool,
):
    """Lock plugin definitions.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#lock
    """
    tracker = Tracker(project)
    tracker.add_contexts(
        CliContext.from_command_and_kwargs(
            "lock",
            None,
            update=update,
            plugin_type=plugin_type,
            plugin_name=plugin_name,
        )
    )
    tracker.track_command_event(CliEvent.started)

    lock_service = PluginLockService(project)
    plugins_service = ProjectPluginsService(project)

    with plugins_service.use_preferred_source(DefinitionSource.HUB):
        try:
            if plugin_type:
                plugin_type = PluginType.from_cli_argument(plugin_type)
                plugins = plugins_service.get_plugins_of_type(plugin_type)
                if plugin_name:
                    plugins = [
                        plugin for plugin in plugins if plugin.name in plugin_name
                    ]
            else:
                # Make it a list so source preference is not lazily evaluated.
                plugins = list(plugins_service.plugins())
        except Exception:
            tracker.track_command_event(CliEvent.aborted)
            raise

    tracked_plugins = []

    for plugin in plugins:
        descriptor = f"{plugin.type.descriptor} {plugin.name}"
        tracked_plugins.append((plugin, None))
        if plugin.is_custom():
            click.secho(f"{descriptor.capitalize()} is a custom plugin", fg="yellow")
        else:
            try:
                lock_service.save(plugin, exists_ok=update)
            except LockfileAlreadyExistsError as err:
                relative_path = err.path.relative_to(project.root)
                click.secho(
                    f"Lockfile exists for {descriptor} at {relative_path}",
                    fg="red",
                )
                continue

            click.secho(f"Locked definition for {descriptor}", fg="green")

    tracker.add_contexts(PluginsTrackingContext(tracked_plugins))
    tracker.track_command_event(CliEvent.completed)
