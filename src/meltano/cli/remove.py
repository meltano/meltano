"""Defines `meltano remove` command."""
import click
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_remove_service import PluginRemoveService, RemoveStatus

from . import cli
from .params import pass_project


@cli.command()
@click.argument("plugin_type", type=click.Choice(PluginType.cli_arguments()))
@click.argument("plugin_names", nargs=-1, required=True)
@pass_project()
@click.pass_context
def remove(ctx, project, plugin_type, plugin_names):
    """Remove a plugin from your project."""
    plugins = [
        ProjectPlugin(PluginType.from_cli_argument(plugin_type), plugin_name)
        for plugin_name in plugin_names
    ]

    remove_service = PluginRemoveService(project)
    num_removed, total = remove_service.remove_plugins(
        plugins, status_cb=remove_status_update
    )

    click.echo()

    fg = "green"
    if num_removed < total:
        fg = "yellow"

    if len(plugins) > 1:
        click.secho(f"Removed {num_removed}/{total} plugins", fg=fg)
        click.echo()


def remove_status_update(plugin, remove_status):
    """Print remove status message."""
    plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"

    if remove_status is RemoveStatus.RUNNING:
        click.echo()
        click.secho(f"Removing {plugin_descriptor}...")

    elif remove_status.status is RemoveStatus.ERROR:
        click.secho(
            f"Error removing plugin {plugin_descriptor} from {remove_status.location}: {remove_status.message}",
            fg="red",
        )

    elif remove_status.status is RemoveStatus.NOT_FOUND:
        click.secho(
            f"Could not find {plugin_descriptor} in {remove_status.location} to remove",
            fg="yellow",
        )

    elif remove_status.status is RemoveStatus.REMOVED:
        click.secho(
            f"Removed {plugin_descriptor} from {remove_status.location}", fg="green"
        )
