import os
import re
from typing import Any, Dict

import meltano.core.bundle as bundle
from ruamel.yaml import YAML


class PluginDiscoveryGenerator:
    def __init__(self):
        self._yaml = YAML()

        self._discovery_version = 19
        self._header_comment = [
            "# Increment this version number whenever the schema of discovery.yml is changed.\n",
            "# See https://www.meltano.com/docs/contributor-guide.html#discovery-yml-version for more information.\n",
        ]

    def generate_discovery(
        self,
        plugin_definitions_dir=str(bundle.find("discovery_definitions")) + "/",
        discovery_file_path=str(bundle.find("")) + "/discovery.yml",
    ):
        discovery_dict: Dict[str, Any] = {}
        discovery_dict["version"] = self._discovery_version

        for root, _, files in os.walk(plugin_definitions_dir):
            meltano_type = re.sub(plugin_definitions_dir, "", root)
            if meltano_type == "":
                continue
            meltano_array = []

            for file in files:
                with open(os.path.join(root, file), "r") as plugin_file:
                    plugin_data = self._yaml.load(plugin_file)

                meltano_array.append(plugin_data)

            discovery_dict[meltano_type] = meltano_array

        with open(discovery_file_path, "w") as outfile:
            outfile.writelines(self._header_comment)
            self._yaml.dump(discovery_dict, outfile)


if __name__ == "__main__":
    obj = PluginDiscoveryGenerator()
    obj.generate_discovery()
