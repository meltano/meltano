import os
import functools
import click

from meltano.core.utils import pop_all
from meltano.core.db import DB


def db_options(func):
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
        config = pop_all(("host", "port", "database", "username", "password"), kwargs)
        DB.setup(**config)
        return func(*args, **kwargs)

    return wrapper
