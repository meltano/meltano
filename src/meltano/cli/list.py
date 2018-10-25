import click
from . import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginDiscoveryService

@cli.group()
def list():
    pass

@list.command()
def extractors():
    discovery_service = PluginDiscoveryService()
    click.echo("\n".join(discovery_service.list(PluginType.EXTRACTORS)))

@list.command()
def loaders():
    discovery_service = PluginDiscoveryService()
    click.echo("\n".join(discovery_service.list(PluginType.LOADERS)))