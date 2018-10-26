import os
from enum import Enum
from meltano.core.project import Project


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"
    EXTRACTORS_DIR = Project.find().meltano_dir(EXTRACTORS)
    LOADERS_DIR = Project.find().meltano_dir(LOADERS)

    def __str__(self):
        return self.value
