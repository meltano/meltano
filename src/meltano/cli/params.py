"""Click parameter helper decorators."""

from __future__ import annotations

import functools
import typing as t

import click

from meltano.cli.utils import CliError, install_plugins
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationError
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import async_noop

if t.TYPE_CHECKING:
    from meltano.core.project import Project

InstallPlugins = t.Callable[..., t.Coroutine[t.Any, t.Any, bool]]


def _install_plugins_fn(_ctx, _param, value: bool) -> InstallPlugins:
    return install_plugins if value else async_noop  # type: ignore[return-value]


def database_uri_option(func):
    """Database URI Click option decorator.

    args:
        func: The function to decorate.
    """

    @click.option("--database-uri", help="System database URI.")
    def decorate(*args, database_uri=None, **kwargs):
        if database_uri:
            ProjectSettingsService.config_override["database_uri"] = database_uri

        return func(*args, **kwargs)

    return functools.update_wrapper(decorate, func)


def _get_project_auto_install():
    ctx = click.get_current_context()
    project: Project | None = ctx.obj["project"]

    return project and project.settings.get("auto_install")


install_option = click.option(
    "--install/--no-install",
    "install_plugins",
    default=_get_project_auto_install,
    callback=_install_plugins_fn,
    help="Whether or not to install the subject plugin(s) automatically.",
)


class pass_project:  # noqa: N801
    """Pass current project to decorated CLI command function."""

    __name__ = "project"

    def __init__(self, migrate=False):
        """Instantiate decorator.

        args:
            migrate: Flag to perform database migration before passing the project.
        """
        self.migrate = migrate

    def __call__(self, func):
        """Return decorated function.

        args:
            func: The function to decorate.
        """

        @database_uri_option
        def decorate(*args, **kwargs):
            ctx = click.get_current_context()

            project = ctx.obj["project"]
            if not project:
                raise CliError(
                    f"`{ctx.command_path}` must be run inside a Meltano project.\n"  # noqa: EM102
                    "Use `meltano init <project_directory>` to create one.",
                )

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
