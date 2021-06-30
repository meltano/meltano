from typing import Dict

from meltano.core.plugin import PluginType

from .base import *
from .catalog import ListExecutor, SelectExecutor
from .tap import SingerTap
from .target import SingerTarget
