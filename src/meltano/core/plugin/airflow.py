import configparser
import shutil
import logging
import subprocess
import time
import os
from . import Plugin, PluginType

from meltano.core.behavior.hookable import hook
from meltano.core.plugin.config_service import PluginConfigService
from meltano.core.venv_service import VenvService
from meltano.core.plugin_invoker import PluginInvoker


class Airflow(Plugin):
    __plugin_type__ = PluginType.ORCHESTRATORS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @property
    def config_files(self):
        return {"config": "airflow.cfg"}

    def home(self, project):
        return project.run_dir(self.name)

    @hook("before_prepare")
    def set_run_dir(self, invoker, *args):
        home = self.home(invoker.project)
        invoker.env["AIRFLOW_HOME"] = str(invoker.config_service.run_dir)
        logging.debug(f"Set AIRFLOW_HOME={invoker.env['AIRFLOW_HOME']}")

        # inject current PATH so the plugin can run `meltano`
        venv_dir = invoker.project.venvs_dir(self.type, self.name)
        invoker.env["PATH"] = os.pathsep.join(
            [str(venv_dir.joinpath("bin")), os.environ["PATH"]]
        )
        invoker.env["VIRTUAL_ENV"] = str(venv_dir)

    @hook("before_install")
    def setup_env(self, project, *args):
        # to make airflow installable
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"
        os.environ["AIRFLOW_HOME"] = str(self.home(project))

    @hook("after_install")
    def after_install(self, project, *args):
        plugin_config_service = PluginConfigService(project, self)

        invoker = PluginInvoker(project, self, config_service=plugin_config_service)

        airflow_cfg_path = plugin_config_service.run_dir.joinpath("airflow.cfg")
        stub_path = plugin_config_service.config_dir.joinpath("airflow.cfg")
        handle = invoker.invoke(
            "--help", prepare=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        handle.wait()
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
        handle = invoker.invoke(
            "initdb", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        handle.wait()
        logging.debug(f"Completed `airflow initdb`")
