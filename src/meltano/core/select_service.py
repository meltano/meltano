import json
import logging

from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginLacksCapabilityError
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
        self.config = config_service or ConfigService(project)
        self._extractor = self.config.find_plugin(extractor, PluginType.EXTRACTORS)

    @property
    def extractor(self):
        return self._extractor

    @property
    def current_select(self):
        plugin_settings_service = PluginSettingsService(
            self.project, self.extractor, config_service=self.config
        )
        return plugin_settings_service.get("_select")

    def load_schema(self, session):
        invoker = invoker_factory(
            self.project, self.extractor, prepare_with_session=session
        )

        # ensure we already have the discovery run at least once
        if not invoker.files["catalog"].exists():
            logging.debug("Catalog not found, trying to run the tap with --discover.")
            self.extractor.run_discovery(invoker)

        # update the catalog accordingly
        self.extractor.apply_catalog_rules(invoker)

        # return the updated catalog
        with invoker.files["catalog"].open() as catalog:
            return json.load(catalog)

    def list_all(self, session) -> ListSelectedExecutor:
        list_all = ListSelectedExecutor()

        try:
            schema = self.load_schema(session)
            list_all.visit(schema)
        except FileNotFoundError as e:
            logging.error(
                "Cannot find catalog: make sure the tap runs correctly with --discover; `meltano invoke TAP --discover`"
            )
            raise e

        return list_all

    def select(self, entities_filter, attributes_filter, exclude=False):
        exclude = "!" if exclude else ""
        pattern = f"{exclude}{entities_filter}.{attributes_filter}"
        self.extractor.add_select_filter(pattern)
        self.config.update_plugin(self.extractor)
