import click
from meltano.support.plugin_discovery_service import PluginDiscoveryService
from meltano.support.project_add_service import ProjectAddService
from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)
from . import cli


@cli.command()
@click.argument(
    "plugin_type",
    type=click.Choice([ProjectAddService.EXTRACTOR, ProjectAddService.LOADER]),
)
@click.argument("plugin_name")
def install(plugin_type, plugin_name):
    install_service = PluginInstallService()
    plugin_type = (
        PluginDiscoveryService.EXTRACTORS
        if plugin_type == ProjectAddService.EXTRACTOR
        else PluginDiscoveryService.LOADERS
    )
    try:
        install_service.install(plugin_type, plugin_name)
    except Exception as e:
        raise e
        click.Abort()
