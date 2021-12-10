import copy
from typing import Dict, Iterable, List

import yaml
from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.environment import Environment
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.schedule import Schedule

VERSION = 1


class MeltanoFile(Canonical):
    def __init__(
        self,
        version: int = VERSION,
        plugins: Dict[str, dict] = None,
        schedules: List[dict] = None,
        environments: List[dict] = None,
        **extras,
    ):
        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            version=version,
            extras=extras,
            plugins=self.load_plugins(plugins or {}),
            schedules=self.load_schedules(schedules or []),
            environments=self.load_environments(environments or []),
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

    @staticmethod
    def load_environments(environments: Iterable[dict]) -> List[Environment]:
        """Parse `Environment` objects from python objects.

        Args:
            environments: Sequence of environment dictionaries.

        Returns:
            A list of `Environment` objects.
        """
        return [Environment.parse(obj) for obj in environments]
