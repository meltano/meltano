import yaml

import meltano.core.bundle as bundle
from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):
    def file_contents(self, project):
        initialize_file = bundle.find("initialize.yml")
        return yaml.safe_load(open(initialize_file))

    def plugin_config(self, project):
        return {}
