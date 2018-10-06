import os
import json
import click
from urllib.parse import urljoin
from . import cli

EXTRACTORS = 'extractors';
LOADERS = 'loaders'
ALL = 'all'

discovery_file = urljoin(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),'cli/discovery.json')

@cli.command()
@click.argument('what', type=click.Choice([EXTRACTORS, LOADERS, ALL]))
def discover(what):
    with open(discovery_file) as f:
        data = json.load(f)

        if what == ALL:
            list_discovery(EXTRACTORS, data)
            list_discovery(LOADERS, data)
        else:
            list_discovery(what, data)

def list_discovery(discovery, data):
    click.echo(click.style(discovery.title(), fg='green'))
    click.echo('\n'.join(data.get(discovery).keys()))