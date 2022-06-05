from typing import Dict

from meltano.core.plugin import PluginType

# from .base import *  # TODO: delete
from .catalog import ListExecutor, SelectExecutor
from .mapper import SingerMapper
from .tap import SingerTap
from .target import BookmarkWriter, SingerTarget

__all__ = [
    "Dict",
    "PluginType",
    "ListExecutor",
    "SelectExecutor",
    "SingerMapper",
    "SingerTap",
    "BookmarkWriter",
    "SingerTarget",
]
