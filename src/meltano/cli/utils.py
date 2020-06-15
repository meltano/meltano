import click
from typing import List

from meltano.core.project_add_service import (
    ProjectAddService,
    PluginNotSupportedException,
    PluginAlreadyAddedException,
)
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
):

    try:
        plugin = add_service.add(plugin_type, plugin_name)
        click.secho(
            f"Added {plugin_type.descriptor} '{plugin_name}' to your Meltano project",
            fg="green",
        )
    except PluginAlreadyAddedException as err:
        click.secho(
            f"{plugin_type.descriptor.capitalize()} '{plugin_name}' is already in your Meltano project",
            fg="yellow",
            err=True,
        )
        plugin = err.plugin
    except (PluginNotSupportedException, PluginNotFoundError) as err:
        click.secho(
            f"Error: {plugin_type.descriptor} '{plugin_name}' is not known to Meltano",
            fg="red",
        )
        raise click.Abort()

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type=plugin_type, plugin_name=plugin_name)

    return plugin


def add_related_plugins(
    project, plugins, add_service: ProjectAddService, plugin_types=list(PluginType)
):
    discovery_service = PluginDiscoveryService(project)

    added_plugins = []
    for plugin_install in plugins:
        try:
            plugin_def = discovery_service.find_plugin(
                plugin_install.type, plugin_install.name
            )
        except PluginNotFoundError:
            continue

        related_plugins = add_service.add_related(plugin_def, plugin_types=plugin_types)
        for related_plugin in related_plugins:
            click.secho(
                f"Added related {related_plugin.type.descriptor} '{related_plugin.name}' to your Meltano project",
                fg="green",
            )

        added_plugins.extend(related_plugins)

    return added_plugins


def install_status_update(data):
    plugin = data["plugin"]

    if data["status"] == "running":
        click.echo()
        click.secho(f"Installing {plugin.type.descriptor} '{plugin.name}'...")
    elif data["status"] == "error":
        click.secho(data["message"], fg="red")
        click.secho(data["details"], err=True)
    elif data["status"] == "warning":
        click.secho(f"Warning! {data['message']}.", fg="yellow")
    elif data["status"] == "success":
        click.secho(f"Installed {plugin.type.descriptor} '{plugin.name}'", fg="green")


def install_plugins(project, plugins, **kwargs):
    install_service = PluginInstallService(project)
    install_status = install_service.install_plugins(
        plugins, status_cb=install_status_update, **kwargs
    )
    num_installed = len(install_status["installed"])
    num_failed = len(install_status["errors"])

    fg = "green"
    if num_failed >= 0 and num_installed == 0:
        fg = "red"
    elif num_failed > 0 and num_installed > 0:
        fg = "yellow"

    if len(plugins) > 1:
        click.echo()
        click.secho(
            f"Installed {num_installed}/{num_installed+num_failed} plugins", fg=fg
        )

    return num_failed == 0
