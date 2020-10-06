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
from meltano.core.plugin import PluginType, VariantNotFoundError
from meltano.core.project import Project
from meltano.core.tracking import GoogleAnalyticsTracker


class CliError(Exception):
    pass


def print_added_plugin(project, plugin, plugin_def=None, related=False):
    descriptor = plugin.type.descriptor
    if related:
        descriptor = f"related {descriptor}"

    if plugin.should_add_to_file(project):
        click.secho(
            f"Added {descriptor} '{plugin.name}' to your Meltano project", fg="green"
        )
    else:
        click.secho(
            f"Adding {descriptor} '{plugin.name}' to your Meltano project...",
            fg="green",
        )

    if plugin_def:
        repo_url = plugin_def.repo
        if repo_url:
            click.echo(f"Repository:\t{repo_url}")

        docs_url = plugin_def.docs
        if docs_url:
            click.echo(f"Documentation:\t{docs_url}")


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
    variant=None,
):
    try:
        plugin = add_service.add(plugin_type, plugin_name, variant=variant)
        plugin_def = add_service.discovery_service.get_definition(plugin)

        print_added_plugin(project, plugin, plugin_def)
    except PluginAlreadyAddedException as err:
        click.secho(
            f"{plugin_type.descriptor.capitalize()} '{plugin_name}' is already in your Meltano project",
            fg="yellow",
            err=True,
        )
        plugin = err.plugin
    except VariantNotFoundError as err:
        raise CliError(str(err)) from err
    except (PluginNotSupportedException, PluginNotFoundError) as err:
        raise CliError(
            f"{plugin_type.descriptor.capitalize()} '{plugin_name}' is not known to Meltano"
        ) from err

    click.echo()

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
            related_plugin_def = add_service.discovery_service.get_definition(
                related_plugin
            )
            print_added_plugin(
                project, related_plugin, related_plugin_def, related=True
            )
            click.echo()

        added_plugins.extend(related_plugins)

    return added_plugins


def install_status_update(data, reason):
    plugin = data["plugin"]

    if data["status"] == "running":
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
        click.echo()


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
        verb = "Updated" if reason == PluginInstallReason.UPGRADE else "Installed"
        click.secho(f"{verb} {num_installed}/{num_installed+num_failed} plugins", fg=fg)

    return num_failed == 0
