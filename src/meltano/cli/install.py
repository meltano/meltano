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
from meltano.core.plugin import PluginType
from meltano.core.project import Project, ProjectNotFound
from meltano.core.project_add_service import ProjectAddService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.db import project_engine


def install_status_update(data):
    plugin = data["plugin"]

    if data["status"] == "running":
        click.echo()
        click.secho(f"Installing {plugin.type.descriptor} '{plugin.name}'...")
    elif data["status"] == "error":
        click.secho(data["message"], fg="red")
        click.secho(data["details"], err=True)
    elif data["status"] == "warning":
        click.secho(f"Warning! {data['message']}.", fg="yellow")
    elif data["status"] == "success":
        click.secho(f"Installed {plugin.type.descriptor} '{plugin.name}'", fg="green")


def install_plugins(project, plugins, **kwargs):
    install_service = PluginInstallService(project)
    install_status = install_service.install_plugins(
        plugins, status_cb=install_status_update, **kwargs
    )
    num_installed = len(install_status["installed"])
    num_failed = len(install_status["errors"])

    fg = "green"
    if num_failed >= 0 and num_installed == 0:
        fg = "red"
    elif num_failed > 0 and num_installed > 0:
        fg = "yellow"

    if len(plugins) > 1:
        click.echo()
        click.secho(
            f"Installed {num_installed}/{num_installed+num_failed} plugins", fg=fg
        )

    return num_failed == 0


@cli.command()
@click.argument(
    "plugin_type", type=click.Choice([*list(PluginType), "all"]), default="all"
)
@click.option("--include-related", is_flag=True)
@project(migrate=True)
def install(project, plugin_type, include_related):
    """
    Installs all the dependencies of your project based on the meltano.yml file.
    Read more at https://www.meltano.com/docs/command-line-interface.html.
    """
    config_service = ConfigService(project)

    if plugin_type == "all":
        plugins = list(config_service.plugins())
    else:
        plugins = config_service.get_plugins_of_type(PluginType(plugin_type))

    if include_related:
        discovery_service = PluginDiscoveryService(project)
        add_service = ProjectAddService(
            project,
            config_service=config_service,
            plugin_discovery_service=discovery_service,
        )

        for plugin_install in plugins:
            try:
                plugin_def = discovery_service.find_plugin(
                    plugin_install.type, plugin_install.name
                )
            except PluginNotFoundError:
                continue

            related_plugins = add_service.add_related(plugin_def)
            for plugin in related_plugins:
                click.secho(
                    f"Added {plugin.type.descriptor} '{plugin.name}' to your Meltano project because it is related to {plugin_def.type.descriptor} '{plugin_def.name}'.",
                    fg="green",
                )

            plugins.extend(related_plugins)

    click.echo(f"Installing {len(plugins)} plugins...")

    success = install_plugins(project, plugins)

    tracker = GoogleAnalyticsTracker(project)
    tracker.track_meltano_install()

    if not success:
        raise click.Abort()
