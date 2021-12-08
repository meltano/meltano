"""PluginDiscoveryGenerator for compiling discovery.yml dynamically."""
import os
from typing import Any, Dict

from meltano.core import bundle
from ruamel.yaml import YAML


class PluginDiscoveryGenerator:
    """This class generates and writes out the discovery.yml file."""

    def __init__(self):
        """Init PluginDiscoveryGenerator with yaml and discovery extras."""
        self._yaml = YAML()

        self._discovery_version = 19
        self._header_comment = [
            "# Increment this version number whenever the schema of discovery.yml is changed.\n",
            "# See https://www.meltano.com/docs/contributor-guide.html#discovery-yml-version for more information.\n",
        ]

    def generate_discovery(
        self,
        plugin_definitions_dir=None,
        discovery_file_path=None,
    ):
        """Generate the discovery.yml and write it out to a file."""
        if not plugin_definitions_dir:
            definition_path = str(bundle.find("discovery_definitions"))
            plugin_definitions_dir = f"{definition_path}/"
        if not discovery_file_path:
            discovery_file_path = str(bundle.find("discovery.yml"))
        discovery_dict: Dict[str, Any] = {}
        discovery_dict["version"] = self._discovery_version

        for plugin_type_path, _, files in os.walk(plugin_definitions_dir):
            if plugin_type_path == plugin_definitions_dir:
                continue
            plugin_type = os.path.basename(plugin_type_path)
            plugin_type_definitions = self._get_plugin_type_definitions(
                files, plugin_type_path
            )
            discovery_dict[plugin_type] = plugin_type_definitions
        self._write_discovery(discovery_file_path, discovery_dict)

    def _get_plugin_type_definitions(self, files, root_path):
        plugin_type_definitions = []

        for file in files:
            with open(os.path.join(root_path, file), "r") as plugin_file:
                plugin_definition = self._yaml.load(plugin_file)

            plugin_type_definitions.append(plugin_definition)
        return plugin_type_definitions

    def _write_discovery(self, discovery_file_path, discovery_dict):
        with open(discovery_file_path, "w") as outfile:
            outfile.writelines(self._header_comment)
            self._yaml.dump(discovery_dict, outfile)


if __name__ == "__main__":
    obj = PluginDiscoveryGenerator()
    obj.generate_discovery()
