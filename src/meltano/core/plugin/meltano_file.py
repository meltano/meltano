from __future__ import annotations

from pathlib import Path

import yaml

from meltano.core import bundle

from .file import FilePlugin


class MeltanoFilePlugin(FilePlugin):
    def __init__(self, discovery: bool = False):
        super().__init__(None, None)
        self._discovery = discovery

    def file_contents(self, project):
        initialize_file = bundle.root / "initialize.yml"
        file_contents = {
            Path(relative_path): content
            for relative_path, content in yaml.safe_load(initialize_file.open()).items()
        }
        if self._discovery:
            file_contents["discovery.yml"] = (bundle.root / "discovery.yml").read_text()
        return file_contents

    def update_config(self, project):
        return {}
