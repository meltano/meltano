"""Defines helpers for use by the CLI."""
import logging
import os
import signal
from contextlib import contextmanager
from typing import List, Optional

import click

from meltano.core.logging import setup_logging
from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
    PluginInstallState,
    PluginInstallStatus,
)
from meltano.core.project import Project
from meltano.core.project_add_service import (
    PluginAlreadyAddedException,
    ProjectAddService,
)
from meltano.core.setting_definition import SettingKind
from meltano.core.tracking import GoogleAnalyticsTracker

setup_logging()

logger = logging.getLogger(__name__)

RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
MAGENTA = "magenta"


class CliError(Exception):
    """Exception that is raised when a CLI command fails."""

    def __init__(self, *args, **kwargs):
        """Initialize the exception.

        Args:
            args: Arguments to pass to the Exception constructor.
            kwargs: Keyword arguments to pass to the Exception constructor.
        """
        super().__init__(*args, **kwargs)

        self.printed = False

    def print(self):
        """Print the exception message to the console."""
        if self.printed:
            return

        logger.debug(str(self), exc_info=True)
        click.secho(str(self), fg=RED, err=True)

        self.printed = True


def print_added_plugin(project, plugin, related=False):
    """Print a message indicating that a plugin was added to the project.

    Args:
        project: The project the plugin was added to.
        plugin: The plugin that was added.
        related: Whether the plugin was added as a related plugin.
    """
    descriptor = plugin.type.descriptor
    if related:
        descriptor = f"related {descriptor}"

    if plugin.should_add_to_file():
        click.secho(
            f"Added {descriptor} '{plugin.name}' to your Meltano project", fg=GREEN
        )
    else:
        click.secho(
            f"Adding {descriptor} '{plugin.name}' to your Meltano project...",
            fg=GREEN,
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
        fg=GREEN,
    )
    click.echo()

    namespace_in_blue = click.style("namespace", fg=BLUE)
    click.echo(f"Specify the plugin's {namespace_in_blue}, which will serve as the:")
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
        click.style("(namespace)", fg=BLUE),
        type=str,
        default=plugin_name.replace("-", "_"),
    )


def _prompt_plugin_pip_url(plugin_name: str) -> Optional[str]:
    pip_example_in_blue = click.style("`pip install` argument", fg=BLUE)

    click.echo()
    click.echo(f"Specify the plugin's {pip_example_in_blue}, for example:")
    click.echo("- PyPI package name:")
    click.echo(f"\t{plugin_name}")
    click.echo("- Git repository URL:")
    click.echo(f"\tgit+https://gitlab.com/meltano/{plugin_name}.git")
    click.echo("- local directory, in editable/development mode:")
    click.echo(f"\t-e extract/{plugin_name}")
    click.echo("- 'n' if using a local executable (nothing to install)")
    click.echo()
    click.echo("Default: plugin name as PyPI package name")
    click.echo()

    result = click.prompt(
        click.style("(pip_url)", fg=BLUE), type=str, default=plugin_name
    )
    return None if result == "n" else result


def _prompt_plugin_executable(pip_url: Optional[str], plugin_name: str) -> str:
    derived_from = "`pip_url`"
    prompt_request = "executable name"
    if pip_url is None:
        derived_from = "the plugin name"
        prompt_request = "executable path"

    executable_in_blue = click.style(prompt_request, fg=BLUE)

    click.echo()
    click.echo(f"Specify the plugin's {executable_in_blue}")
    click.echo()
    click.echo(f"Default: name derived from {derived_from}")
    click.echo()

    plugin_basename = os.path.basename(pip_url or plugin_name)
    package_name, _ = os.path.splitext(plugin_basename)
    return click.prompt(click.style("(executable)", fg=BLUE), default=package_name)


def _prompt_plugin_capabilities(plugin_type):
    if plugin_type != PluginType.EXTRACTORS:
        return []

    capabilities_help = click.style("supported Singer features", fg=BLUE)

    click.echo()
    click.echo(
        f"Specify the tap's {capabilities_help} (executable flags), for example:"
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
        click.style("(capabilities)", fg=BLUE),
        type=list,
        default="",
        value_proc=lambda value: [word.strip() for word in value.split(",") if word],
    )


