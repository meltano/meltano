import os
import subprocess
import click

from . import cli
from meltano.api import app


@cli.command()
@click.option("--debug/--no-debug", default=True, help="Run webserver in debug mode")
@click.option("--port", default=5001, help="Port to run webserver on")
@click.option(
    "--reload/--no-reload",
    default=True,
    help="To reload the server or not on file changes",
)
@click.option("--hostname", default="localhost", help="The hostname of the webserver")
def www(debug, port, reload, hostname):
    # todo: run gunicorn if not in debug mode
    if debug:
        app.run(debug=debug, use_reloader=reload, port=port, host=hostname)
    else:
        pass
