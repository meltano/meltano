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
from meltano.core.plugin_install_service import (
    PluginInstallService,
    PluginInstallReason,
)
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker


class CliError(Exception):
    pass


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
):
    try:
        plugin = add_service.add(plugin_type, plugin_name)
        if plugin.should_add_to_file(project):
            click.secho(
                f"Added {plugin_type.descriptor} '{plugin_name}' to your Meltano project",
                fg="green",
            )
        else:
            click.secho(
                f"Adding {plugin_type.descriptor} '{plugin_name}' to your Meltano project...",
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
        raise CliError(
            f"{plugin_type.descriptor.capitalize()} '{plugin_name}' is not known to Meltano"
        ) from err

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_add(plugin_type=plugin_type, plugin_name=plugin_name)

    return plugin


def add_related_plugins(
    project, plugins, add_service: ProjectAddService, plugin_types=list(PluginType)
):
    added_plugins = []
    for plugin_install in plugins:
        related_plugins = add_service.add_related(
            plugin_install, plugin_types=plugin_types
        )
        for related_plugin in related_plugins:
            if related_plugin.should_add_to_file(project):
                click.secho(
                    f"Added related {related_plugin.type.descriptor} '{related_plugin.name}' to your Meltano project",
                    fg="green",
                )
            else:
                click.secho(
                    f"Adding related {related_plugin.type.descriptor} '{related_plugin.name}' to your Meltano project...",
                    fg="green",
                )

        added_plugins.extend(related_plugins)

    return added_plugins


def install_status_update(data, reason):
    plugin = data["plugin"]

    if data["status"] == "running":
        click.echo()
        verb = "Updating" if reason == PluginInstallReason.UPGRADE else "Installing"
        click.secho(f"{verb} {plugin.type.descriptor} '{plugin.name}'...")
    elif data["status"] == "error":
        click.secho(data["message"], fg="red")
        click.secho(data["details"], err=True)
    elif data["status"] == "warning":
        click.secho(f"Warning! {data['message']}.", fg="yellow")
    elif data["status"] == "success":
        verb = "Updated" if reason == PluginInstallReason.UPGRADE else "Installed"
        click.secho(f"{verb} {plugin.type.descriptor} '{plugin.name}'", fg="green")


def install_plugins(project, plugins, reason=PluginInstallReason.INSTALL):
    install_service = PluginInstallService(project)
    install_status = install_service.install_plugins(
        plugins, status_cb=install_status_update, reason=reason
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
        verb = "Updated" if reason == PluginInstallReason.UPGRADE else "Installed"
        click.secho(f"{verb} {num_installed}/{num_installed+num_failed} plugins", fg=fg)

    return num_failed == 0
