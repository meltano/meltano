import os
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Union

from meltano.core.project import Project
from meltano.core.plugin import ProjectPlugin


class PluginConfigService:
    """
    Manage the plugin configuration files. Each plugin can expose a
    set of files that should be stubbed using environment variables.
    """

    def __init__(
        self,
        plugin: ProjectPlugin,
        config_dir: Union[str, Path],
        run_dir: Union[str, Path],
    ):
        self.plugin = plugin
        self.config_dir = Path(config_dir)
        self.run_dir = Path(run_dir)

    def configure(self):
        os.makedirs(self.run_dir, exist_ok=True)

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
            except FileNotFoundError:
                logging.debug(
                    f"Could not find {src.name} in {src.resolve()}, skipping."
                )

        return stubbed
