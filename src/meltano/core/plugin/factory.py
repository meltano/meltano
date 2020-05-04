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
        PluginType.ORCHESTRATORS: {
            "airflow": lazy_import(".airflow", "Airflow"),
            "gitlab-ci-scheduler": lazy_import(
                ".gitlab_ci_scheduler", "GitlabCiScheduler"
            ),
        },
        PluginType.TRANSFORMERS: {"dbt": lazy_import(".dbt", "DbtPlugin")},
    }

    name = plugin_def.pop("name")

    # this will parse the discovery file and create an instance of the
    # corresponding `plugin_class` for all the plugins.
    plugin_cls_factory = plugin_class[plugin_type]

    if isinstance(plugin_cls_factory, dict):
        plugin_cls_factory = plugin_cls_factory[name]

    plugin_cls = plugin_cls_factory()

    return plugin_cls(name, **plugin_def)
