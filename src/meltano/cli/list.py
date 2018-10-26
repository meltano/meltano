import click
from . import cli
from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginDiscoveryService


def all_command():
    discovery_service = PluginDiscoveryService()
    click.secho("Extractors", fg="green")
    click.echo("\n".join(discovery_service.list(PluginType.EXTRACTORS)))
    click.secho("Loaders", fg="green")
    click.echo("\n".join(discovery_service.list(PluginType.LOADERS)))


@cli.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    if ctx.invoked_subcommand is None:
        all_command()


@list.command()
def extractors():
    discovery_service = PluginDiscoveryService()
    click.echo("\n".join(discovery_service.list(PluginType.EXTRACTORS)))


@list.command()
def loaders():
    discovery_service = PluginDiscoveryService()
    click.echo("\n".join(discovery_service.list(PluginType.LOADERS)))


@list.command()
def all():
    all_command()
