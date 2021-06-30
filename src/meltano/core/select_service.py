import json
import logging

from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project_plugins_service import ProjectPluginsService

from .db import project_engine
from .project import Project


class SelectService:
    def __init__(
        self,
        project: Project,
        extractor: str,
        plugins_service: ProjectPluginsService = None,
    ):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self._extractor = self.plugins_service.find_plugin(
            extractor, PluginType.EXTRACTORS
        )

    @property
    def extractor(self):
        return self._extractor

    @property
    def current_select(self):
        plugin_settings_service = PluginSettingsService(
            self.project, self.extractor, plugins_service=self.plugins_service
        )
        return plugin_settings_service.get("_select")

    def load_catalog(self, session):
        invoker = invoker_factory(
            self.project, self.extractor, plugins_service=self.plugins_service
        )

        with invoker.prepared(session):
            catalog_json = invoker.dump("catalog")

        return json.loads(catalog_json)

    def list_all(self, session) -> ListSelectedExecutor:
        try:
            catalog = self.load_catalog(session)
        except FileNotFoundError as err:
            raise PluginExecutionError(
                f"Could not find catalog. Verify that the tap supports discovery mode and advertises the `discover` capability as well as either `catalog` or `properties`"
            ) from err

        list_all = ListSelectedExecutor()
        list_all.visit(catalog)

        return list_all

    def select(self, entities_filter, attributes_filter, exclude=False):
        exclude = "!" if exclude else ""
        pattern = f"{exclude}{entities_filter}.{attributes_filter}"

        plugin = self.extractor

        select = plugin.extras.get("select", [])
        select.append(pattern)
        plugin.extras["select"] = select

        self.plugins_service.update_plugin(plugin)
