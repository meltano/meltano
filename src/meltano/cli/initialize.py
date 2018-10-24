import os
import yaml
import click
from meltano.core.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)
from urllib.parse import urlparse
from . import cli

EXTRACTORS = "extractors"
LOADERS = "loaders"
ALL = "all"


@cli.command()
@click.argument("project_name")
def init(project_name):
    init_service = ProjectInitService(project_name)
    try:
        init_service.init()
        init_service.echo_instructions()
    except ProjectInitServiceError as e:
        print(e)
        click.secho(f"Directory {init_service.project} already exists!", fg="red")
        raise click.Abort()
