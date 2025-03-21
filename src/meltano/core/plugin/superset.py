"""Plugin glue code for Superset."""

from __future__ import annotations

import subprocess
import typing as t
from contextlib import suppress

import anyio
import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.error import AsyncSubprocessError
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition

from . import BasePlugin, PluginType

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = structlog.getLogger(__name__)


class SupersetInvoker(PluginInvoker):
    """Invoker that prepares env for Superset."""

    def env(self) -> dict[str, str]:
        """Environment variables for Superset.

        Returns:
            Dictionary of environment variables.
        """
        env = super().env()

        env["SUPERSET_HOME"] = str(self.plugin_config_service.run_dir)
        env["SUPERSET_CONFIG_PATH"] = str(self.files["config"])
        env["FLASK_APP"] = "superset"

        return env


class Superset(BasePlugin):
    """Plugin glue code for Superset."""

    __plugin_type__ = PluginType.UTILITIES

    invoker_class = SupersetInvoker

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = [
        SettingDefinition(name="_config_path"),
    ]

    @property
    def config_files(self) -> dict[str, str]:
        """Return the configuration files required by the plugin.

        Returns:
            Dictionary of config file identifiers and filenames
        """
        return {"config": "superset_config.py"}

    @hook("before_configure")
    async def before_configure(
        self,
        invoker: SupersetInvoker,
        session: Session,  # noqa: ARG002
    ) -> None:
        """Write plugin configuration to superset_config.py.

        Args:
            invoker: the active PluginInvoker
            session: metadata database session

        Raises:
            PluginExecutionError: if config file couldn't be found
        """
        config = invoker.plugin_config_processed

        config_script_lines = [
            "import sys",
            "module = sys.modules[__name__]",
            f"config = {config!r}",
            "for key, value in config.items():",
            "    if key.isupper():",
            "        setattr(module, key, value)",
        ]

        if custom_config_filename := invoker.plugin_config_extras["_config_path"]:
            custom_config_path = invoker.project.root.joinpath(custom_config_filename)

            if not custom_config_path.exists():
                raise PluginExecutionError(
                    f"Could not find config file {custom_config_path}",  # noqa: EM102
                )

            config_script_lines.extend(
                [
                    "from importlib.util import module_from_spec, spec_from_file_location",  # noqa: E501
                    f'spec = spec_from_file_location("superset_config", {str(custom_config_path)!r})',  # noqa: E501
                    "custom_config = module_from_spec(spec)",
                    'sys.modules["superset_config"] = custom_config',
                    "spec.loader.exec_module(custom_config)",
                    "for key in dir(custom_config):",
                    "    if key.isupper():",
                    "        setattr(module, key, getattr(custom_config, key))",
                ],
            )

            logger.info(f"Merged in config from {custom_config_path}")  # noqa: G004
        config_path = invoker.files["config"]
        async with await anyio.open_file(config_path, "w") as config_file:
            await config_file.write("\n".join(config_script_lines))
        logger.debug(f"Created configuration at {config_path}")  # noqa: G004

    @hook("before_invoke")
    async def db_upgrade_hook(
        self,
        invoker: PluginInvoker,
        exec_args: list[str],  # noqa: ARG002
    ) -> None:
        """Create or upgrade metadata database.

        Args:
            invoker: the active PluginInvoker
            exec_args: the args being passed

        Raises:
            AsyncSubprocessError: if command failed to run
        """
        handle = await invoker.invoke_async(
            "db",
            "upgrade",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                (
                    "Superset metadata database could not be initialized: "  # noqa: EM101
                    "`superset db upgrade` failed"
                ),
                handle,
            )

        logger.debug("Completed `superset db upgrade`")

    @hook("before_invoke")
    async def init_hook(
        self,
        invoker: PluginInvoker,
        exec_args: list[str],  # noqa: ARG002
    ) -> None:
        """Create default roles and permissions.

        Args:
            invoker: the active PluginInvoker
            exec_args: the args being passed

        Raises:
            AsyncSubprocessError: if command failed to run
        """
        handle = await invoker.invoke_async(
            "init",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        exit_code = await handle.wait()

        if exit_code:
            raise AsyncSubprocessError(
                (
                    "Superset default roles and permissions could not be "  # noqa: EM101
                    "created: `superset init` failed"
                ),
                handle,
            )

        logger.debug("Completed `superset init`")

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
