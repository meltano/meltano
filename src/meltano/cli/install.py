import click
from . import cli
from .params import project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.config_service import ConfigService
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_add_service import ProjectAddService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine


def install_status_update(data):
    plugin = data["plugin"]

    if data["status"] == "error":
        click.secho(data["message"], fg="red")
        click.secho(data["details"], err=True)
    if data["status"] == "warning":
        click.secho(f"Warning! {data['message']}.", fg="yellow")
    if data["status"] == "success":
        click.secho(f"Installed '{plugin.name}'.", fg="green")


@cli.command()
@click.option("--include-related", is_flag=True)
@project(migrate=True)
def install(project, include_related):
    """
    Installs all the dependencies of your project based on the meltano.yml file.
    Read more at https://www.meltano.com/docs/command-line-interface.html#command-line-interface.
    """
    if include_related:
        config_service = ConfigService(project)
        discovery_service = PluginDiscoveryService(project)
        add_service = ProjectAddService(
            project,
            config_service=config_service,
            plugin_discovery_service=discovery_service,
        )

        installed_plugins = config_service.plugins()
        for plugin_install in installed_plugins:
            try:
                plugin_def = discovery_service.find_plugin(
                    plugin_install.type, plugin_install.name
                )
            except PluginNotFoundError:
                continue

            related_plugins = add_service.add_related(plugin_def)
            for plugin in related_plugins:
                click.secho(
                    f"Added '{plugin.name}' to your Meltano project because it is related to '{plugin_def.name}'.",
                    fg="green",
                )

    install_service = PluginInstallService(project)
    install_status = install_service.install_all_plugins(
        status_cb=install_status_update
    )
    num_installed = len(install_status["installed"])
    num_failed = len(install_status["errors"])

    fg = "green"
    if num_failed >= 0 and num_installed == 0:
        fg = "red"
    elif num_failed > 0 and num_installed > 0:
        fg = "yellow"

    click.secho(f"{num_installed}/{num_installed+num_failed} plugins installed.", fg=fg)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_install()
