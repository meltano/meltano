import logging
import subprocess
from typing import List

from meltano.core.behavior.hookable import hook
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin_invoker import PluginInvoker

from . import BasePlugin, PluginType


class SupersetInvoker(PluginInvoker):
    def env(self):
        env = super().env()

        env["SUPERSET_HOME"] = str(self.plugin_config_service.run_dir)
        env["SUPERSET_CONFIG_PATH"] = str(self.files["config"])
        env["FLASK_APP"] = "superset"

        return env


class Superset(BasePlugin):
    __plugin_type__ = PluginType.UTILITIES

    invoker_class = SupersetInvoker

    @property
    def config_files(self):
        return {"config": "superset_config.py"}

    def process_config(self, flat_config):
        # TODO: This means that `meltano config superset` doesn't show settings that are handled by Meltano itself, e.g. `ui.port` in the `ui` command
        return {key: value for key, value in flat_config.items() if key.isupper()}

    @hook("before_configure")
    async def before_configure(self, invoker: SupersetInvoker, session):  # noqa: WPS217
        """Write plugin configuration to superset_config.py."""
        config_path = invoker.files["config"]
        with open(config_path, "w") as config_file:
            config = invoker.plugin_config_processed
            config_file.write(
                "\n".join(
                    [
                        "import sys",
                        "module = sys.modules[__name__]",
                        f"config = {str(config)}",
                        "for key, value in config.items():",
                        "    setattr(module, key, value)",
                    ]
                )
            )
        logging.debug(f"Created configuration at {config_file}")

    @hook("before_invoke")
    async def db_upgrade_hook(self, invoker: PluginInvoker, exec_args: List[str]):
        """Create or upgrade metadata database."""
        handle = await invoker.invoke_async(
            "db",
            "upgrade",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                "Superset metadata database could not be initialized: `superset db upgrade` failed",
                handle,
            )

        logging.debug("Completed `superset db upgrade`")

    @hook("before_invoke")
    async def init_hook(self, invoker: PluginInvoker, exec_args: List[str]):
        """Create default roles and permissions."""

        handle = await invoker.invoke_async(
            "init",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                "Superset default roles and permissions could not be created: `superset init` failed",
                handle,
            )

        logging.debug("Completed `superset init`")

    @hook("before_cleanup")
    async def before_cleanup(self, invoker: PluginInvoker):
        """Delete the config file."""
        config_file = invoker.files["config"]
        try:
            config_file.unlink()
            logging.debug(f"Deleted configuration at {config_file}")
        except FileNotFoundError:
            pass
