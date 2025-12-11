"""Defines helpers for use by the CLI."""

from __future__ import annotations

import os
import signal
import sys
import typing as t
from contextlib import contextmanager
from enum import Enum, auto

import click
import structlog
from click_default_group import DefaultGroup

from meltano.cli._didyoumean import DYMGroup
from meltano.core.error import MeltanoConfigurationError
from meltano.core.logging import setup_logging
from meltano.core.plugin.base import PluginDefinition, PluginType
from meltano.core.plugin.error import InvalidPluginDefinitionError, PluginNotFoundError
from meltano.core.project_add_service import (
    PluginAddedReason,
    PluginAlreadyAddedException,
)
from meltano.core.project_plugins_service import AddedPluginFlags
from meltano.core.setting_definition import SettingKind
from meltano.core.tracking.contexts import CliContext, CliEvent, ProjectContext
from meltano.core.version_check import VersionCheckService

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

if t.TYPE_CHECKING:
    from meltano.core.plugin.base import PluginRef
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project
    from meltano.core.project_add_service import ProjectAddService
    from meltano.core.project_plugins_service import ProjectPluginsService

setup_logging()

logger = structlog.stdlib.get_logger(__name__)

# Commands that should skip version check
EXCLUDED_VERSION_CHECK_COMMANDS = {"version", "upgrade", "init"}


class CliError(Exception):
    """CLI Error."""

    def __init__(self, *args: t.Any, exit_code: int = 1, **kwargs: t.Any) -> None:
        """Instantiate custom CLI Error exception."""
        super().__init__(*args, **kwargs)

        self.exit_code = exit_code
        self.printed = False

    def print(self) -> None:
        """Print CLI error."""
        if self.printed:
            return

        logger.error(str(self), exc_info=self.__cause__)

        self.printed = True


