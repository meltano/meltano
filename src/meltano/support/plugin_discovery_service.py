import os, json


class PluginDiscoveryInvalidJSONError(Exception):
    invalid_message = "Invalid JSON data in discovery.json"
    pass


class PluginDiscoveryService:
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __init__(self):
        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
        self.discovery_data = None

    def discover_json(self):
        with open(self.discovery_file) as f:
            try:
                discovery_json = json.load(f)
                return discovery_json
            except Exception as e:
                raise PluginDiscoveryInvalidJSONError()

    def discover(self, plugin_type):
        with open(self.discovery_file) as f:
            try:
                self.discovery_data = json.load(f)
            except Exception as e:
                raise PluginDiscoveryInvalidJSONError()

        if plugin_type == PluginDiscoveryService.ALL:
            return {PluginDiscoveryService.EXTRACTORS: self.list_discovery(PluginDiscoveryService.EXTRACTORS),
            PluginDiscoveryService.LOADERS: self.list_discovery(PluginDiscoveryService.LOADERS)}
        else:
            return {plugin_type: self.list_discovery(plugin_type)}

    def list_discovery(self, discovery):
        return "\n".join(self.discovery_data.get(discovery).keys())
