import os
import yaml
from meltano.core.plugin_discovery_service import PluginDiscoveryService


class ConfigService:
    def __init__(self):
        self.meltano_yml_file = self.meltano_yml_file = os.path.join(
            "./", "meltano.yml"
        )
        self.meltano_yml = yaml.load(open(self.meltano_yml_file)) or {}
        self.meltano_secret_dir = os.path.join("./", ".meltano")

    def make_meltano_secret_dir(self):
        if not os.path.isdir(self.meltano_secret_dir):
            os.mkdir(os.path.join("./", ".meltano"))

    def get_extractors(self):
        return self.meltano_yml.get(PluginDiscoveryService.EXTRACTORS)

    def get_loaders(self):
        return self.meltano_yml.get(PluginDiscoveryService.LOADERS)

    def get_database(self, database_name):
        return yaml.load(
            open(os.path.join("./", ".meltano", f".database_{database_name}.yml"))
        )
