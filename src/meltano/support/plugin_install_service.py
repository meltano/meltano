import os
import subprocess
import click
from meltano.support.project_add_service import ProjectAddService
from meltano.support.plugin_discovery_service import PluginDiscoveryService


class PluginInstallServicePluginNotFoundError(Exception):
    pass


class PluginInstallService:
    def __init__(self):
        pass
        self.discovery_service = PluginDiscoveryService()

    def install(self, plugin_type, plugin_name):
        discover_json = self.discovery_service.discover_json()
        plugin_url = discover_json[plugin_type].get(plugin_name)
        if plugin_url is None:
            click.secho(f"{plugin_type.title()} {plugin_name} not supported", fg="red")
            raise PluginInstallServicePluginNotFoundError()

        path_to_plugin = os.path.join(
            "./", "meltano", "venvs", plugin_type, plugin_name
        )
        os.makedirs(path_to_plugin, exist_ok=True)
        run_venv = subprocess.run(
            ["python", "-m", "venv", f"./.meltano/venvs/{plugin_type}/{plugin_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        click.echo(run_venv.stdout)
        click.secho(run_venv.stderr, fg="red")

        click.echo(f"getting from {plugin_url}")
        path_to_plugin = os.path.join(
            "./", "meltano", "venvs", plugin_type, plugin_name
        )
        path_to_pip_install = os.path.join(
            ".meltano", "venvs", plugin_type, plugin_name, "bin", "pip"
        )

        run_pip_install = subprocess.run(
            [path_to_pip_install, "install", plugin_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        click.echo(run_pip_install.stdout)
        click.secho(run_pip_install.stderr, fg="red")
