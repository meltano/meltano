import json
import logging

from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.plugin.singer.catalog import ListSelectedExecutor
from .project import Project
from .db import project_engine


class SelectService:
    def __init__(self, project: Project, extractor: str):
        self.project = project
        self.config = ConfigService(project)
        self.extractor = self.config.find_plugin(extractor, PluginType.EXTRACTORS)

    def get_extractor(self):
        return self.extractor

    def load_schema(self):
        _, Session = project_engine(self.project)
        session = Session()
        invoker = invoker_factory(session, self.project, self.extractor)

        try:
            if not invoker.files["catalog"].exists():
                logging.info(
                    "Catalog not found, trying to run the tap with --discover."
                )
                self.extractor.run_discovery(invoker)

            self.extractor.apply_select(invoker)
            with invoker.files["catalog"].open() as catalog:
                return json.load(catalog)
        finally:
            session.close()

    def get_extractor_entities(self):
        list_all = ListSelectedExecutor()

        try:
            schema = self.load_schema()
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
