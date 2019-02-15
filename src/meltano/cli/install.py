import click
from . import cli
from .params import project
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_add_service import ProjectAddService
from meltano.core.tracking import GoogleAnalyticsTracker


def install_status_update(data):
    plugin = data["plugin"]

    if data["status"] == "running":
        click.secho(f"Installing {plugin.type}: {plugin.name}", fg="yellow")
    if data["status"] == "error":
        click.secho(f"An error occured: {data['message']}.", fg="red")
    if data["status"] == "warning":
        click.secho(f"Warning! {data['message']}.", fg="yellow")
    if data["status"] == "success":
        click.secho(
            f"{plugin.type.title()}: {plugin.name} installed successfully", fg="green"
        )


@cli.command()
@project
def install(project):
    install_service = PluginInstallService(project)
    install_status = install_service.install_all_plugins(install_status_update)
    num_installed = len(install_status["installed"])
    click.secho(f"{num_installed} plugins installed successfully", fg="green")

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_install()
