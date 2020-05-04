import configparser
import shutil
import logging
import subprocess
import time
import os
from . import PluginInstall, PluginType

from meltano.core.behavior.hookable import hook


class GitlabCiScheduler(PluginInstall):
    __plugin_type__ = PluginType.ORCHESTRATORS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
