import functools
import urllib
import click
import click.globals
import os
from pathlib import Path

from .utils import CliError

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import pop_all
from meltano.core.migration_service import MigrationService, MigrationError
from meltano.core.db import project_engine


def database_uri_option(func):
    @click.option("--database-uri", help="System database URI")
    def decorate(*args, database_uri=None, **kwargs):
        if database_uri:
            ProjectSettingsService.config_override["database_uri"] = database_uri

        return func(*args, **kwargs)

    return functools.update_wrapper(decorate, func)


class project:
    __name__ = "project"

    def __init__(self, migrate=False):
        self.migrate = migrate

    def __call__(self, func):
        @database_uri_option
        def decorate(*args, **kwargs):
            ctx = click.globals.get_current_context()

            project = ctx.obj["project"]
            if not project:
                raise CliError(
                    f"`{ctx.command_path}` must be run inside a Meltano project."
                    "\nUse `meltano init <project_name>` to create one."
                    "\nIf you are in a project, you may be in a subfolder. Navigate to the root directory."
                )

            # register the system database connection
            settings_service = ProjectSettingsService(project)
            engine, _ = project_engine(
                project, settings_service.get("database_uri"), default=True
            )

            if self.migrate:
                try:
                    migration_service = MigrationService(engine)
                    migration_service.upgrade(silent=True)
                    migration_service.seed(project)
                except MigrationError as err:
                    raise CliError(str(err)) from err

            func(project, *args, **kwargs)

        return functools.update_wrapper(decorate, func)
