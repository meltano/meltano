from __future__ import annotations  # noqa: D100

import shutil
import typing as t
from pathlib import Path

import structlog

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin

logger = structlog.stdlib.get_logger(__name__)


class PluginConfigService:
    """Manage the plugin configuration files.

    Each plugin can expose a set of files that should be stubbed using
    environment variables.
    """

    def __init__(  # noqa: D107
        self,
        plugin: ProjectPlugin,
        config_dir: str | Path,
        run_dir: str | Path,
    ):
        self.plugin = plugin
        self.config_dir = Path(config_dir)
        self.run_dir = Path(run_dir)

    def configure(self) -> list[Path]:  # noqa: D102
        self.run_dir.mkdir(parents=True, exist_ok=True)

        config_file = self.config_dir.joinpath
        run_file = self.run_dir.joinpath

        # grab the list of files the plugin needs
        stubs = (
            (run_file(file_name), config_file(file_name))
            for file_id, file_name in self.plugin.config_files.items()
            if file_id != "config"
        )

        stubbed = []
        # stub the files from the env
        for dst, src in stubs:
            try:
                shutil.copy(src, dst)
                stubbed.append(dst)
            except FileNotFoundError:  # noqa: PERF203
                logger.debug(
                    f"Could not find {src.name} in {src.resolve()}, skipping.",  # noqa: G004
                )

        return stubbed
