from typing import Dict

from meltano.core.behavior.hookable import hook
from meltano.core.connection_service import ConnectionService
from meltano.core.db import project_engine
from . import SingerPlugin, PluginType


class SingerTarget(SingerPlugin):
    __plugin_type__ = PluginType.LOADERS

    def exec_args(self, files: Dict):
        args = ["--config", files["config"]]

        return args

    @property
    def config_files(self):
        return {"config": "target.config.json"}

    @property
    def output_files(self):
        return {"state": "new_state.json"}

    def context_config(self, elt_context):
        """
        Tries to infer the connection from the current ELTContext
        if available
        """
        _, Session = project_engine(elt_context.project)

        try:
            session = Session()
            connection_service = ConnectionService(elt_context)
            load_connection = connection_service.connection(session, "load")

            # it could be worth having a strategy pattern for each
            # plugin type. We could actually inherit this class for each plugin
            # we have in discovery.yml, but I wanted to find a generic approach
            # first.
            if self.name == "target-sqlite":
                return {
                    "database": f"{elt_context.loader_config['database']}_{load_connection['schema']}"
                }
            else:
                return {"schema": load_connection["schema"]}
        finally:
            session.close()
