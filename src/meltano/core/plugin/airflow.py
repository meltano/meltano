"""Plugin glue code for Airflow."""

from __future__ import annotations

import configparser
import os
import subprocess
import typing as t
from contextlib import suppress

import structlog
from packaging.version import Version

from meltano.core.behavior.hookable import hook
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.utils import nest

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = structlog.stdlib.get_logger(__name__)


class AirflowInvoker(PluginInvoker):
    """Invoker that prepares env for Airflow."""

    def env(self) -> dict[str, str]:
        """Environment variables for Airflow.

        Returns:
            Dictionary of environment variables.
        """
        env = super().env()

        env["AIRFLOW_HOME"] = str(self.plugin_config_service.run_dir)
        env["AIRFLOW_CONFIG"] = str(self.files["config"])

        return env


class Airflow(BasePlugin):
    """Plugin glue code for Airflow."""

    __plugin_type__ = PluginType.ORCHESTRATORS

    invoker_class = AirflowInvoker

    @property
    def config_files(self) -> dict[str, str]:
        """Return the configuration files required by the plugin.

        Returns:
            Dictionary of config file identifiers and filenames
        """
        return {"config": "airflow.cfg"}

    def process_config(self, flat_config: dict[str, str]) -> dict[str, dict[str, str]]:
        """Unflatten the config.

        Args:
            flat_config: the flat config

        Returns:
            unflattened config
        """
        config: dict[str, dict[str, str]] = {}
        for key, value in flat_config.items():
            nest(config, key, str(value))
        return config

    @staticmethod
    def update_config_file(invoker: AirflowInvoker) -> None:
        """Update airflow.cfg with plugin configuration.

        Args:
            invoker: the active PluginInvoker
        """
        airflow_cfg_path = invoker.files["config"]
        logger.debug(f"Generated default '{airflow_cfg_path!s}'")  # noqa: G004

        # open the configuration and update it
        # now we let's update the config to use our stubs
        airflow_cfg = configparser.ConfigParser()

        with airflow_cfg_path.open() as airflow_cfg_file_to_read:
            airflow_cfg.read_file(airflow_cfg_file_to_read)
            logger.debug(f"Loaded '{airflow_cfg_path!s}'")  # noqa: G004

        config = invoker.plugin_config_processed
        for section, section_config in config.items():
            airflow_cfg[section].update(section_config)
            logger.debug(f"\tUpdated section [{section}] with {section_config}")  # noqa: G004

        with airflow_cfg_path.open("w") as airflow_cfg_file_to_write:
            airflow_cfg.write(airflow_cfg_file_to_write)
            logger.debug(f"Saved '{airflow_cfg_path!s}'")  # noqa: G004

    @hook("before_install")
    async def setup_env(self, *args: t.Any, **kwargs: t.Any) -> None:  # noqa: ARG002
        """Configure the env to make airflow installable without GPL deps.

        Args:
            args: Arbitrary args
            kwargs: Arbitrary kwargs
        """
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    @hook("before_configure")
    async def before_configure(self, invoker: AirflowInvoker, session: Session) -> None:
        """Generate config file and keep metadata database up-to-date.

        Args:
            invoker: the active PluginInvoker
            session: metadata database session

        Raises:
            AsyncSubprocessError: if command failed to run
        """
        # generate the default `airflow.cfg`
        handle = await invoker.invoke_async(
            "--help",
            require_preparation=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                "Command `airflow --help` failed",  # noqa: EM101
                process=handle,
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
                "Command `airflow version` failed",  # noqa: EM101
                process=handle,
            )

        version = stdout.decode()
        init_db_cmd = (
            ["initdb"] if Version(version) < Version("2.0.0") else ["db", "init"]
        )

        handle = await invoker.invoke_async(
            *init_db_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                (
                    "Airflow metadata database could not be initialized: "  # noqa: EM101
                    "`airflow initdb` failed"
                ),
                handle,
            )

        logger.debug("Completed `airflow initdb`")

    @hook("before_cleanup")
    async def before_cleanup(self, invoker: PluginInvoker) -> None:
        """Delete the config file.

        Args:
            invoker: the active PluginInvoker
        """
        config_file = invoker.files["config"]
        with suppress(FileNotFoundError):
            config_file.unlink()
            logger.debug(f"Deleted configuration at {config_file}")  # noqa: G004
