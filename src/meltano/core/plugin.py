from enum import Enum


class PluginType(str, Enum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    ALL = "all"

    def __str__(self):
        return self.value
