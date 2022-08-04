from __future__ import annotations

from meltano.core.plugin import PluginType

from .base import BasePlugin, SingerPlugin
from .catalog import ListExecutor, SelectExecutor
from .mapper import SingerMapper
from .tap import SingerTap
from .target import BookmarkWriter, SingerTarget
