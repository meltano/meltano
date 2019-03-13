import os
import subprocess
import click

from . import cli
from .params import project
from meltano.api.app import start
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
@project
@click.option("--debug/--no-debug", default=True, help="Run webserver in debug mode")
@click.option(
    "--port",
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
    "--hostname",
    default="0.0.0.0",
    help="The hostname (or IP address) to bind on",
    envvar="MELTANO_API_HOSTNAME",
)
def ui(project, debug, port, reload, hostname):
    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_ui()

    # todo: run gunicorn if not in debug mode
    start(project, debug=debug, use_reloader=reload, port=port, host=hostname)
