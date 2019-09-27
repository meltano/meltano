import functools
import urllib
import click
import click.globals
from pathlib import Path

from meltano.core.project import Project
from meltano.core.utils import pop_all
from meltano.core.migration_service import MigrationService
from meltano.core.db import project_engine


def db_options(func):
    @click.option(
        "--database-uri",
        envvar="MELTANO_DATABASE_URI",
        default="sqlite:///.meltano/meltano.db",
        help="System database URI",
    )
    def decorate(*args, **kwargs):
        engine_uri = kwargs.pop("database_uri")

        return func(engine_uri, *args, **kwargs)

    return functools.update_wrapper(decorate, func)


def project(func):
    @db_options
    def decorate(engine_uri, *args, **kwargs):
        ctx = click.globals.get_current_context()

        project = ctx.obj["project"]
        if not project:
            raise click.ClickException(
                f"`{ctx.command_path}` must be run inside a Meltano project."
                "\nUse `meltano init <project_name>` to create one."
            )

        # register the system database connection
        project_engine(project, engine_uri, default=True)

        func(project, *args, **kwargs)

    return functools.update_wrapper(decorate, func)
