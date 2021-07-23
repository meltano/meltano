from typing import Dict, List, Optional

import yaml
from meltano.core.meltano_file import MeltanoFile
from meltano.core.multiple_config import load

# TODO:
#   [ ] appropriate name for trio: schedules, plugins.extractors, plugins.loaders
#   [ ] use trio name to rename plugin_states(), update_plugin(), add_plugins()
#   [ ] move same_name() and contains_plugin() to multiple_config.py if they can be used there
#   ALLOW-LIST
#   1.  write to multiple Meltano files for Plugins.Extractors, Plugins.Loaders, Schedules
#   2.  duplicate plugins/schedules throw build error (this means record is not needed)


def same_name(plugin1: dict, plugin2: dict) -> bool:
    return plugin1["name"] == plugin2["name"]


def contains_plugin(plugins: List[dict], plugin: dict) -> Optional[dict]:
    """
    p from plugins if plugin in plugins else None
    """
    for p in plugins:
        if same_name(plugin, p):
            return p
    return None


class MultipleMeltanoFile(MeltanoFile):
    def plugin_states(self, reference, result, plugin_type):
        update = (
            self[plugin_type]
            if plugin_type == "schedules"
            else self["plugins"][plugin_type]
        )
        reference = (
            reference[plugin_type]
            if plugin_type == "schedules"
            else reference["plugins"][plugin_type]
        )
        result = (
            result[plugin_type]
            if plugin_type == "schedules"
            else result["plugins"][plugin_type]
        )
        return update, reference, result

    def update_plugin(self, reference, result, plugin_type):
        update, reference, result = self.plugin_states(reference, result, plugin_type)
        for plugin in reference:
            plugin_update = contains_plugin(update, plugin)
            if plugin_update:
                result.append(plugin_update)
            # items not in update are not included in result

    def add_plugin(
        self, reference, result, plugin_type
    ):  # only called if result/reference is primary config
        update, reference, result = self.plugin_states(reference, result, plugin_type)
        for plugin in update:  # items in update but not in reference belong in result
            if not contains_plugin(reference, plugin):
                result.append(plugin)

    def dump(self, path, is_primary=False):
        """
        Order: Version, Extras, Plugins, Schedules (per src/meltano/core/meltanofile.py)
        """
        # Create config to be written back to system (out)
        config_out = {}

        # Get config dict from filesystem (system)
        config_system = load(path)

        #   Version
        config_out["version"] = self["version"]

        #   Extras
        for extra in self["extras"]:
            config_out[extra] = self["extras"][extra]

        #   Plugins and Schedules
        config_out["plugins"]: Dict[Dict[List]] = {"extractors": [], "loaders": []}
        config_out["schedules"] = []
        for plugin in ["extractors", "loaders", "schedules"]:
            self.update_plugin(config_system, config_out, plugin)
            if is_primary:  # New schedules go to meltano.yml
                self.add_plugin(config_system, config_out, plugin)

        # Write config out to path
        yaml.dump(config_out, path, default_flow_style=False, sort_keys=False)
