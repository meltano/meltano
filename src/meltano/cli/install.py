import click
from . import cli
from meltano.support.plugin_install_service import (
    PluginInstallService,
    PluginInstallServicePluginNotFoundError,
)

from meltano.support.project_add_service import ProjectAddService

def install_status_update(data):
    if data['status'] == 'running':
        click.secho(f"Installing {data['plugin_type']}: {data['plugin']['name']}", fg="yellow")
    if data['status'] == 'success':
        click.secho(f"{data['plugin_type'].title()}: {data['plugin']['name']} installed successfully", fg="green")

@cli.command()
def install():
    add_service = ProjectAddService()
    install_service = PluginInstallService(None, None, None, add_service)
    install_status = install_service.install_all_plugins(install_status_update)
    num_installed = len(install_status['installed'])
    click.secho(f"{num_installed} plugins installed successfully", fg="green")