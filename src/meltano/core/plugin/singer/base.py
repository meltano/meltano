import json
import os
import logging

from meltano.core.behavior.hookable import hook
from meltano.core.project import Project
from meltano.core.plugin import PluginInstall
from meltano.core.db import project_engine
from meltano.core.utils import nest_object


class SingerPlugin(PluginInstall):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    def process_config(self, flat_config):
        return nest_object(flat_config)

    @hook("before_configure")
    def before_configure(self, invoker, session):
        project = invoker.project
        plugin_dir = project.plugin_dir(self)

        with open(plugin_dir.joinpath(self.config_files["config"]), "w") as config_stub:
            config = invoker.plugin_config_processed
            json.dump(config, config_stub, indent=4)
            logging.debug(f"Created configuration stub at {config_stub}")
