from typing import Dict
import importlib

from . import PluginType, ProjectPlugin


def plugin_factory(plugin_type: PluginType, raw_plugin: Dict) -> ProjectPlugin:
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

    plugin_cls = plugin_class[plugin_type]()

    return plugin_cls(raw_plugin.pop("name"), **raw_plugin)
