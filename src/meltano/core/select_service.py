import json
import logging

from .project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import visit, ListSelectedExecutor


class SelectService:
    def __init__(self, project: Project, extractor: str):
        self.project = project
        self.config = ConfigService(project)
        self.extractor = self.config.get_plugin(extractor, PluginType.EXTRACTORS)

    def get_extractor(self):
        return self.extractor

    def get_extractor_entities(self):
        invoker = PluginInvoker(self.project, self.extractor)

        list_all = ListSelectedExecutor()
        try:
            if not invoker.files["catalog"].exists():
                logging.info(
                    "Catalog not found, trying to run the tap with --discover."
                )
                self.extractor.run_discovery(invoker)
            else:
                self.extractor.apply_select(invoker)

            with invoker.files["catalog"].open() as catalog:
                schema = json.load(catalog)
                visit(schema, list_all)
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
