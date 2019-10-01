import os
import subprocess
import click

from . import cli
from .params import project
from meltano.api.app import start
from meltano.core.db import project_engine
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
@click.option(
    "--bind-port",
    default=5000,
    help="Port to run webserver on",
    envvar="MELTANO_API_PORT",
    type=int,
)
@click.option(
    "--bind",
    default="0.0.0.0",
    help="The hostname (or IP address) to bind on",
    envvar="MELTANO_API_HOSTNAME",
)
@project
def ui(project, bind_port, bind):
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_ui()

    engine, _ = project_engine(project)
    database_uri = str(engine.url)

    # todo: run gunicorn if not in debug mode
    start(
        project,
        port=bind_port,
        host=bind,
        app_config={"SQLALCHEMY_DATABASE_URI": database_uri},
    )
