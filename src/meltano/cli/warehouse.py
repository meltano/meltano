import click
from meltano.support.project_init_service import (
    ProjectInitService,
    ProjectInitServiceError,
)
from . import cli


@cli.command()
def warehouse(project_name):
    pass
