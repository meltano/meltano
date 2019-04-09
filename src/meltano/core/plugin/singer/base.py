import json
import os
from meltano.core.behavior.hookable import hook
from meltano.core.project import Project
from meltano.core.plugin import Plugin


class SingerPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("before_install")
    def install_config_stub(self, project):
        plugin_dir = project.plugin_dir(self)
        os.makedirs(plugin_dir, exist_ok=True)

        # TODO: refactor as explicit stubs
        with open(plugin_dir.joinpath(self.config_files["config"]), "w") as config:
            json.dump(self.config, config)
