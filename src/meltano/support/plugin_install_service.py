import os
import yaml
import subprocess
from meltano.support.project_add_service import ProjectAddService
from meltano.support.plugin_discovery_service import PluginDiscoveryService


class PluginInstallServicePluginNotFoundError(Exception):
    pass


class PluginInstallService:
    def __init__(self, plugin_type=None, plugin_name=None, discovery_service=None, add_service=None):
        self.discovery_service = discovery_service or PluginDiscoveryService()
        self.add_service = add_service or ProjectAddService()
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self.plugin_url = None
        self.path_to_plugin = None
        self.path_to_pip_install = None

    def get_plugin_url(self):
        discover_json = self.discovery_service.discover_json()
        return discover_json[self.plugin_type].get(self.plugin_name)

    def get_path_to_plugin(self):
        self.path_to_plugin = os.path.join(
            "./", ".meltano", "venvs", self.plugin_type, self.plugin_name
        )
        return self.path_to_plugin

    def get_path_to_pip_install(self):
        self.get_path_to_plugin()
        self.path_to_pip_install = os.path.join(self.path_to_plugin, "bin", "pip")

    def create_venv(self):
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

        return {
            "stdout": run_pip_install_dbt.stdout,
            "stderr": run_pip_install_dbt.stderr,
        }

    def install_all_plugins(self, status_cb):
        config_yml = self.add_service.meltano_yml
        approved_keys = [PluginDiscoveryService.EXTRACTORS, PluginDiscoveryService.LOADERS]
        errors = []
        installed = []
        for key, value in config_yml.items():
            if key in approved_keys:
                for plugin in value:
                    status_cb({'plugin_type': key, 'plugin': plugin, 'status': 'running'})
                    self.plugin_name = plugin.get('name')
                    self.plugin_url = plugin.get('url')
                    self.plugin_type = key
                    if self.plugin_url is None:
                        errors.append({'plugin_type': key, 'plugin': plugin, 'reason': 'Missing URL'})
                        continue
                    self.create_venv()
                    self.install_dbt()
                    self.install_plugin()
                    installed.append({'plugin_type': key, 'plugin': plugin, 'status': 'success'})
                    status_cb({'plugin_type': key, 'plugin': plugin, 'status': 'success'})
        
        return {'errors': errors, 'installed': installed}

    def install_plugin(self):
        self.get_path_to_pip_install()
        run_pip_install = subprocess.run(
            [self.path_to_pip_install, "install", self.plugin_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return {"stdout": run_pip_install.stdout, "stderr": run_pip_install.stderr}
