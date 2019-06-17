import os
import subprocess
import click

from . import cli
from .params import project, db_options
from meltano.api.app import start
from meltano.core.db import project_engine
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
@click.option("--debug/--no-debug", default=True, help="Run webserver in debug mode")
@click.option(
    "--bind-port",
    default=5000,
    help="Port to run webserver on",
    envvar="MELTANO_API_PORT",
    type=int,
)
@click.option(
    "--reload/--no-reload",
    default=True,
    help="To reload the server or not on file changes",
)
@click.option(
    "--bind",
    default="0.0.0.0",
    help="The hostname (or IP address) to bind on",
    envvar="MELTANO_API_HOSTNAME",
)
@db_options
@project
def ui(project, debug, bind_port, reload, bind, engine_uri):
    project_engine(project, engine_uri, default=True)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_ui()

    # todo: run gunicorn if not in debug mode
    start(project, debug=debug, use_reloader=reload, port=bind_port, host=bind)
