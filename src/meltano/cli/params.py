import os
import functools
import click
import urllib

from meltano.core.project import Project
from meltano.core.utils import pop_all


def db_options(func):
    @click.option(
        "-B",
        "--backend",
        envvar="MELTANO_BACKEND",
        default="sqlite",
        type=click.Choice(["sqlite", "postgresql"]),
        help="Database backend for Meltano.",
    )
    @click.option("--path", envvar="SQLITE_DATABASE", default="meltano")
    @click.option(
        "-H",
        "--host",
        envvar="PG_ADDRESS",
        default="localhost",
        help="Database address.",
    )
    @click.option("-p", "--port", type=int, envvar="PG_PORT", default=5432)
    @click.option(
        "-d",
        "-db",
        "database",
        envvar="PG_DATABASE",
        help="Database to import the data to.",
    )
    @click.option(
        "-u",
        "--username",
        envvar="PG_USERNAME",
        default=lambda: os.getenv("USER", ""),
        help="Specifies the user to connect to the database with.",
    )
    @click.password_option(prompt=False, envvar="PG_PASSWORD")
    def wrapper(*args, **kwargs):
        engine_uri = os.getenv("SQL_ENGINE_URI")
        backend = kwargs.pop("backend")

        config = {
            "sqlite": pop_all(("path",), kwargs),
            "postgresql": pop_all(
                ("host", "port", "database", "username", "password"), kwargs
            ),
        }

        if not engine_uri and backend == "sqlite" and config[backend]["path"]:
            engine_uri = "sqlite:///{path}.db".format(**config[backend])

        if not engine_uri and backend == "postgresql":
            pg_config = config[backend]
            pg_config["password"] = urllib.parse.quote(pg_config["password"])
            engine_uri = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
                **pg_config
            )

        return func(*args, **kwargs, engine_uri=engine_uri)

    return functools.update_wrapper(wrapper, func)


def project(func):
    @click.pass_context
    def decorate(ctx, *args, **kwargs):
        project = ctx.obj["project"]
        if not project:
            raise click.ClickException(
                f"`{ctx.command_path}` must be run inside a Meltano project."
                "\nUse `meltano init <project_name>` to create one."
            )

        ctx.invoke(func, project, *args, **kwargs)

    return functools.update_wrapper(decorate, func)
