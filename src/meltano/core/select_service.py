import json
import logging

from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from .project import Project
from .db import project_engine


class SelectService:
    def __init__(
        self, project: Project, extractor: str, config_service: ConfigService = None
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self._extractor = self.config_service.find_plugin(
            extractor, PluginType.EXTRACTORS
        )

    @property
    def extractor(self):
        return self._extractor

    @property
    def current_select(self):
        plugin_settings_service = PluginSettingsService(
            self.project, self.extractor, config_service=self.config_service
        )
        return plugin_settings_service.get("_select")

    def load_catalog(self, session):
        invoker = invoker_factory(self.project, self.extractor)

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
        self.extractor.add_select_filter(pattern)
        self.config_service.update_plugin(self.extractor)
