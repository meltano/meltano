import os
import subprocess
import click

from . import cli
from .params import project
from meltano.core.project import Project, ProjectNotFound
from meltano.core.projects import Projects
from meltano.api.app import start
from meltano.core.tracking import GoogleAnalyticsTracker


@cli.command()
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
    default=False,
    help="To reload the server or not on file changes",
)
@click.option(
    "--hostname",
    default="0.0.0.0",
    help="The hostname (or IP address) to bind on",
    envvar="MELTANO_API_HOSTNAME",
)
def ui(debug, port, reload, hostname):
    project = False
    try:
        project = Project.find()
    except ProjectNotFound as e:
        project = False

    if project:
        click.secho(
            "We found a Meltano project here. Start meltano ui in the directory where your meltano projects exist or will exist.",
            fg="red",
        )
        raise click.Abort()

    projects = Projects()
    # todo: run gunicorn if not in debug mode
    start(projects, debug=debug, use_reloader=reload, port=port, host=hostname)
