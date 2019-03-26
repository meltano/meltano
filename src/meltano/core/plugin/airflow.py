import configparser
from . import Plugin, PluginType

from meltano.core.behavior.hookable import HookObject, hook
# from meltano.core.config_service import ConfigService
from meltano.core.venv_service import VenvService
from meltano.core.plugin_invoker import PluginInvoker


class Airflow(HookObject, Plugin):
    __plugin_type__ = PluginType.ORCHESTRATORS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @hook("after_install")
    def after_install(self, *args):
        config_service = ConfigService(project)

    @hook("after_install")
    def initdb(self, project, *args):
        invoker = PluginInvoker(project, self)
        handle = invoker.invoke("initdb")

    @hook("after_configure")
    def after_init(self, *args):
        # open the configuration and update it

        airflow_cfg = configparser.ConfigParser()
        # airflow_cfg.read_file()
