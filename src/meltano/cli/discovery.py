import os
import json
import click
from urllib.parse import urlparse
from . import cli

EXTRACTORS = 'extractors';
LOADERS = 'loaders'
ALL = 'all'

discovery_file = os.path.join(os.path.dirname(__file__), "cli/discovery.json")

@cli.command()
@click.argument('plugin_type', type=click.Choice([EXTRACTORS, LOADERS, ALL]))
def discover(plugin_type):
    with open(discovery_file) as f:
        data = json.load(f)

        if plugin_type == ALL:
            list_discovery(EXTRACTORS, data)
            list_discovery(LOADERS, data)
        else:
            list_discovery(plugin_type, data)

def list_discovery(discovery, data):
    click.echo(click.style(discovery.title(), fg='green'))
    click.echo('\n'.join(data.get(discovery).keys()))
