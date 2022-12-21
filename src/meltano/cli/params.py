"""Click parameter helper decorators."""

from __future__ import annotations

import functools

import click
from click.globals import get_current_context as get_current_click_context

from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationError
from meltano.core.project_settings_service import ProjectSettingsService

from .utils import CliError


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
            ctx = get_current_click_context()

            project = ctx.obj["project"]
            if not project:
                raise CliError(
                    f"`{ctx.command_path}` must be run inside a Meltano project.\n"
                    + "Use `meltano init <project_directory>` to create one."
                )

            # register the system database connection
            engine, _ = project_engine(project, default=True)

            if self.migrate:
                from meltano.core.migration_service import MigrationService

                try:
                    migration_service = MigrationService(engine)
                    migration_service.upgrade(silent=True)
                    migration_service.seed(project)
                except MigrationError as err:
                    raise CliError(str(err))

            func(project, *args, **kwargs)

        return functools.update_wrapper(decorate, func)
