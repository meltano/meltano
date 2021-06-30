from pathlib import Path

import meltano.core.bundle as bundle
import yaml

from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):
    def __init__(self, discovery=False):
        super().__init__(None, None)
        self._discovery = discovery

    def file_contents(self, project):
        initialize_file = bundle.find("initialize.yml")
        file_contents = {
            Path(relative_path): content
            for relative_path, content in yaml.safe_load(initialize_file.open()).items()
        }
        if self._discovery:
            file_contents["discovery.yml"] = bundle.find("discovery.yml").read_text()
        return file_contents

    def update_config(self, project):
        return {}
