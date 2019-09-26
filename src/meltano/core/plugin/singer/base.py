import json
import os
import logging

from meltano.core.behavior.hookable import hook
from meltano.core.project import Project
from meltano.core.plugin import PluginInstall
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.db import project_engine


class SingerPlugin(PluginInstall):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("before_configure")
    def install_config_stub(self, invoker):
        project = invoker.project
        plugin_dir = project.plugin_dir(self)

        with open(plugin_dir.joinpath(self.config_files["config"]), "w") as config_stub:
            json.dump(invoker.plugin_config, config_stub)
            logging.debug(f"Created configuration stub at {config_stub}")
