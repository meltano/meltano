from typing import Dict

from . import PluginType
from .singer import SingerTap, SingerTarget
from .dbt import DbtPlugin, DbtTransformPlugin
from .model import ModelPlugin
from .airflow import Airflow as AirflowPlugin


def plugin_factory(plugin_type: PluginType, plugin_def: Dict):
    plugin_class = {
        PluginType.EXTRACTORS: SingerTap,
        PluginType.LOADERS: SingerTarget,
        PluginType.TRANSFORMERS: DbtPlugin,
        PluginType.TRANSFORMS: DbtTransformPlugin,
        PluginType.MODELS: ModelPlugin,
        PluginType.ORCHESTRATORS: AirflowPlugin,
    }

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    return plugin_class[plugin_type](**plugin_def)
