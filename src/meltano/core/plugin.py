import os
from enum import Enum


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"
    SECRET_DIR = os.path.join("./", ".meltano")
    VENV_DIR = os.path.join(SECRET_DIR, "venvs")
    EXTRACTORS_DIR = os.path.join(VENV_DIR, EXTRACTORS)
    LOADERS_DIR = os.path.join(VENV_DIR, LOADERS)

    def __str__(self):
        return self.value