def _prompt_plugin_settings(plugin_type):
    if plugin_type not in {PluginType.EXTRACTORS, PluginType.LOADERS}:
        return []
    singer_type = "tap" if plugin_type == PluginType.EXTRACTORS else "target"
    supported_settings_help = click.style("supported settings", fg=BLUE)

    click.echo()
    click.echo(
        f"Specify the {singer_type}'s {supported_settings_help} (`config.json` keys)"
    )
    click.echo()
    click.echo("Multiple setting names (keys) can be separated using commas.")
    click.echo()
    click.echo(
        "A setting kind can be specified alongside the name (key) by using the `:` delimiter,"
    )
    click.echo("e.g. `port:integer` to set the kind `integer` for the name `port`")
    click.echo()
    click.echo("Supported setting kinds:")
    click.echo(
        " | ".join([click.style(kind.value, fg=MAGENTA) for kind in SettingKind])
    )
    click.echo()
    click.echo(
        "- Credentials and other sensitive setting types should use the "
        + click.style("password", fg=MAGENTA)
        + " kind."
    )
    click.echo(
        "- If not specified, setting kind defaults to "
        + click.style("string", fg=MAGENTA)
        + "."
    )
    click.echo(
        "- Nested properties can be represented using the `.` separator, "
        + 'e.g. `auth.username` for `{ "auth": { "username": value } }`.'
    )
    click.echo(
        f"- To find out what settings a {singer_type} supports, reference its documentation."
    )
    click.echo()
    click.echo("Default: no settings")
    click.echo()

    settings: dict = None
    while settings is None:  # noqa:  WPS426  # allows lambda in loop
        settings_input = click.prompt(
            click.style("(settings)", fg=BLUE),
            type=list,
            default="",
            value_proc=lambda value: [
                setting.strip().partition(":")
                for setting in value.split(",")
                if setting
            ],
        )
        try:
            settings = [
                {"name": name, "kind": kind and SettingKind(kind).value}
                for name, sep, kind in settings_input
            ]
        except ValueError as ex:
            click.secho(str(ex), fg=RED)

    return settings


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
    variant=None,
    inherit_from=None,
    custom=False,
):
    """Add a plugin to the project.

    Args:
        project: The project to add the plugin to.
        plugin_type: The type of plugin to add.
        plugin_name: The name of the plugin to add.
        add_service: The service to use to add the plugin.
        variant: The variant of the plugin to add.
        inherit_from: The name of the plugin to inherit from.
        custom: Whether the plugin is a custom plugin.

    Returns:
        The added plugin.
    """
    plugin_attrs = {}
    if custom:
        namespace = _prompt_plugin_namespace(plugin_type, plugin_name)
        pip_url = _prompt_plugin_pip_url(plugin_name)
        executable = _prompt_plugin_executable(pip_url, plugin_name)
        capabilities = _prompt_plugin_capabilities(plugin_type)
        settings = _prompt_plugin_settings(plugin_type)

        plugin_attrs = {
            "namespace": namespace,
            "pip_url": pip_url,
            "executable": executable,
            "capabilities": capabilities,
            "settings": settings,
        }

    try:  # noqa: WPS229 (allow two-line try)
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
        plugin_descriptor = plugin_type.descriptor.capitalize()

        click.secho(
            f"{plugin_descriptor} '{plugin_name}' already exists in your Meltano project",
            fg=YELLOW,
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
                "To learn more, visit https://www.meltano.com/docs/plugin-management.html#switching-from-one-variant-to-another"
            )

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

            click.echo()
            click.echo(
                "To learn more, visit https://www.meltano.com/docs/plugin-management.html#multiple-variants"
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
    project,
    plugins,
    add_service: ProjectAddService,
    plugin_types: Optional[List[PluginType]] = None,
):
    """Add related plugins to the project.

    Args:
        project: The project to add the plugins to.
        plugins: The plugins to add.
        add_service: PluginAddService instance.
        plugin_types: The plugin types to add.

    Returns:
        The added plugins.
    """
    added_plugins = []

    if plugin_types is None:
        plugin_types = list(PluginType)

    for plugin_install in plugins:
        related_plugins = add_service.add_related(
            plugin_install, plugin_types=plugin_types
        )
        for related_plugin in related_plugins:
            print_added_plugin(project, related_plugin, related=True)
            click.echo()

        added_plugins.extend(related_plugins)

    return added_plugins


def install_status_update(install_state: PluginInstallState):
    """Print the status of plugin installation.

    Used as the callback for PluginInstallService.

    Args:
        install_state (PluginInstallState): The state of the plugin installation.
    """
    plugin = install_state.plugin
    desc = plugin.type.descriptor
    if install_state.status is PluginInstallStatus.RUNNING:
        msg = f"{install_state.verb} {desc} '{plugin.name}'..."
        click.secho(msg)
    elif install_state.status is PluginInstallStatus.ERROR:
        click.secho(install_state.message, fg=RED)
        click.secho(install_state.details, err=True)
    elif install_state.status is PluginInstallStatus.WARNING:
        click.secho(f"Warning! {install_state.message}.", fg=YELLOW)
    elif install_state.status is PluginInstallStatus.SUCCESS:
        msg = f"{install_state.verb} {desc} '{plugin.name}'"
        click.secho(msg, fg=GREEN)


def install_plugins(
    project, plugins, reason=PluginInstallReason.INSTALL, parallelism=None, clean=False
):
    """Install the provided plugins and report results to the console.

    Args:
        project: The project to install the plugins into.
        plugins: The plugins to install.
        reason: The reason for installing the plugins.
        parallelism: The number of parallel processes to use.
        clean: Whether to clean the plugin venv directory before installing.

    Returns:
        The list of installed plugins.
    """
    install_service = PluginInstallService(
        project, status_cb=install_status_update, parallelism=parallelism, clean=clean
    )
    install_results = install_service.install_plugins(plugins, reason=reason)
    num_total = len(install_results)
    num_successful = len([status for status in install_results if status.successful])
    num_skipped = len([status for status in install_results if status.skipped])
    num_failed = num_total - num_successful
    num_installed = num_successful - num_skipped

    fg = GREEN
    if num_failed >= 0 and num_successful == 0:
        fg = RED
    elif num_failed > 0 and num_successful > 0:
        fg = YELLOW

    if len(plugins) > 1:
        verb = "Updated" if reason == PluginInstallReason.UPGRADE else "Installed"
        click.secho(
            f"{verb} {num_installed}/{num_total} plugins",
            fg=fg,
        )
    if num_skipped:
        verb = "Skipped installing"
        click.secho(
            f"{verb} {num_skipped}/{num_total} plugins",
            fg=fg,
        )

    return num_failed == 0


@contextmanager
def propagate_stop_signals(proc):
    """When a stop signal is received, send it to `proc` and wait for it to terminate.

    Args:
        proc: The process to send the stop signal to.

    Yields:
        Nothing.
    """

    def _handler(sig, _):  # noqa: WPS430
        proc.send_signal(sig)
        logger.debug("stopping child process...")
        # unset signal handler, so that even if the child never stops,
        # an additional stop signal will terminate as usual
        signal.signal(signal.SIGTERM, original_termination_handler)

    original_termination_handler = signal.signal(signal.SIGTERM, _handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, original_termination_handler)
