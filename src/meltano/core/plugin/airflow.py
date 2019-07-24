import configparser
import shutil
import logging
import subprocess
import time
import os
from . import PluginInstall, PluginType

from meltano.core.behavior.hookable import hook
from meltano.core.plugin.config_service import PluginConfigService
from meltano.core.plugin_invoker import invoker_factory, PluginInvoker
from meltano.core.db import project_engine
from meltano.core.venv_service import VenvService
from meltano.core.utils import nest, map_dict


class Airflow(PluginInstall):
    __plugin_type__ = PluginType.ORCHESTRATORS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    def invoker(self, session, project, *args, **kwargs):
        return AirflowInvoker(session, project, self, *args, **kwargs)

    @property
    def config_files(self):
        return {"config": "airflow.cfg"}

    @hook("before_install")
    def setup_env(self, project, args=[]):
        # to make airflow installables without GPL dependency
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"
        os.environ["AIRFLOW_HOME"] = str(project.run_dir(self.name))

    @hook("after_install")
    def after_install(self, project, args=[]):
        _, Session = project_engine(project)
        session = Session()

        plugin_config_service = PluginConfigService(project, self)
        invoker = invoker_factory(
            session, project, self, config_service=plugin_config_service
        )

        try:
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

            for section, cfg in invoker.plugin_settings.as_config(self).items():
                airflow_cfg[section].update(map_dict(str, cfg))
                logging.debug(f"\tUpdated section [{section}] with {cfg}")

            with airflow_cfg_path.open("w") as cfg:
                airflow_cfg.write(cfg)
            logging.debug(f"Saved '{str(airflow_cfg_path)}'")

            # initdb
            handle = invoker.invoke(
                "initdb", stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            handle.wait()
            logging.debug(f"Completed `airflow initdb`")
        finally:
            session.close()


class AirflowInvoker(PluginInvoker):
    def Popen_options(self):
        env = os.environ.copy()
        venv_dir = self.project.venvs_dir(self.plugin.type, self.plugin.name)
        env["PATH"] = os.pathsep.join([str(venv_dir.joinpath("bin")), env["PATH"]])
        env["VIRTUAL_ENV"] = str(venv_dir)
        env["AIRFLOW_HOME"] = str(self.config_service.run_dir)

        options = super().Popen_options()
        options_env = nest(options, "env")
        options_env.update(env)

        return options
