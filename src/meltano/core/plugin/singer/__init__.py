from typing import Dict

from meltano.core.plugin import PluginType

from .base import SingerPlugin
from .catalog import ListExecutor, SelectExecutor
from .mapper import SingerMapper
from .tap import SingerTap
from .target import BookmarkWriter, SingerTarget

__all__ = [
    "BookmarkWriter",
    "Dict",
    "ListExecutor",
    "PluginType",
    "SelectExecutor",
    "SingerMapper",
    "SingerPlugin",
    "SingerTap",
    "SingerTarget",
]
