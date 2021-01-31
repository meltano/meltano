import copy
from typing import Iterable, List

import yaml
from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.schedule import Schedule

VERSION = 1


class MeltanoFile(Canonical):
    def __init__(
        self, version: int = VERSION, plugins={}, schedules: list = [], **extras
    ):
        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            version=version,
            extras=extras,
            plugins=self.load_plugins(plugins),
            schedules=self.load_schedules(schedules),
        )

    def load_plugins(self, plugins) -> Canonical:
        """Parse the meltano.yml file and return it as `ProjectPlugin` instances."""
        plugin_type_plugins = Canonical()

        for plugin_type in PluginType:
            plugin_type_plugins[plugin_type] = []

        # this will parse the meltano.yml file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        for plugin_type, raw_plugins in plugins.items():
            for raw_plugin in raw_plugins:
                plugin = ProjectPlugin(PluginType(plugin_type), **raw_plugin)
                plugin_type_plugins[plugin.type].append(plugin)

        return plugin_type_plugins

    def load_schedules(self, schedules) -> List[Schedule]:
        return list(map(Schedule.parse, schedules))
