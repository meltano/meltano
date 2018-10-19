import os, json
import click

class PluginDiscoveryService:
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __init__(self):
        self.discovery_file = os.path.join(os.path.dirname(__file__), "discovery.json")
        self.discovery_data = None

    def discover(self, plugin_type):
        with open(self.discovery_file) as f:
            self.discovery_data = json.load(f)

        if plugin_type == PluginDiscoveryService.ALL:
            self.list_discovery(PluginDiscoveryService.EXTRACTORS)
            self.list_discovery(PluginDiscoveryService.LOADERS)
        else:
            self.list_discovery(plugin_type)


    def list_discovery(self, discovery):
        click.echo(click.style(discovery.title(), fg="green"))
        click.echo("\n".join(self.discovery_data.get(discovery).keys()))