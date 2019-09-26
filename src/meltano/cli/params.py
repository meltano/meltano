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
        "-B",
        "--backend",
        envvar="MELTANO_BACKEND",
        default="sqlite",
        type=click.Choice(["sqlite", "postgresql"]),
        help="System database backend",
    )
    @click.option(
        "--path",
        envvar="SQLITE_DATABASE",
        default="meltano",
        help="With database backend 'sqlite': system database path",
    )
    @click.option(
        "-H",
        "--host",
        envvar="PG_ADDRESS",
        default="localhost",
        help="With database backend 'postgresql': system database address",
    )
    @click.option(
        "-p",
        "--port",
        type=int,
        envvar="PG_PORT",
        default=5432,
        help="With database backend 'postgresql': system database port",
    )
    @click.option(
        "-d",
        "-db",
        "database",
        envvar="PG_DATABASE",
        help="With database backend 'postgresql': system database name",
    )
    @click.option(
        "-u",
        "--username",
        envvar="PG_USERNAME",
        default=lambda: os.getenv("USER", ""),
        help="With database backend 'postgresql': system database user",
    )
    @click.password_option(
        prompt=False,
        envvar="PG_PASSWORD",
        help="With database backend 'postgresql': system database password",
    )
    @click.option(
        "--database-uri",
        envvar="MELTANO_DATABASE_URI",
        help="System database URI (takes priority over other database options if set)",
    )
    def decorate(*args, **kwargs):
        engine_uri = kwargs.pop("database_uri")
        backend = kwargs.pop("backend")

        config = {
            "sqlite": pop_all(("path",), kwargs),
            "postgresql": pop_all(
                ("host", "port", "database", "username", "password"), kwargs
            ),
        }

        if not engine_uri and backend == "sqlite" and config[backend]["path"]:
            path = Path(config[backend]["path"]).with_suffix(".db")
            engine_uri = f"sqlite:///{path}"

        if not engine_uri and backend == "postgresql":
            pg_config = config[backend]
            pg_config["password"] = urllib.parse.quote(pg_config["password"])
            engine_uri = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
                **pg_config
            )

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
