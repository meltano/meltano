from typing import Dict
from meltano.core.plugin import PluginType

from .catalog import SelectExecutor, ListExecutor
from .base import *
from .tap import SingerTap
from .target import SingerTarget
