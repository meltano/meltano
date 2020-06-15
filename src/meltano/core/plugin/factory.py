from typing import Dict
import importlib

from . import PluginType


def plugin_factory(plugin_type: PluginType, plugin_def: Dict):
    def lazy_import(module, cls):
        def lazy():
            return getattr(importlib.import_module(module, "meltano.core.plugin"), cls)

        return lazy

    plugin_class = {
        PluginType.EXTRACTORS: lazy_import(".singer", "SingerTap"),
        PluginType.LOADERS: lazy_import(".singer", "SingerTarget"),
        PluginType.TRANSFORMS: lazy_import(".dbt", "DbtTransformPlugin"),
        PluginType.MODELS: lazy_import(".model", "ModelPlugin"),
        PluginType.DASHBOARDS: lazy_import(".dashboard", "DashboardPlugin"),
        PluginType.ORCHESTRATORS: lazy_import(".airflow", "Airflow"),
        PluginType.TRANSFORMERS: lazy_import(".dbt", "DbtPlugin"),
        PluginType.FILES: lazy_import(".file", "FilePlugin"),
    }

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    plugin_cls = plugin_class[plugin_type]()

    return plugin_cls(plugin_def.pop("name"), **plugin_def)
