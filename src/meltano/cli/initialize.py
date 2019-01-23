import os
import yaml
import click
from urllib.parse import urlparse

from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.tracking import GoogleAnalyticsTracker
from . import cli

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"


@cli.command()
@click.argument("project_name")
def init(project_name):
    init_service = ProjectInitService(project_name)
    try:
        project = init_service.init()
        init_service.echo_instructions()

        tracker = GoogleAnalyticsTracker()
        tracker.track_meltano_init(project_name=project_name)
    except ProjectInitServiceError as e:
        print(e)
        click.secho(f"Directory {project_name} already exists!", fg="red")
        raise click.Abort()
