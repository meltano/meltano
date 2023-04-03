"""Defines helpers for use by the CLI."""

from __future__ import annotations

import logging
import os
import signal
import typing as t
from contextlib import contextmanager
from enum import Enum, auto

import click
from click_default_group import DefaultGroup

from meltano.core.error import MeltanoConfigurationError
from meltano.core.logging import setup_logging
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
    PluginInstallStatus,
)
from meltano.core.plugin_lock_service import LockfileAlreadyExistsError
from meltano.core.project_add_service import (
    PluginAddedReason,
    PluginAlreadyAddedException,
    ProjectAddService,
)
from meltano.core.setting_definition import SettingKind
from meltano.core.tracking.contexts import CliContext, CliEvent, ProjectContext

if t.TYPE_CHECKING:
    from meltano.core.plugin.base import PluginRef
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.project_plugins_service import ProjectPluginsService

setup_logging()

logger = logging.getLogger(__name__)


class CliError(Exception):
    """CLI Error."""

    def __init__(self, *args, **kwargs):
        """Instantiate custom CLI Error exception."""
        super().__init__(*args, **kwargs)

        self.printed = False

    def print(self):
        """Print CLI error."""
        if self.printed:
            return

        logger.debug(str(self), exc_info=True)
        click.secho(str(self), fg="red", err=True)

        self.printed = True


