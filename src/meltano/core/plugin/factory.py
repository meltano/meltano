import importlib
from typing import Union

from . import BasePlugin, PluginDefinition, PluginType, Variant


def lazy_import(module, cls):
    def lazy():
        return getattr(importlib.import_module(module, "meltano.core.plugin"), cls)

    return lazy


base_plugin_classes = {
    PluginType.EXTRACTORS: lazy_import(".singer", "SingerTap"),
    PluginType.LOADERS: lazy_import(".singer", "SingerTarget"),
    PluginType.TRANSFORMS: lazy_import(".dbt", "DbtTransformPlugin"),
    PluginType.MODELS: lazy_import(".model", "ModelPlugin"),
    PluginType.DASHBOARDS: lazy_import(".dashboard", "DashboardPlugin"),
    PluginType.ORCHESTRATORS: lazy_import(".airflow", "Airflow"),
    PluginType.TRANSFORMERS: lazy_import(".dbt", "DbtPlugin"),
    PluginType.FILES: lazy_import(".file", "FilePlugin"),
    PluginType.UTILITIES: lazy_import(".utility", "UtilityPlugin"),
}


def base_plugin_factory(
    plugin_def: PluginDefinition, variant_or_name: Union[str, Variant]
) -> BasePlugin:
    plugin_cls = base_plugin_classes.get(plugin_def.type, lambda: BasePlugin)()
    variant = plugin_def.find_variant(variant_or_name)
    return plugin_cls(plugin_def, variant)
