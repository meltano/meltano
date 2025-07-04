"""Defines `meltano remove` command."""

from __future__ import annotations

import typing as t
import warnings

import click

from meltano.cli.params import pass_project
from meltano.cli.utils import InstrumentedCmd, PluginTypeArg, infer_plugin_type
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_location_remove import (
    DbRemoveManager,
    PluginLocationRemoveManager,
)
from meltano.core.plugin_remove_service import PluginRemoveService

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from meltano.core.project import Project


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
    if plugin_type is None and plugin[0] in PluginType.cli_arguments():
        plugin_type = PluginType.from_cli_argument(plugin[0])
        plugin_names = plugin[1:]
        warnings.warn(
            "Passing the plugin type as the first positional argument is deprecated "
            "and will be removed in Meltano v4. "
            "Please use the --plugin-type option instead.",
            DeprecationWarning,
            stacklevel=1,
        )
    else:
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

    click.echo()
    if len(plugins) > 1:
        fg = "yellow" if num_removed < total else "green"
        click.secho(f"Fully removed {num_removed}/{total} plugins", fg=fg)
        click.echo()


def remove_plugin_status_update(plugin: ProjectPlugin) -> None:
    """Print remove status message for a plugin."""
    plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"

    click.echo()
    click.secho(f"Removing {plugin_descriptor}...")
    click.echo()


def removal_manager_status_update(removal_manager: PluginLocationRemoveManager) -> None:
    """Print remove status message for a plugin location."""
    plugin_descriptor = removal_manager.plugin_descriptor
    location = removal_manager.location
    if removal_manager.plugin_error:
        message = removal_manager.message

        click.secho(
            f"Error removing plugin {plugin_descriptor} from {location}: {message}",
            fg="red",
        )

    elif removal_manager.plugin_not_found:
        click.secho(
            f"Could not find {plugin_descriptor} in {location} to remove",
            fg="yellow",
        )

    elif removal_manager.plugin_removed:
        msg = f"Removed {plugin_descriptor} from {location}"

        if isinstance(removal_manager, DbRemoveManager):
            msg = f"Reset {plugin_descriptor} plugin settings in the {location}"

        click.secho(msg, fg="green")
