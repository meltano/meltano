import configparser
import logging
import os
import subprocess
from distutils.version import StrictVersion

from meltano.core.behavior.hookable import hook
from meltano.core.error import AsyncSubprocessError
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

    @staticmethod
    def update_config_file(invoker: AirflowInvoker) -> None:
        """Update airflow.cfg with plugin configuration."""
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

    @hook("before_install")
    async def setup_env(self, *args, **kwargs):
        """Configure the env to make airflow installable without GPL deps."""
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    @hook("before_configure")
    async def before_configure(self, invoker: AirflowInvoker, session):  # noqa: WPS217
        """Keep the Airflow metadata database up-to-date."""
        # generate the default `airflow.cfg`
        handle = await invoker.invoke_async(
            "--help",
            require_preparation=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        return_code = await handle.wait()

        if return_code:
            raise AsyncSubprocessError(
                "Command `airflow --help` failed", process=handle
            )

        # Read and update airflow.cfg
        self.update_config_file(invoker)

        # we've changed the configuration here, so we need to call
        # prepare again on the invoker so it re-reads the configuration
        # for the Airflow plugin
        await invoker.prepare(session)

        # make sure we use correct db init
        handle = await invoker.invoke_async(
            "version",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await handle.communicate()

        if handle.returncode:
            raise AsyncSubprocessError(
                "Command `airflow version` failed", process=handle
            )

        version = stdout.decode()
        init_db_cmd = (
            ["initdb"]
            if StrictVersion(version) < StrictVersion("2.0.0")
            else ["db", "init"]
        )

        handle = await invoker.invoke_async(
            *init_db_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        initdb = await handle.wait()

        if initdb:
            raise AsyncSubprocessError(
                "Airflow metadata database could not be initialized: `airflow initdb` failed",
                handle,
            )

        logging.debug("Completed `airflow initdb`")

    @hook("before_cleanup")
    async def before_cleanup(self, invoker: PluginInvoker):
        """Delete the config file."""
        config_file = invoker.files["config"]
        try:
            config_file.unlink()
        except FileNotFoundError:
            pass
        logging.debug(f"Deleted configuration at {config_file}")
