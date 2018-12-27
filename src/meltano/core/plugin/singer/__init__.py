from typing import Dict
from meltano.core.plugin import PluginType

from .catalog import visit, SelectExecutor, ListExecutor
from .base import SingerPlugin
from .tap import SingerTap
from .target import SingerTarget


def plugin_factory(plugin_type: PluginType, canonical: Dict):
    plugin_class = {PluginType.EXTRACTORS: SingerTap, PluginType.LOADERS: SingerTarget}

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    return plugin_class[plugin_type](**canonical)
