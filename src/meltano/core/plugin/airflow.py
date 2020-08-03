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
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import nest


class AirflowInvoker(PluginInvoker):
    def env(self):
        env = super().env()

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

    def process_config(self, flat_config):
        config = {}
        for key, value in flat_config.items():
            nest(config, key, str(value))
        return config

    @hook("before_install")
    def setup_env(self, project, reason):
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

        config = invoker.plugin_config_processed
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
            raise SubprocessError(
                "Airflow metadata database could not be initialized: `airflow initdb` failed",
                handle,
            )

        logging.debug(f"Completed `airflow initdb`")
