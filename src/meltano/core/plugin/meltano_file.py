import yaml
from pathlib import Path

import meltano.core.bundle as bundle
from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):
    def file_contents(self, project):
        initialize_file = bundle.find("initialize.yml")
        return {
            Path(relative_path): content
            for relative_path, content in yaml.safe_load(initialize_file.open()).items()
        }

    def plugin_config(self, project):
        return {}
