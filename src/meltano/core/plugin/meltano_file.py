import yaml
from pathlib import Path

import meltano.core.bundle as bundle
from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):
    def __init__(self, *args, discovery=False, **kwargs):
        self.discovery = discovery
        super().__init__(*args, **kwargs)

    def file_contents(self, project):
        initialize_file = bundle.find("initialize.yml")
        file_contents = {
            Path(relative_path): content
            for relative_path, content in yaml.safe_load(initialize_file.open()).items()
        }
        if self.discovery:
            file_contents["discovery.yml"] = bundle.find("discovery.yml").read_text()
        return file_contents

    def update_config(self, project):
        return {}