def print_added_plugin(
    plugin: ProjectPlugin,
    reason: PluginAddedReason = PluginAddedReason.USER_REQUEST,
) -> None:
    """Print added plugin."""
    descriptor = plugin.type.descriptor
    if reason is PluginAddedReason.RELATED:
        descriptor = f"related {descriptor}"
    elif reason is PluginAddedReason.REQUIRED:
        descriptor = f"required {descriptor}"

    if plugin.should_add_to_file():
        click.secho(
            f"Added {descriptor} '{plugin.name}' to your Meltano project",
            fg="green",
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
    click.echo(
        f"\nSpecify the plugin's {click.style('namespace', fg='blue')}, which "
        "will serve as the:\n"
        "- identifier to find related/compatible plugins",
    )
    if plugin_type == PluginType.EXTRACTORS:
        click.echo(
            "- default database schema (`load_schema` extra),"
            "  for use by loaders that support a target schema",
        )
    elif plugin_type == PluginType.LOADERS:
        click.echo(
            "- default target database dialect (`dialect` extra),"
            "  for use by transformers that connect with the database",
        )
    click.echo(
        "\nHit Return to accept the default: plugin name with underscores "
        "instead of dashes\n",
    )

    return click.prompt(
        click.style("(namespace)", fg="blue"),
        type=str,
        default=plugin_name.replace("-", "_"),
    )


def _prompt_plugin_pip_url(plugin_name: str) -> str | None:
    click.echo(
        "\nSpecify the plugin's "
        f"{click.style('`pip install` argument', fg='blue')}, for example:"
        "- PyPI package name:\n"
        f"\t{plugin_name}\n"
        "- Git repository URL:\n"
        "\tgit+https://<PLUGIN REPO URL>.git\n"
        "- local directory, in editable/development mode:\n"
        f"\t-e extract/{plugin_name}\n"
        "- 'n' if using a local executable (nothing to install)\n\n"
        "Default: plugin name as PyPI package name\n",
    )
    result = click.prompt(
        click.style("(pip_url)", fg="blue"),
        type=str,
        default=plugin_name,
    )
    return None if result == "n" else result


def _prompt_plugin_executable(pip_url: str | None, plugin_name: str) -> str:
    derived_from = "`pip_url`"
    prompt_request = "executable name"
    if pip_url is None:
        derived_from = "the plugin name"
        prompt_request = "executable path"
    click.echo(
        f"\nSpecify the plugin's {click.style(prompt_request, fg='blue')}\n"
        f"\nDefault: name derived from {derived_from}\n",
    )
    plugin_basename = os.path.basename(pip_url or plugin_name)
    package_name, _ = os.path.splitext(plugin_basename)
    return click.prompt(click.style("(executable)", fg="blue"), default=package_name)


def _prompt_plugin_capabilities(plugin_type):
    if plugin_type != PluginType.EXTRACTORS:
        return []

    click.echo(
        f"\nSpecify the tap's {click.style('supported Singer features', fg='blue')} "
        "(executable flags), for example:\n"
        "\t`catalog`: supports the `--catalog` flag\n"
        "\t`discover`: supports the `--discover` flag\n"
        "\t`properties`: supports the `--properties` flag\n"
        "\t`state`: supports the `--state` flag\n\n"
        "To find out what features a tap supports, reference its "
        "documentation or try one of the tricks under"
        "https://docs.meltano.com/guide/integration#troubleshooting.\n\n"
        "Multiple capabilities can be separated using commas.\n\n"
        "Default: no capabilities\n",
    )

    return click.prompt(
        click.style("(capabilities)", fg="blue"),
        type=list,
        default=[],
        value_proc=lambda value: [word.strip() for word in value.split(",")]
        if value
        else [],
    )


def _prompt_plugin_settings(plugin_type):
    if plugin_type not in {
        PluginType.EXTRACTORS,
        PluginType.LOADERS,
        PluginType.TRANSFORMERS,
    }:
        return []

    click.echo(
        f"\nSpecify the {plugin_type.descriptor}'s "
        f"{click.style('supported settings', fg='blue')}\n"
        "Multiple setting names (keys) can be separated using commas.\n\n"
        "A setting kind can be specified alongside the name (key) by using "
        "the `:` delimiter,\n"
        "e.g. `port:integer` to set the kind `integer` for the name `port`\n\n"
        "Supported setting kinds:",
    )
    click.echo(
        " | ".join([click.style(kind.value, fg="magenta") for kind in SettingKind]),
    )
    click.echo(
        "\n- Credentials and other sensitive setting types should use the "
        f"{click.style('password', fg='magenta')} kind.\n"
        "- If not specified, setting kind defaults to "
        f"{click.style('string', fg='magenta')}.\n"
        "- Nested properties can be represented using the `.` separator, "
        'e.g. `auth.username` for `{ "auth": { "username": value } }`.\n'
        f"- To find out what settings a {plugin_type.descriptor} supports, "
        "reference its documentation.\n"
        "\nDefault: no settings\n",
    )

    settings: dict | None = None
    while settings is None:  # noqa:  WPS426  # allows lambda in loop
        settings_input = click.prompt(
            click.style("(settings)", fg="blue"),
            type=list,
            default=[],
            value_proc=lambda value: [
                setting.strip().partition(":") for setting in value.split(",")
            ]
            if value
            else [],
        )
        try:
            settings = [
                {"name": name, "kind": kind and SettingKind(kind).value}
                for name, sep, kind in settings_input
            ]
        except ValueError as ex:
            click.secho(str(ex), fg="red")

    return settings


def add_plugin(
    project: Project,
    plugin_type: PluginType,
    plugin_name: str,
    add_service: ProjectAddService,
    variant=None,
    inherit_from=None,
    custom=False,
    lock=True,
):
    """Add Plugin to given Project."""
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

    try:
        plugin = add_service.add(
            plugin_type,
            plugin_name,
            variant=variant,
            inherit_from=inherit_from,
            lock=lock,
            **plugin_attrs,
        )
        print_added_plugin(plugin)
    except PluginAlreadyAddedException as err:
        plugin = err.plugin
        click.secho(
            (
                f"{plugin_type.descriptor.capitalize()} '{plugin_name}' "
                "already exists in your Meltano project"
            ),
            fg="yellow",
            err=True,
        )
        if variant and variant != plugin.variant:
            new_plugin = err.new_plugin
            click.echo(
                f"\nTo switch from the current '{plugin.variant}' variant "
                f"to '{new_plugin.variant}':\n"
                "1. Update `variant` and `pip_url` in your `meltano.yml` "
                "project file:\n"
                f"\tname: {plugin.name}\n"
                f"\tvariant: {new_plugin.variant}\n"
                f"\tpip_url: {new_plugin.pip_url}\n"
                "2. Reinstall the plugin:\n"
                f"\tmeltano install {plugin_type.singular} {plugin.name}\n"
                "3. Check if the configuration is still valid (and make "
                "changes until it is):\n"
                f"\tmeltano config {plugin.name} list\n\n"
                "To learn more, visit "
                "https://docs.meltano.com/guide/plugin-management#switching-from-one-variant-to-another\n\n"  # noqa: E501
                f"Alternatively, to keep the existing '{plugin.name}' with "
                f"variant '{new_plugin.variant}', add variant '{new_plugin.variant}' "
                "as a separate plugin with its own unique name:\n"
                f"\tmeltano add {plugin_type.singular} "
                f"{plugin.name}--{new_plugin.variant} --inherit-from {plugin.name} "
                f"--variant {new_plugin.variant}\n\n"
                "To learn more, visit "
                "https://docs.meltano.com/guide/plugin-management#multiple-variants",
            )
        else:
            click.echo(
                "To add it to your project another time so that each can be "
                "configured differently,\n"
                "add a new plugin inheriting from the existing one with its "
                "own unique name:\n"
                f"\tmeltano add {plugin_type.singular} {plugin.name}--new "
                f"--inherit-from {plugin.name}",
            )
    except LockfileAlreadyExistsError as exc:
        # TODO: This is a BasePlugin, not a ProjectPlugin, as this method
        # should return! Results in `KeyError: venv_name`
        plugin = exc.plugin
        click.secho(
            f"Plugin definition is already locked at {exc.path}.",
            fg="yellow",
            err=True,
        )
        click.echo(
            "You can remove the file manually to avoid using a stale definition.",
        )

    click.echo()

    return plugin


def add_required_plugins(
    project: Project,
    plugins: list[ProjectPlugin],
    add_service: ProjectAddService,
    lock: bool = True,
):
    """Add any Plugins required by the given Plugin."""
    added_plugins = []
    for plugin_install in plugins:
        required_plugins = add_service.add_required(
            plugin_install,
            lock=lock,
        )
        for required_plugin in required_plugins:
            print_added_plugin(required_plugin, reason=PluginAddedReason.REQUIRED)
            click.echo()

        added_plugins.extend(required_plugins)

    return added_plugins


def install_status_update(install_state):
    """
    Print the status of plugin installation.

    Used as the callback for PluginInstallService.
    """
    plugin = install_state.plugin
    desc = plugin.type.descriptor
    if install_state.status in {
        PluginInstallStatus.RUNNING,
        PluginInstallStatus.SKIPPED,
    }:
        msg = f"{install_state.verb} {desc} '{plugin.name}'..."
        click.secho(msg)
    elif install_state.status is PluginInstallStatus.ERROR:
        click.secho(install_state.message, fg="red")
        click.secho(install_state.details, err=True)
    elif install_state.status is PluginInstallStatus.WARNING:
        click.secho(f"Warning! {install_state.message}.", fg="yellow")
    elif install_state.status is PluginInstallStatus.SUCCESS:
        msg = f"{install_state.verb} {desc} '{plugin.name}'"
        click.secho(msg, fg="green")


def install_plugins(
    project,
    plugins,
    reason=PluginInstallReason.INSTALL,
    parallelism=None,
    clean=False,
    force=False,
):
    """Install the provided plugins and report results to the console."""
    install_service = PluginInstallService(
        project,
        status_cb=install_status_update,
        parallelism=parallelism,
        clean=clean,
        force=force,
    )
    install_results = install_service.install_plugins(plugins, reason=reason)
    num_successful = len([status for status in install_results if status.successful])
    num_skipped = len([status for status in install_results if status.skipped])
    num_failed = len(install_results) - num_successful

    fg = "green"
    if num_failed >= 0 and num_successful == 0:
        fg = "red"
    elif num_failed > 0 and num_successful > 0:
        fg = "yellow"

    if len(plugins) > 1:
        verb = "Updated" if reason == PluginInstallReason.UPGRADE else "Installed"
        click.secho(
            f"{verb} {num_successful-num_skipped}/{num_successful+num_failed} plugins",
            fg=fg,
        )
    if num_skipped:
        verb = "Skipped installing"
        click.secho(
            f"{verb} {num_skipped}/{num_successful+num_failed} plugins",
            fg=fg,
        )

    return num_failed == 0


@contextmanager
def propagate_stop_signals(proc):
    """Propagate stop signals to `proc`, then wait for it to terminate."""

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


def check_dependencies_met(
    plugin_refs: list[PluginRef],
    plugins_service: ProjectPluginsService,
) -> tuple[bool, str]:
    """Check dependencies of added plugins are met.

    Args:
        plugins: List of plugins to be added.
        plugin_service: Plugin service to use when checking for dependencies.

    Returns:
        A tuple with dependency check outcome (True/False), and a string
        message with details of the check.
    """
    passed = True
    messages = []

    for plugin in plugin_refs:
        if plugin.type == PluginType.TRANSFORMS:
            # check that the `dbt` transformer plugin is installed
            try:
                plugins_service.get_transformer()
            except PluginNotFoundError:
                passed = False
                messages.append(
                    f"Plugin '{plugin.name}' requires a transformer plugin. "
                    "Please first add a transformer using `meltano add transformer`.",
                )
    if passed:
        message = "All dependencies met"
    else:
        message = f"Dependencies not met: {'; '.join(messages)}"
    return passed, message


def activate_environment(
    ctx: click.Context,
    project: Project,
    required: bool = False,
) -> None:
    """Activate the selected environment.

    The selected environment is whatever was selected with the `--environment`
    option, or the default environment (set in `meltano.yml`) otherwise.

    Args:
        ctx: The Click context, used to determine the selected environment.
        project: The project for which the environment will be activated.
    """
    if ctx.obj.get("selected_environment"):
        project.activate_environment(ctx.obj["selected_environment"])
        # Update the project context being used for telemetry:
        project_ctx = next(
            ctx
            for ctx in ctx.obj["tracker"].contexts
            if isinstance(ctx, ProjectContext)
        )
        project_ctx.environment_name = ctx.obj["selected_environment"]

    elif required:
        raise MeltanoConfigurationError(
            reason="A Meltano environment must be specified",
            instruction="Set the `default_environment` option in "
            "`meltano.yml`, or the `--environment` CLI option",
        )


def activate_explicitly_provided_environment(
    ctx: click.Context,
    project: Project,
) -> None:
    """Activate the selected environment if it has been explicitly set.

    Some commands (e.g. `config`, `job`, etc.) do not respect the configured
    `default_environment`, and will only run with an environment active if it
    has been explicitly set (e.g. with the `--environment` CLI option).

    Args:
        ctx: The Click context, used to determine the selected environment.
        project: The project for which the environment will be activated.
    """
    if ctx.obj.get("is_default_environment"):
        logger.info(
            f"The default environment {ctx.obj['selected_environment']!r} will "
            f"be ignored for `meltano {ctx.command.name}`. To configure a specific "
            "environment, please use the option `--environment=<environment name>`.",
        )
        project.deactivate_environment()
    else:
        activate_environment(ctx, project)


class CliEnvironmentBehavior(Enum):
    """Enum of the different Meltano environment activation behaviours."""

    # Use explicit environment, or `default_environment`, or fail.
    environment_required = auto()

    # Use explicit environment, or `default_environment`, or no environment.
    environment_optional_use_default = auto()

    # Use explicit environment, or no environment; ignore `default_environment`.
    environment_optional_ignore_default = auto()


def enact_environment_behavior(
    behavior: CliEnvironmentBehavior | None,
    ctx: click.Context,
) -> None:
    """Activate the environment in the specified way."""
    if behavior is None or "selected_environment" not in ctx.obj:
        return
    if behavior is CliEnvironmentBehavior.environment_optional_use_default:
        activate_environment(ctx, ctx.obj["project"], required=False)
    elif behavior is CliEnvironmentBehavior.environment_required:
        activate_environment(ctx, ctx.obj["project"], required=True)
    elif behavior is CliEnvironmentBehavior.environment_optional_ignore_default:
        activate_explicitly_provided_environment(ctx, ctx.obj["project"])


class InstrumentedCmdMixin:
    """Shared functionality for all instrumented commands."""

    def __init__(
        self,
        *args,
        environment_behavior: CliEnvironmentBehavior | None = None,
        **kwargs,
    ):
        """Initialize the `InstrumentedCmdMixin`.

        Args:
            args: Arguments to pass to the parent class.
            environment_behavior: The behavior to use regarding the activation
                of the Meltano environment for this command.
            kwargs: Keyword arguments to pass to the parent class.
        """
        self.environment_behavior = environment_behavior
        super().__init__(*args, **kwargs)


class InstrumentedGroupMixin(InstrumentedCmdMixin):
    """Shared functionality for all instrumented groups."""

    def invoke(self, ctx: click.Context):
        """Update the telemetry context and invoke the group."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)
        if ctx.obj.get("tracker"):
            ctx.obj["tracker"].add_contexts(CliContext.from_click_context(ctx))
        super().invoke(ctx)


class InstrumentedDefaultGroup(InstrumentedGroupMixin, DefaultGroup):
    """Click group with telemetry instrumentation and a default command."""


class InstrumentedGroup(InstrumentedGroupMixin, click.Group):
    """Click group with telemetry instrumentation."""


class InstrumentedCmd(InstrumentedCmdMixin, click.Command):
    """Click command that automatically fires telemetry events when invoked.

    Both starting and ending events are fired. The ending event fired is
    dependent on whether invocation of the command resulted in an Exception.
    """

    def invoke(self, ctx: click.Context):
        """Invoke the requested command firing start and events accordingly."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)
        if ctx.obj.get("tracker"):
            tracker = ctx.obj["tracker"]
            tracker.add_contexts(CliContext.from_click_context(ctx))
            tracker.track_command_event(CliEvent.started)
            try:
                super().invoke(ctx)
            except Exception:
                tracker.track_command_event(CliEvent.failed)
                raise
            tracker.track_command_event(CliEvent.completed)
        else:
            super().invoke(ctx)


class PartialInstrumentedCmd(InstrumentedCmdMixin, click.Command):
    """Click command with partial telemetry instrumentation.

    Only automatically fires a 'start' event.
    """

    def invoke(self, ctx):
        """Invoke the requested command firing only a start event."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)
        if ctx.obj.get("tracker"):
            ctx.obj["tracker"].add_contexts(CliContext.from_click_context(ctx))
            ctx.obj["tracker"].track_command_event(CliEvent.started)
        super().invoke(ctx)
