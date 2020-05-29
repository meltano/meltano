import configparser
import shutil
import logging
import subprocess
import time
import os
import sys
from . import PluginInstall, PluginType

from meltano.core.error import SubprocessError
from meltano.core.behavior.hookable import hook
from meltano.core.plugin.config_service import PluginConfigService
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import invoker_factory, PluginInvoker
from meltano.core.db import project_engine
from meltano.core.venv_service import VenvService
from meltano.core.utils import nest, map_dict


class AirflowInvoker(PluginInvoker):
    def env(self):
        env = super().env()
        venv_dir = self.project.venvs_dir(self.plugin.type, self.plugin.name)

        # add the Airflow virtualenv because it contains `gunicorn`
        env["PATH"] = os.pathsep.join([str(venv_dir.joinpath("bin")), env["PATH"]])
        env["VIRTUAL_ENV"] = str(venv_dir)
        env["AIRFLOW_HOME"] = str(self.config_service.run_dir)

        # we want Airflow to inherit our current venv so that the `meltano`
        # module can be used from inside `orchestrate/dags/meltano.py`
        sys_paths = []
        for path in sys.path:
            # the current venv if any
            if path.endswith("site-packages"):
                sys_paths.append(path)

            # when meltano is installed as editable
            if path.endswith(os.path.join("meltano", "src")):
                sys_paths.append(path)

        if "PYTHONPATH" in env and env["PYTHONPATH"]:
            sys_paths.append(env["PYTHONPATH"])

        env["PYTHONPATH"] = os.pathsep.join(sys_paths)

        return env


class Airflow(PluginInstall):
    __plugin_type__ = PluginType.ORCHESTRATORS
    __invoker_cls__ = AirflowInvoker

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    @property
    def config_files(self):
        return {"config": "airflow.cfg"}

    @hook("before_install")
    def setup_env(self, project, args=[]):
        # to make airflow installables without GPL dependency
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    @hook("before_configure")
    def before_configure(self, invoker, session):
        project = invoker.project

        stub_path = project.plugin_dir(self).joinpath("airflow.cfg")

        # generate the default `airflow.cfg`
        handle = invoker.invoke(
            "--help",
            require_preparation=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        handle.wait()

        airflow_cfg_path = invoker.files["config"]
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

        config = {}
        for key, value in invoker.plugin_config.items():
            nest(config, key, str(value))

        for section, cfg in config.items():
            airflow_cfg[section].update(cfg)
            logging.debug(f"\tUpdated section [{section}] with {cfg}")

        with airflow_cfg_path.open("w") as cfg:
            airflow_cfg.write(cfg)
            logging.debug(f"Saved '{str(airflow_cfg_path)}'")

        # we've changed the configuration here, so we need to call
        # prepare again on the invoker so it re-reads the configuration
        # for the Airflow plugin
        invoker.prepare(session)
        handle = invoker.invoke(
            "initdb",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        initdb = handle.wait()

        if initdb:
            raise SubprocessError("airflow initdb failed", handle)

        logging.debug(f"Completed `airflow initdb`")
