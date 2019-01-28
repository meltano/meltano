import os
import functools
import click
import urllib

from meltano.core.project import Project
from meltano.core.utils import pop_all
from meltano.core.db import project_register_engine
from sqlalchemy import create_engine


def db_options(func):
    @click.option(
        "-B",
        "--backend",
        envvar="MELTANO_BACKEND",
        default="sqlite",
        type=click.Choice(["sqlite", "postgresql"]),
        help="Database backend for Meltano.",
    )
    @click.option("--path", default="meltano.db")
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
    @click.password_option(envvar="PG_PASSWORD")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        project = Project.find()
        engine_uri = None
        backend = kwargs.pop("backend")

        config = {
            "sqlite": pop_all(("path",), kwargs),
            "postgresql": pop_all(
                ("host", "port", "database", "username", "password"), kwargs
            ),
        }

        if backend == "sqlite":
            engine_uri = "sqlite:///{path}".format(**config[backend])
        elif backend == "postgresql":
            pg_config = config[backend]
            pg_config["password"] = urllib.parse.quote(pg_config["password"])
            engine_uri = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
                **pg_config
            )
        else:
            raise Exception(f"Invalid backend: {backend} is not supported.")

        engine = create_engine(engine_uri)
        project_register_engine(project, engine)

        return func(*args, **kwargs)

    return wrapper
