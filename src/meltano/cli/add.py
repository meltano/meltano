import os
import yaml
import json
import click
from urllib.parse import urlparse
from . import cli
from ..support.project_add_service import ProjectAddService, ProjectMissingYMLFileException


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice([ProjectAddService.EXTRACTOR, ProjectAddService.LOADER]),
)
@click.argument("plugin_name")
def add(plugin_type, plugin_name):
    try:
        add_service = ProjectAddService(plugin_type, plugin_name)
        add_service.add()
    except ProjectMissingYMLFileException as e:
        click.Abort()
    
