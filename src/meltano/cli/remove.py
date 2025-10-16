"""Defines `meltano remove` command."""

from __future__ import annotations

import logging
import typing as t

import click
import structlog

from meltano.cli.params import PluginTypeArg, pass_project
from meltano.cli.utils import InstrumentedCmd, infer_plugin_type
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_location_remove import DbRemoveManager
from meltano.core.plugin_remove_service import PluginRemoveService

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from meltano.core.plugin import PluginType
    from meltano.core.plugin_location_remove import PluginLocationRemoveManager
    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


@click.command(cls=InstrumentedCmd, short_help="Remove plugins from your project.")
@click.argument("plugin", nargs=-1, required=True)
@click.option("--plugin-type", type=PluginTypeArg())
@pass_project()
def remove(
    project: Project,
    plugin: tuple[str, ...],
    plugin_type: PluginType | None,
) -> None:
    """Remove plugins from your project.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#remove
    """  # noqa: D301
    plugin_names = plugin

    plugins = [
        ProjectPlugin(
            infer_plugin_type(plugin_name) if plugin_type is None else plugin_type,
            plugin_name,
        )
        for plugin_name in plugin_names
    ]
    remove_plugins(project, plugins)


def remove_plugins(project: Project, plugins: Sequence[ProjectPlugin]) -> None:
    """Invoke PluginRemoveService and output CLI removal overview."""
    remove_service = PluginRemoveService(project)

    num_removed, total = remove_service.remove_plugins(
        plugins,
        plugin_status_cb=remove_plugin_status_update,
        removal_manager_status_cb=removal_manager_status_update,
    )

    if len(plugins) > 1:
        level = logging.WARNING if num_removed < total else logging.INFO
        logger.log(level, "Fully removed %d/%d plugins", num_removed, total)


def remove_plugin_status_update(plugin: ProjectPlugin) -> None:
    """Print remove status message for a plugin."""
    plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"
    logger.info("Removing %s...", plugin_descriptor)


def removal_manager_status_update(removal_manager: PluginLocationRemoveManager) -> None:
    """Print remove status message for a plugin location."""
    plugin_descriptor = removal_manager.plugin_descriptor
    location = removal_manager.location
    if removal_manager.plugin_error:
        message = removal_manager.message
        logger.error(
            "Error removing plugin %s from %s: %s",
            plugin_descriptor,
            location,
            message,
        )

    elif removal_manager.plugin_not_found:
        logger.warning("Could not find %s in %s to remove", plugin_descriptor, location)

    elif removal_manager.plugin_removed:
        msg = (
            f"Reset {plugin_descriptor} plugin settings in the {location}"
            if isinstance(removal_manager, DbRemoveManager)
            else f"Removed {plugin_descriptor} from {location}"
        )
        logger.info(msg)
