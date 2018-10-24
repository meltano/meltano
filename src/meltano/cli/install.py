import click
from . import cli
from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)

from meltano.support.project_add_service import ProjectAddService


@cli.command()
def install():
    add_service = ProjectAddService()
    install_service = PluginInstallService(None, None, None, add_service)
    click.echo(install_service.install_all_plugins())