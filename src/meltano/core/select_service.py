import json

from .project import Project
from meltano.core.config_service import ConfigService
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer.catalog import visit, ListSelectedExecutor


class SelectService:
    def __init__(self, project: Project):
        self.project = project

    def select(self, project, extractor, entities_filter, attributes_filter):
        config = ConfigService(project)
        extractor = config.get_plugin(PluginType.EXTRACTORS, extractor)
        invoker = PluginInvoker(project, extractor)

        list_all = ListSelectedExecutor()
        try:
            if not invoker.files["catalog"].exists():
                logging.info(
                    "Catalog not found, trying to run the tap with --discover."
                )
                extractor.run_discovery(invoker)
            else:
                extractor.apply_select(invoker)

            with invoker.files["catalog"].open() as catalog:
                schema = json.load(catalog)
                visit(schema, list_all)
        except FileNotFoundError as e:
            logging.error(
                "Cannot find catalog: make sure the tap runs correctly with --discover; `meltano invoke TAP --discover`"
            )
            raise e

        return (extractor, list_all)
