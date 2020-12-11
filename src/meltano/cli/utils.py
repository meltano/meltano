import logging
import sys
from typing import List

import click
from meltano.core.logging import setup_logging
from meltano.core.plugin import PluginType, VariantNotFoundError
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)
from meltano.core.project import Project
from meltano.core.project_add_service import (
    PluginAlreadyAddedException,
    PluginNotSupportedException,
    ProjectAddService,
)
from meltano.core.tracking import GoogleAnalyticsTracker

setup_logging()

logger = logging.getLogger(__name__)


class CliError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.printed = False

    def print(self):
        if self.printed:
            return

        logger.debug(str(self), exc_info=True)
        click.secho(str(self), fg="red")

        self.printed = True


def print_added_plugin(project, plugin, related=False):
    descriptor = plugin.type.descriptor
    if related:
        descriptor = f"related {descriptor}"

    if plugin.should_add_to_file():
        click.secho(
            f"Added {descriptor} '{plugin.name}' to your Meltano project", fg="green"
        )
    else:
        click.secho(
            f"Adding {descriptor} '{plugin.name}' to your Meltano project...",
            fg="green",
        )

    inherit_from = plugin.inherit_from
    has_variant = plugin.is_variant_set
    variant_label = plugin.variant_label(plugin.variant)
    if inherit_from:
        if has_variant:
            inherit_from = f"{inherit_from}, variant {variant_label}"

        click.echo(f"Inherit from:\t{inherit_from}")
    elif has_variant:
        click.echo(f"Variant:\t{variant_label}")

    repo_url = plugin.repo
    if repo_url:
        click.echo(f"Repository:\t{repo_url}")

    docs_url = plugin.docs
    if docs_url:
        click.echo(f"Documentation:\t{docs_url}")


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
    variant=None,
    inherit_from=None,
):
    try:
        plugin = add_service.add(
            plugin_type, plugin_name, variant=variant, inherit_from=inherit_from
        )
        print_added_plugin(project, plugin)
    except PluginAlreadyAddedException as err:
        plugin = err.plugin

        click.secho(
            f"{plugin_type.descriptor.capitalize()} '{plugin_name}' already exists in your Meltano project",
            fg="yellow",
            err=True,
        )

        if variant and variant != plugin.variant:
            variant = plugin.find_variant(variant)

            click.echo()
            click.echo(
                f"To switch from the current '{plugin.variant}' variant to '{variant.name}':"
            )
            click.echo(
                "1. Update `variant` and `pip_url` in your `meltano.yml` project file:"
            )
            click.echo(f"\tname: {plugin.name}")
            click.echo(f"\tvariant: {variant.name}")
            click.echo(f"\tpip_url: {variant.pip_url}")

            click.echo("2. Reinstall the plugin:")
            click.echo(f"\tmeltano install {plugin_type.singular} {plugin.name}")

            click.echo(
                "3. Check if the configuration is still valid (and make changes until it is):"
            )
            click.echo(f"\tmeltano config {plugin.name} list")

            click.echo()
            click.echo(
                f"Alternatively, to keep the existing '{plugin.name}' with variant '{plugin.variant}',"
            )
            click.echo(
                f"add variant '{variant.name}' as a separate plugin with its own unique name:"
            )
            click.echo(
                f"\tmeltano add {plugin_type.singular} {plugin.name}--{variant.name} --inherit-from {plugin.name} --variant {variant.name}"
            )
        else:
            click.echo(
                "To add it to your project another time so that each can be configured differently,"
            )
            click.echo(
                "add a new plugin inheriting from the existing one with its own unique name:"
            )
            click.echo(
                f"\tmeltano add {plugin_type.singular} {plugin.name}--new --inherit-from {plugin.name}"
            )
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
            print_added_plugin(project, related_plugin, related=True)
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