def print_added_plugin(
    plugin: ProjectPlugin,
    reason: PluginAddedReason = PluginAddedReason.USER_REQUEST,
    *,
    flags: AddedPluginFlags = AddedPluginFlags.ADDED,
) -> None:
    """Print added plugin."""
    descriptor = plugin.type.descriptor
    if reason is PluginAddedReason.RELATED:
        descriptor = f"related {descriptor}"
    elif reason is PluginAddedReason.REQUIRED:
        descriptor = f"required {descriptor}"

    match flags:
        case AddedPluginFlags.ADDED:
            action, preposition = "Added", "to"
        case AddedPluginFlags.UPDATED:
            action, preposition = "Updated", "in"
        case AddedPluginFlags.NOT_ADDED:
            action, preposition = "Initialized", "in"
        case _:  # pragma: no cover
            t.assert_never(flags)

    click.secho(
        f"{action} {descriptor} '{plugin.name}' {preposition} your project",
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

    if repo_url := plugin.repo:
        click.echo(f"Repository:\t{repo_url}")

    if docs_url := plugin.docs:
        click.echo(f"Documentation:\t{docs_url}")

    if plugin.python:
        click.echo(f"Python Version:\t{plugin.python}")


def _prompt_plugin_namespace(plugin_type, plugin_name):  # noqa: ANN001, ANN202
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
    plugin_basename = os.path.basename(pip_url or plugin_name)  # noqa: PTH119
    package_name, _ = os.path.splitext(plugin_basename)  # noqa: PTH122
    return click.prompt(click.style("(executable)", fg="blue"), default=package_name)


def _prompt_plugin_capabilities(plugin_type):  # noqa: ANN001, ANN202
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


def _prompt_plugin_settings(plugin_type: PluginType) -> list[dict[str, t.Any]]:
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

    settings: list | None = None
    while settings is None:  # allows lambda in loop
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


def add_plugin(  # noqa: ANN201
    plugin_type: PluginType,
    plugin_name: str,
    *,
    python: str | None = None,
    add_service: ProjectAddService,
    variant: str | None = None,
    inherit_from: str | None = None,
    custom: bool = False,
    update: bool = False,
    plugin_yaml: dict | None = None,
):
    """Add Plugin to given Project."""
    if custom:
        # XXX: For backwards compatibility, the namespace must be prompted for first.
        namespace = _prompt_plugin_namespace(plugin_type, plugin_name)
        pip_url = _prompt_plugin_pip_url(plugin_name)
        plugin_attrs = {
            "namespace": namespace,
            "pip_url": pip_url,
            "executable": _prompt_plugin_executable(pip_url, plugin_name),
            "capabilities": _prompt_plugin_capabilities(plugin_type),
            "settings": _prompt_plugin_settings(plugin_type),
        }
    else:
        plugin_attrs = {}

    if plugin_yaml is not None:
        try:
            plugin_definition = PluginDefinition.parse(
                {
                    "plugin_type": plugin_type,
                    **plugin_yaml,
                },
            )
        except TypeError as e:
            raise InvalidPluginDefinitionError(plugin_yaml) from e

        # exclude unspecified properties
        plugin_definition.extras.clear()

        plugin_attrs = plugin_definition.canonical()  # type: ignore[assignment]

        plugin_name = plugin_attrs.pop("name")
        variant = plugin_attrs.pop("variant", variant)
        python = plugin_attrs.pop("python", python)

    try:
        plugin, flags = add_service.add_with_flags(
            plugin_type,
            plugin_name,
            variant=variant,
            inherit_from=inherit_from,
            update=update,
            python=python,
            **plugin_attrs,
        )
        print_added_plugin(plugin, flags=flags)
    except PluginAlreadyAddedException as err:
        plugin = err.plugin  # type: ignore[assignment]
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
                "https://docs.meltano.com/guide/plugin-management#switching-from-one-variant-to-another\n\n"
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

    click.echo()

    return plugin


def add_required_plugins(  # noqa: ANN201
    plugins: list[ProjectPlugin],
    add_service: ProjectAddService,
    *,
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


@contextmanager
def propagate_stop_signals(proc):  # noqa: ANN001, ANN201
    """Propagate stop signals to `proc`, then wait for it to terminate."""

    def _handler(sig, _) -> None:  # noqa: ANN001
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


def check_dependencies_met(  # noqa: D417
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


def activate_environment(  # noqa: D417
    ctx: click.Context,
    project: Project,
    *,
    required: bool = False,
) -> None:
    """Activate the selected environment.

    The selected environment is whatever was selected with the `--environment`
    option, or the default environment (set in `meltano.yml`) otherwise.

    Args:
        ctx: The Click context, used to determine the selected environment.
        project: The project for which the environment will be activated.
    """
    if env := ctx.obj.get("selected_environment"):
        project.activate_environment(env)
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
            f"The default environment {ctx.obj['selected_environment']!r} will "  # noqa: G004
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
        *args,  # noqa: ANN002
        environment_behavior: CliEnvironmentBehavior | None = None,
        **kwargs,  # noqa: ANN003
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

    def invoke(self, ctx: click.Context) -> None:
        """Update the telemetry context and invoke the group."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)
        if ctx.obj.get("tracker"):
            ctx.obj["tracker"].add_contexts(CliContext.from_click_context(ctx))
        # Typing these mixin hierarchies is a bit messy, so we'll just ignore it here
        # https://mypy.readthedocs.io/en/latest/more_types.html#mixin-classes
        super().invoke(ctx)  # type: ignore[misc]


class InstrumentedDefaultGroup(InstrumentedGroupMixin, DefaultGroup, DYMGroup):
    """Click group with telemetry instrumentation and a default command."""


class InstrumentedGroup(InstrumentedGroupMixin, DYMGroup):
    """Click group with telemetry instrumentation."""


class _BaseMeltanoCommand(click.Command):
    """Base class for all Meltano commands."""

    def _perform_version_check(self, ctx: click.Context) -> None:
        """Perform version check if conditions are met."""
        # Skip version check for certain commands
        if self.name in EXCLUDED_VERSION_CHECK_COMMANDS:
            return

        # Skip if project not available or version check disabled
        project: Project | None = ctx.obj.get("project")
        if project is None or not ctx.obj.get("version_check_enabled", False):
            return

        version_service = VersionCheckService(project)

        if (result := version_service.check_version()) and result.is_outdated:
            # Display version update message
            logger.warning(version_service.format_update_message(result))


class InstrumentedCmd(InstrumentedCmdMixin, _BaseMeltanoCommand):
    """Click command that automatically fires telemetry events when invoked.

    Both starting and ending events are fired. The ending event fired is
    dependent on whether invocation of the command resulted in an Exception.
    """

    def invoke(self, ctx: click.Context) -> None:
        """Invoke the requested command firing start and events accordingly."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)

        # Perform version check for actual commands (not excluded ones)
        self._perform_version_check(ctx)

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


class PartialInstrumentedCmd(InstrumentedCmdMixin, _BaseMeltanoCommand):
    """Click command with partial telemetry instrumentation.

    Only automatically fires a 'start' event.
    """

    def invoke(self, ctx) -> None:  # noqa: ANN001
        """Invoke the requested command firing only a start event."""
        ctx.ensure_object(dict)
        enact_environment_behavior(self.environment_behavior, ctx)

        # Perform version check for actual commands (not excluded ones)
        self._perform_version_check(ctx)

        if ctx.obj.get("tracker"):
            ctx.obj["tracker"].add_contexts(CliContext.from_click_context(ctx))
            ctx.obj["tracker"].track_command_event(CliEvent.started)
        super().invoke(ctx)


class AutoInstallBehavior(StrEnum):
    """Enum of the different behaviors for automatic plugin installation."""

    install = auto()
    no_install = auto()
    only_install = auto()


def infer_plugin_type(plugin_name: str) -> PluginType:
    """Infer the plugin type from the plugin name."""
    if plugin_name.startswith("tap-"):
        return PluginType.EXTRACTORS
    if plugin_name.startswith("target-"):
        return PluginType.LOADERS

    return PluginType.UTILITIES
