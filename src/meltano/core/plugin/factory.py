"""Factory for creating plugins."""
from __future__ import annotations

import importlib

from . import BasePlugin, PluginDefinition, PluginType, Variant


def lazy_import(module: str, classname: str):
    """Lazily import a class.

    Args:
        module: the module to import from
        classname: the class to import

    Returns:
        Function for lazily importing the given class.
    """

    def lazy():
        return getattr(
            importlib.import_module(module, "meltano.core.plugin"), classname
        )

    return lazy


base_plugin_classes = {  # noqa: WPS317
    PluginType.EXTRACTORS: lazy_import(".singer", "SingerTap"),
    PluginType.LOADERS: lazy_import(".singer", "SingerTarget"),
    PluginType.TRANSFORMS: lazy_import(".dbt", "DbtTransformPlugin"),
    (PluginType.ORCHESTRATORS, "airflow"): lazy_import(".airflow", "Airflow"),
    PluginType.TRANSFORMERS: lazy_import(".dbt", "DbtPlugin"),
    PluginType.FILES: lazy_import(".file", "FilePlugin"),
    PluginType.UTILITIES: lazy_import(".utility", "UtilityPlugin"),
    (PluginType.UTILITIES, "superset"): lazy_import(".superset", "Superset"),
    PluginType.MAPPERS: lazy_import(".singer", "SingerMapper"),
}


def base_plugin_factory(
    plugin_def: PluginDefinition, variant_or_name: str | Variant
) -> BasePlugin:
    """Return a plugin based on the given PluginDefinition and variant.

    Args:
        plugin_def: the PluginDefinition of the plugin to create.
        variant_or_name: the variant or name of the plugin to create.

    Returns:
        The created plugin.
    """
    plugin_cls = base_plugin_classes.get(  # noqa: WPS317
        (plugin_def.type, plugin_def.name),
        base_plugin_classes.get(plugin_def.type, lambda: BasePlugin),
    )()
    variant = plugin_def.find_variant(variant_or_name)
    return plugin_cls(plugin_def, variant)
