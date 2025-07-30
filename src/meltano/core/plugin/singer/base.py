from __future__ import annotations  # noqa: D100

import json
import logging
import typing as t
from textwrap import dedent

import anyio
import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.plugin import BasePlugin
from meltano.core.utils import nest_object, uuid7

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.plugin_invoker import PluginInvoker

logger = structlog.stdlib.get_logger(__name__)


class SingerPlugin(BasePlugin):  # noqa: D101
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize a `SingerPlugin`.

        Args:
            args: Positional arguments for the super class.
            kwargs: Keyword arguments for the super class.
        """
        super().__init__(*args, **kwargs)
        # Canonical class leads to an error if the UUID is defined here
        # directly. Also, this data attribute must be defined or we'll get
        # errors from Canonical.
        self._instance_uuid: str | None = None

    def process_config(self, flat_config: dict) -> dict:  # noqa: D102
        non_null_config = {k: v for k, v in flat_config.items() if v is not None}
        processed_config = nest_object(non_null_config)
        # Result at this point will contain duplicate entries for nested config
        # options. We need to pop those redundant entries recursively.

        def _pop_non_leaf_keys(nested_config: dict) -> None:
            """Recursively pop dictionary entries with '.' in their keys."""
            for key, val in list(nested_config.items()):
                if "." in key:
                    nested_config.pop(key)
                elif isinstance(val, dict):
                    _pop_non_leaf_keys(val)

        _pop_non_leaf_keys(processed_config)
        return processed_config

    def exec_env(self, plugin_invoker: PluginInvoker) -> dict[str, str]:
        """Get the environment variables for this tap.

        Args:
            plugin_invoker: the plugin invoker running

        Returns:
            the environment variables for this tap
        """
        return {
            "SINGER_SDK_LOG_CONFIG": str(plugin_invoker.files["singer_sdk_logging"]),
            "LOGGING_CONF_FILE": str(
                plugin_invoker.files["pipelinewise_singer_logging"],
            ),
        }

    @hook("before_configure")
    async def before_configure(
        self,
        invoker: PluginInvoker,
        session: Session,  # noqa: ARG002
    ) -> None:
        """Create configuration file."""
        config_path = invoker.files["config"]
        async with await anyio.open_file(config_path, "w") as config_file:
            config = invoker.plugin_config_processed
            await config_file.write(json.dumps(config, indent=2))

        logger.debug(f"Created configuration at {config_path}")  # noqa: G004

    @hook("before_cleanup")
    async def before_cleanup(self, invoker: PluginInvoker) -> None:
        """Delete configuration file."""
        config_path = invoker.files["config"]
        config_path.unlink()
        logger.debug(f"Deleted configuration at {config_path}")  # noqa: G004

    @hook("before_invoke")
    async def setup_logging_hook(
        self,
        plugin_invoker: PluginInvoker,
        exec_args: tuple[str, ...] = (),  # noqa: ARG002
    ) -> None:
        """Set up logging before invoking tap.

        Args:
            plugin_invoker: the plugin invoker running
            exec_args: the args being passed to the tap

        Returns:
            None
        """
        singer_sdk_logging = plugin_invoker.files["singer_sdk_logging"]
        pipelinewise_logging = plugin_invoker.files["pipelinewise_singer_logging"]

        log_level = logging.getLevelName(logger.getEffectiveLevel())

        # https://sdk.meltano.com/en/v0.44.3/implementation/logging.html
        async with await anyio.open_file(singer_sdk_logging, mode="w") as f:
            await f.write(
                json.dumps(
                    {
                        "version": 1,
                        "disable_existing_loggers": False,
                        "formatters": {
                            "default": {
                                "format": "%(message)s",
                            },
                        },
                        "handlers": {
                            "console": {
                                "class": "logging.StreamHandler",
                                "formatter": "default",
                                "stream": "ext://sys.stderr",
                                "level": log_level,
                            },
                        },
                        "root": {
                            "handlers": ["console"],
                        },
                    },
                    indent=2,
                ),
            )

        # https://github.com/transferwise/pipelinewise-singer-python/blob/da64a10cdbcad48ab373d4dab3d9e6dd6f58556b/singer/logger.py#L9C9-L9C26
        async with await anyio.open_file(pipelinewise_logging, mode="w") as f:
            await f.write(
                dedent(f"""\
                [loggers]
                keys=root

                [handlers]
                keys=console

                [formatters]
                keys=default

                [logger_root]
                handlers=console

                [handler_console]
                class=StreamHandler
                level={log_level}
                formatter=default
                args=(sys.stderr,)

                [formatter_default]
                format=%(message)s
                """),
            )

    @property
    def instance_uuid(self) -> str:
        """Multiple processes running at the same time have a unique value to use."""
        if not self._instance_uuid:
            self._instance_uuid = str(uuid7())
        return self._instance_uuid
