import configparser
import logging
import os
import subprocess
from distutils.version import StrictVersion

from meltano.core.behavior.hookable import hook
from meltano.core.error import SubprocessError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import nest

from . import BasePlugin, PluginType


class AirflowInvoker(PluginInvoker):
    def env(self):
        env = super().env()

        env["AIRFLOW_HOME"] = str(self.plugin_config_service.run_dir)
        env["AIRFLOW_CONFIG"] = str(self.files["config"])

        return env


class Airflow(BasePlugin):
    __plugin_type__ = PluginType.ORCHESTRATORS

    invoker_class = AirflowInvoker

    @property
    def config_files(self):
        return {"config": "airflow.cfg"}

    def process_config(self, flat_config):
        config = {}
        for key, value in flat_config.items():
            nest(config, key, str(value))
        return config

    @hook("before_install")
    def setup_env(self, *args, **kwargs):
        # to make airflow installables without GPL dependency
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    @hook("before_configure")
    def before_configure(self, invoker, session):
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

        # make sure we use correct db init
        handle = invoker.invoke(
            "version",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        version, err = handle.communicate()

        init_db_cmd = (
            ["initdb"]
            if StrictVersion(version) < StrictVersion("2.0.0")
            else ["db", "init"]
        )

        handle = invoker.invoke(
            *init_db_cmd,
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

        logging.debug("Completed `airflow initdb`")

    @hook("before_cleanup")
    def before_cleanup(self, invoker):
        config_file = invoker.files["config"]
        config_file.unlink()
        logging.debug(f"Deleted configuration at {config_file}")
