import yaml
import copy
from datetime import datetime, date


from typing import Iterable, List
from meltano.core.plugin import PluginInstall
from meltano.core.plugin.factory import plugin_factory
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior import NameEq


VERSION = 1


class Schedule(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
        extractor: str = None,
        loader: str = None,
        transform: str = None,
        interval: str = None,
        start_date: datetime = None,
        env={},
    ):
        super().__init__()

        self.name = name
        self.extractor = extractor
        self.loader = loader
        self.transform = transform
        self.interval = interval
        self.start_date = start_date
        self.env = env


class MeltanoFile(Canonical):
    def __init__(self, **attrs):
        super().__init__(
            version=int(attrs.pop("version", VERSION)),
            plugins=self.load_plugins(attrs.pop("plugins", {})),
            schedules=self.load_schedules(attrs.pop("schedules", [])),
            send_anonymous_usage_stats=attrs.pop("send_anonymous_usage_stats", None),
            project_id=attrs.pop("project_id", None),
            **attrs
        )

    def load_plugins(self, plugins) -> Canonical:
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

    def load_schedules(self, schedules) -> List[Schedule]:
        return list(map(Schedule.parse, schedules))
