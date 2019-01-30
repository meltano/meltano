import os
import subprocess
import click

from . import cli
from meltano.api.app import start
from meltano.core.project import Project


@cli.command()
@click.option("--debug/--no-debug", default=True, help="Run webserver in debug mode")
@click.option("--port", default=5000, help="Port to run webserver on")
@click.option(
    "--reload/--no-reload",
    default=True,
    help="To reload the server or not on file changes",
)
@click.option("--hostname", default="0.0.0.0", help="The hostname of the webserver")
def ui(debug, port, reload, hostname):
    project = Project.find()

    # todo: run gunicorn if not in debug mode
    start(project,
          debug=debug,
          use_reloader=reload,
          port=port,
          host=hostname,
          app_config={"ENV": "development"})
