import logging
import os
import sys
from typing import List

import click
from meltano.core.logging import setup_logging
from meltano.core.plugin import PluginType
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


def _prompt_plugin_namespace(plugin_type, plugin_name):
    click.secho(
        f"Adding new custom {plugin_type.descriptor} with name '{plugin_name}'...",
        fg="green",
    )
    click.echo()

    click.echo(
        f"Specify the plugin's {click.style('namespace', fg='blue')}, which will serve as the:"
    )
    click.echo("- identifier to find related/compatible plugins")
    if plugin_type == PluginType.EXTRACTORS:
        click.echo("- default database schema (`load_schema` extra),")
        click.echo("  for use by loaders that support a target schema")
    elif plugin_type == PluginType.LOADERS:
        click.echo("- default target database dialect (`dialect` extra),")
        click.echo("  for use by transformers that connect with the database")
    click.echo()

    click.echo(
        "Hit Return to accept the default: plugin name with underscores instead of dashes"
    )
    click.echo()

    return click.prompt(
        click.style("(namespace)", fg="blue"),
        type=str,
        default=plugin_name.replace("-", "_"),
    )


def _prompt_plugin_pip_url(plugin_name):
    click.echo()
    click.echo(
        f"Specify the plugin's {click.style('`pip install` argument', fg='blue')}, for example:"
    )
    click.echo("- PyPI package name:")
    click.echo(f"\t{plugin_name}")
    click.echo("- Git repository URL:")
    click.echo(f"\tgit+https://gitlab.com/meltano/{plugin_name}.git")
    click.echo("- local directory, in editable/development mode:")
    click.echo(f"\t-e extract/{plugin_name}")
    click.echo()
    click.echo("Default: plugin name as PyPI package name")
    click.echo()

    return click.prompt(
        click.style("(pip_url)", fg="blue"), type=str, default=plugin_name
    )


def _prompt_plugin_executable(pip_url):
    click.echo()
    click.echo(f"Specify the package's {click.style('executable name', fg='blue')}")
    click.echo()
    click.echo("Default: package name derived from `pip_url`")
    click.echo()

    package_name, _ = os.path.splitext(os.path.basename(pip_url))
    return click.prompt(click.style("(executable)", fg="blue"), default=package_name)


def _prompt_plugin_capabilities(plugin_type):
    if plugin_type != PluginType.EXTRACTORS:
        return []

    click.echo()
    click.echo(
        f"Specify the tap's {click.style('supported Singer features', fg='blue')} (executable flags), for example:"
    )
    click.echo("\t`catalog`: supports the `--catalog` flag")
    click.echo("\t`discover`: supports the `--discover` flag")
    click.echo("\t`properties`: supports the `--properties` flag")
    click.echo("\t`state`: supports the `--state` flag")
    click.echo()
    click.echo(
        "To find out what features a tap supports, reference its documentation or try one"
    )
    click.echo(
        "of the tricks under https://meltano.com/docs/contributor-guide.html#how-to-test-a-tap."
    )
    click.echo()
    click.echo("Multiple capabilities can be separated using commas.")
    click.echo()
    click.echo("Default: no capabilities")
    click.echo()

    return click.prompt(
        click.style("(capabilities)", fg="blue"),
        type=list,
        default=[],
        value_proc=lambda value: [word.strip() for word in value.split(",")],
    )


def _prompt_plugin_settings(plugin_type):
    if plugin_type not in {PluginType.EXTRACTORS, PluginType.LOADERS}:
        return []

    singer_type = "tap" if plugin_type == PluginType.EXTRACTORS else "target"

    click.echo()
    click.echo(
        f"Specify the {singer_type}'s {click.style('supported settings', fg='blue')} (`config.json` keys)"
    )
    click.echo()
    click.echo("Nested properties can be represented using the `.` separator,")
    click.echo('e.g. `auth.username` for `{ "auth": { "username": value } }`.')
    click.echo()
    click.echo(
        f"To find out what settings a {singer_type} supports, reference its documentation."
    )
    click.echo()
    click.echo("Multiple setting names (keys) can be separated using commas.")
    click.echo()
    click.echo("Default: no settings")
    click.echo()

    settings = click.prompt(
        click.style("(settings)", fg="blue"),
        type=list,
        default=[],
        value_proc=lambda value: [word.strip() for word in value.split(",")],
    )
    return [{"name": name} for name in settings]


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
    variant=None,
    inherit_from=None,
    custom=False,
):
    plugin_attrs = {}
    if custom:
        namespace = _prompt_plugin_namespace(plugin_type, plugin_name)
        pip_url = _prompt_plugin_pip_url(plugin_name)
        executable = _prompt_plugin_executable(pip_url)
        capabilities = _prompt_plugin_capabilities(plugin_type)
        settings = _prompt_plugin_settings(plugin_type)

        plugin_attrs = {
            "namespace": namespace,
            "pip_url": pip_url,
            "executable": executable,
            "capabilities": capabilities,
            "settings": settings,
        }

    try:
        plugin = add_service.add(
            plugin_type,
            plugin_name,
            variant=variant,
            inherit_from=inherit_from,
            **plugin_attrs,
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
                "\tmeltano add {type} {name}--{variant} --inherit-from {name} --variant {variant}".format(
                    type=plugin_type.singular, name=plugin.name, variant=variant.name
                )
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
