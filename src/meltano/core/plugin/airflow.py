import configparser
import shutil
import logging
from . import Plugin, PluginType

from meltano.core.behavior.hookable import HookObject, hook
from meltano.core.plugin.config_service import PluginConfigService
from meltano.core.venv_service import VenvService
from meltano.core.plugin_invoker import PluginInvoker


class Airflow(HookObject, Plugin):
    __plugin_type__ = PluginType.ORCHESTRATORS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @property
    def config_files(self):
        return {
            "config": "airflow.cfg"
        }

    @hook("before_prepare")
    def set_run_dir(self, invoker, *args):
        invoker.config_service.run_dir = invoker.project.root_dir("orchestrate")

    @hook("after_install")
    def after_install(self, project, *args):
        plugin_config_service = PluginConfigService(project, self, run_dir=project.root_dir("orchestrate"))

        # create the database directory
        project.run_dir(self.name)

        invoker = PluginInvoker(project, self,
                                config_service=plugin_config_service)

        airflow_cfg_path = plugin_config_service.run_dir.joinpath("airflow.cfg")
        stub_path = plugin_config_service.config_dir.joinpath("airflow.cfg")
        handle = invoker.invoke("--help",
                                prepare=False)

        logging.debug(f"Generated default '{str(airflow_cfg_path)}'")

        # move it to the config dir
        shutil.move(airflow_cfg_path, stub_path)
        airflow_cfg_path = stub_path
        logging.debug(f"Moved to '{str(stub_path)}'")

        # open the configuration and update it
        # now we let's update the config to use our stubs
        airflow_cfg = configparser.ConfigParser()

        with airflow_cfg_path.open() as cfg:
            airflow_cfg.read_file(cfg)
        logging.debug(f"Loaded '{str(airflow_cfg_path)}'")

        for section, cfg in self.config.items():
            airflow_cfg[section].update(cfg)
            logging.debug(f"\tUpdated section [{section}]")

        with airflow_cfg_path.open("w") as cfg:
            airflow_cfg.write(cfg)
        logging.debug(f"Saved '{str(airflow_cfg_path)}'")

        # initdb
        handle = invoker.invoke("initdb")
        logging.debug(f"Completed `airflow initdb`")
