import functools
import os
import urllib
from pathlib import Path

import click
import click.globals
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import pop_all

from .utils import CliError


def database_uri_option(func):
    @click.option("--database-uri", help="System database URI")
    def decorate(*args, database_uri=None, **kwargs):
        if database_uri:
            ProjectSettingsService.config_override["database_uri"] = database_uri

        return func(*args, **kwargs)

    return functools.update_wrapper(decorate, func)


class pass_project:  # noqa: N801
    """Pass current project to decorated CLI command function."""

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
                )

            # register the system database connection
            engine, _ = project_engine(project, default=True)

            if self.migrate:
                migration_service = MigrationService(engine)
                migration_service.upgrade(silent=True)
                migration_service.seed(project)

            func(project, *args, **kwargs)

        return functools.update_wrapper(decorate, func)
