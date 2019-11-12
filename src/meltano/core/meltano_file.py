import yaml
import copy

from typing import Iterable, List
from meltano.core.plugin import PluginInstall
from meltano.core.plugin.factory import plugin_factory
from meltano.core.behavior.canonical import Canonical
# from meltano.core.schedule_service import Schedule


VERSION = 1


class MeltanoFile(Canonical):
    # __slots__ = [
    #     "version",
    #     "plugins",
    #     "schedules"
    #     "send_anonymous_usage_stats",
    #     "project_id",
    # ]

    def __init__(self, **attrs):
        super().__init__(
            version=int(attrs.pop("version", VERSION)),
            plugins=self.load_plugins(attrs.pop("plugins", {})),
            schedules=self.load_schedules(attrs.pop("schedules", [])),
            send_anonymous_usage_stats=attrs.pop("send_anonymous_usage_stats", True),
            **attrs)

    def load_plugins(self, plugins) -> List[PluginInstall]:
        """Parse the meltano.yml file and return it as `PluginInstall` instances."""
        plugin_type_plugins = Canonical()

        # this will parse the meltano.yml file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        for plugin_type, plugin_defs in plugins.items():
            plugin_type_plugins[plugin_type] = []

            for plugin_def in plugin_defs:
                plugin = plugin_factory(plugin_type, plugin_def)
                plugin_type_plugins[plugin_type].append(plugin)

        return plugin_type_plugins

    def load_schedules(self, schedules):
        return list(map(Canonical.parse, schedules))
