import functools
import urllib
import click
import click.globals
import os
from pathlib import Path

from meltano.core.project import Project
from meltano.core.utils import pop_all
from meltano.core.migration_service import MigrationService
from meltano.core.db import project_engine


def db_options(func):
    @click.option(
        "--database-uri",
        envvar="MELTANO_DATABASE_URI",
        default=lambda: f"sqlite:///{os.getcwd()}/.meltano/meltano.db",
        help="System database URI",
    )
    def decorate(*args, **kwargs):
        engine_uri = kwargs.pop("database_uri")

        return func(engine_uri, *args, **kwargs)

    return functools.update_wrapper(decorate, func)


class project:
    __name__ = "project"

    def __init__(self, migrate=False):
        self.migrate = migrate

    def __call__(self, func):
        @db_options
        def decorate(engine_uri, *args, **kwargs):
            ctx = click.globals.get_current_context()

            project = ctx.obj["project"]
            if not project:
                raise click.ClickException(
                    f"`{ctx.command_path}` must be run inside a Meltano project."
                    "\nUse `meltano init <project_name>` to create one."
                    "\nIf you are in a project, you may be in a subfolder. Navigate to the root directory."
                )

            # register the system database connection
            engine, _ = project_engine(project, engine_uri, default=True)

            if self.migrate:
                migration_service = MigrationService(engine)
                migration_service.upgrade()
                migration_service.seed(project)

            func(project, *args, **kwargs)

        return functools.update_wrapper(decorate, func)
