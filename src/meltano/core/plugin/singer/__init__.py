from typing import Dict
from meltano.core.plugin import PluginType

from .catalog import visit, SelectExecutor, ListExecutor
from .base import SingerPlugin
from .tap import SingerTap
from .target import SingerTarget
