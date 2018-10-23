import os
import subprocess
from meltano.support.project_add_service import ProjectAddService
from meltano.support.plugin_discovery_service import PluginDiscoveryService


class PluginInstallServicePluginNotFoundError(Exception):
    pass


class PluginInstallService:
    def __init__(self, plugin_type, plugin_name, discovery_service=None):
        self.discovery_service = discovery_service or PluginDiscoveryService()
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self.plugin_url = None
        self.path_to_plugin = None
        self.path_to_pip_install = None

    def get_plugin_url(self):
        discover_json = self.discovery_service.discover_json()
        return discover_json[self.plugin_type].get(self.plugin_name)

    def get_path_to_plugin(self):
        if self.path_to_plugin is None:
            self.path_to_plugin = os.path.join(
                "./", ".meltano", "venvs", self.plugin_type, self.plugin_name
            )
        return self.path_to_plugin

    def get_path_to_pip_install(self):
        self.get_path_to_plugin()
        self.path_to_pip_install = os.path.join(self.path_to_plugin, "bin", "pip")

    def create_venv(self):
        if self.plugin_url is None:
            self.plugin_url = self.get_plugin_url()

        if self.plugin_url is None:  # still
            raise PluginInstallServicePluginNotFoundError()

        self.get_path_to_plugin()

        os.makedirs(self.path_to_plugin, exist_ok=True)
        run_venv = subprocess.run(
            ["python", "-m", "venv", "--upgrade", self.path_to_plugin],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_venv.stdout, "stderr": run_venv.stderr}

    def install_dbt(self):
        self.get_path_to_pip_install()
        run_pip_install_dbt = subprocess.run(
            [self.path_to_pip_install, "install", "dbt"],
                stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        

        return {"stdout": run_pip_install_dbt.stdout, "stderr": run_pip_install_dbt.stderr}

    def install_plugin(self):
        self.get_path_to_pip_install()
        run_pip_install = subprocess.run(
            [self.path_to_pip_install, "install", self.plugin_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_pip_install.stdout, "stderr": run_pip_install.stderr}
