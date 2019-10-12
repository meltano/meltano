import json
import logging

from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
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

    def load_schema(self, session):
        invoker = invoker_factory(
            self.project, self.extractor, prepare_with_session=session
        )

        # ensure we already have the discovery run at least once
        if not invoker.files["catalog"].exists():
            logging.info("Catalog not found, trying to run the tap with --discover.")
            self.extractor.run_discovery(invoker)

        # update the catalog accordingly
        self.extractor.apply_select(invoker)

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

        with self.project.meltano_update() as meltano:
            self.extractor.add_select_filter(pattern)

            idx = next(
                i
                for i, it in enumerate(self.config.get_extractors())
                if it == self.extractor
            )
            meltano["plugins"]["extractors"][idx] = self.extractor.canonical()
