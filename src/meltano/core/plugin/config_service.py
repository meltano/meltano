import os
import subprocess
import logging
import re
from pathlib import Path

from meltano.core.project import Project
from meltano.core.plugin import Plugin


class PluginConfigService:
    """
    Manage the plugin configuration files. Each plugin can expose a
    set of files that should be stubbed using environment variables.
    """

    def __init__(self, project: Project, plugin: Plugin, config_dir=None, run_dir=None):
        self.project = project
        self.plugin = plugin

        # delegate to project
        self.config_dir = config_dir or project.plugin_dir(plugin)
        self.run_dir = run_dir or project.run_dir(plugin.name)

    @classmethod
    def envsubst(cls, src: Path, dst: Path, env={}):
        # find viable substitutions
        var_matcher = re.compile(
            """
            \$                 # starts with a '$'
            (?:                # either $VAR or ${VAR}
                {(\w+)}|(\w+)  # capture the variable name as group[0] or group[1]
            )
            """,
            re.VERBOSE,
        )

        env_override = os.environ.copy()
        env_override.update(env)

        def subst(match) -> str:
            try:
                # the variable can be in either group
                var = next(var for var in match.groups() if var)
                val = str(env_override[var])

                if not val:
                    logging.warning(f"Variable {var} is empty.")

                return val
            except KeyError as e:
                logging.warning(f"Variable {var} is missing from the environment.")
                return None

        with src.open() as i, dst.open("w+") as o:
            output = re.sub(var_matcher, subst, i.read())
            o.write(output)

    def configure(self):
        os.makedirs(self.run_dir, exist_ok=True)

        config_file = self.config_dir.joinpath
        run_file = self.run_dir.joinpath

        # grab the list of files the plugin needs
        stubs = (
            (run_file(file_name), config_file(file_name))
            for file_name in self.plugin.config_files.values()
        )

        stubbed = []
        # stub the files from the env
        for dst, src in stubs:
            try:
                self.envsubst(src, dst)
                stubbed.append(dst)
            except FileNotFoundError:
                logging.warning(
                    f"Could not find {src.name} in {src.resolve()}, skipping."
                )

        return stubbed
