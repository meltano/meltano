import logging
import subprocess
from typing import List

import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition

from . import BasePlugin, PluginType

logger = structlog.getLogger(__name__)


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

    EXTRA_SETTINGS = [SettingDefinition(name="_config_path")]

    @property
    def config_files(self):
        return {"config": "superset_config.py"}

    @hook("before_configure")
    async def before_configure(self, invoker: SupersetInvoker, session):  # noqa: WPS217
        """Write plugin configuration to superset_config.py."""

        config = invoker.plugin_config_processed

        config_script_lines = [
            "import sys",
            "module = sys.modules[__name__]",
            f"config = {str(config)}",
            "for key, value in config.items():",
            "    if key.isupper():",
            "        setattr(module, key, value)",
        ]

        custom_config_filename = invoker.plugin_config_extras["_config_path"]
        if custom_config_filename:
            custom_config_path = invoker.project.root.joinpath(custom_config_filename)

            if custom_config_path.exists():
                config_script_lines.extend(
                    [
                        "import imp",
                        f'custom_config = imp.load_source("superset_config", "{str(custom_config_path)}")',
                        "for key in dir(custom_config):",
                        "    if key.isupper():",
                        "        setattr(module, key, getattr(custom_config, key))",
                    ]
                )

                logger.info(f"Merged in config from {custom_config_path}")
            else:
                raise PluginExecutionError(
                    f"Could not find config file {custom_config_path}"
                )

        config_path = invoker.files["config"]
        with open(config_path, "w") as config_file:
            config_file.write("\n".join(config_script_lines))
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
