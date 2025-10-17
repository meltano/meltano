"""Click parameter helper decorators."""

from __future__ import annotations

import functools
import typing as t
import uuid
from collections.abc import Callable, Coroutine

import click

from meltano.cli.utils import AutoInstallBehavior, CliError
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationError
from meltano.core.plugin import PluginType
from meltano.core.plugin_install_service import PluginInstallReason, install_plugins
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import async_noop

if t.TYPE_CHECKING:
    from meltano.core.project import Project

_AnyCallable = Callable[..., t.Any]
FC = t.TypeVar("FC", bound=_AnyCallable)

InstallPlugins = Callable[..., Coroutine[t.Any, t.Any, bool]]


def _install_plugins_fn(
    ctx: click.Context,
    _param,
    value: AutoInstallBehavior | None,
) -> InstallPlugins:
    if value is None:
        project: Project | None = ctx.obj["project"]
        auto_install = project and project.settings.get("auto_install")
        behavior = (
            AutoInstallBehavior.install
            if auto_install
            else AutoInstallBehavior.no_install
        )
    else:
        behavior = value

    behavior = value or AutoInstallBehavior.install
    if behavior == AutoInstallBehavior.no_install:
        return async_noop
    if behavior == AutoInstallBehavior.only_install:
        return _install_plugins_and_exit

    return install_plugins


async def _install_plugins_and_exit(*args: t.Any, **kwargs: t.Any) -> t.NoReturn:
    kwargs.pop("reason", None)
    await install_plugins(*args, **kwargs, reason=PluginInstallReason.INSTALL)
    context = click.get_current_context()
    context.exit(code=0)


def database_uri_option(func):  # noqa: ANN001, ANN201
    """Database URI Click option decorator.

    Args:
        func: The function to decorate.
    """

    @click.option("--database-uri", help="System database URI.")
    def decorate(*args, database_uri=None, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if database_uri:
            ProjectSettingsService.config_override["database_uri"] = database_uri

        return func(*args, **kwargs)

    return functools.update_wrapper(decorate, func)


def get_install_options(
    *,
    include_only_install: bool,
) -> tuple[Callable[[FC], FC], ...]:
    """Return install options for CLI commands.

    Args:
        include_only_install: Flag to include the `--only-install` option.

    Returns:
        Tuple of install option decorators.
    """
    install_option = click.option(
        "--install",
        "install_plugins",
        flag_value=AutoInstallBehavior.install.value,
        callback=_install_plugins_fn,
        help="Install the subject plugin(s) automatically.",
    )

    no_install_option = click.option(
        "--no-install",
        "install_plugins",
        flag_value=AutoInstallBehavior.no_install.value,
        callback=_install_plugins_fn,
        help="Do not install the subject plugin(s) automatically.",
    )

    only_install_option = click.option(
        "--only-install",
        "install_plugins",
        flag_value=AutoInstallBehavior.only_install.value,
        callback=_install_plugins_fn,
        help="Only install the subject plugin(s).",
    )

    if include_only_install:
        return install_option, no_install_option, only_install_option

    return install_option, no_install_option


class pass_project:  # noqa: N801
    """Pass current project to decorated CLI command function."""

    __name__ = "project"

    def __init__(self, *, migrate=False) -> None:  # noqa: ANN001
        """Instantiate decorator.

        Args:
            migrate: Flag to perform database migration before passing the project.
        """
        self.migrate = migrate

    def __call__(self, func):  # noqa: ANN001, ANN204
        """Return decorated function.

        Args:
            func: The function to decorate.
        """

        @database_uri_option
        def decorate(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
            ctx = click.get_current_context()

            project = ctx.obj["project"]
            if not project:
                msg = (
                    f"`{ctx.command_path}` must be run inside a Meltano project.\n"
                    "Use `meltano init <project_directory>` to create one."
                )
                raise click.UsageError(msg, ctx=ctx)

            # register the system database connection
            engine, _ = project_engine(project, default=True)

            if self.migrate:
                from meltano.core.migration_service import MigrationService

                try:
                    migration_service = MigrationService(engine)
                    migration_service.upgrade(silent=True)
                except MigrationError as err:
                    raise CliError(str(err)) from err

            func(project, *args, **kwargs)

        return functools.update_wrapper(decorate, func)


class UUIDParamType(click.ParamType):
    """A custom click parameter type for UUIDs."""

    name = "uuid"

    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> uuid.UUID:
        """Convert an input value to a UUID."""
        try:
            return uuid.UUID(value)
        except ValueError:
            self.fail(f"{value} is not a valid UUID.", param, ctx)


class PluginTypeArg(click.Choice):
    """A click parameter that converts a string to a PluginType."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize the PluginTypeArg."""
        super().__init__(PluginType.cli_arguments(), *args, **kwargs)

    def convert(
        self,
        value: str,
        param: click.Parameter | None,  # noqa: ARG002
        ctx: click.Context | None,  # noqa: ARG002
    ) -> PluginType:
        """Convert the value to a PluginType."""
        return PluginType.from_cli_argument(value)
