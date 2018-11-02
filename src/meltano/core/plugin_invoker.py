import logging
import subprocess

from .project import Project
from .plugin import Plugin
from .plugin.error import PluginMissingError
from .plugin.config_service import PluginConfigService
from .venv_service import VenvService


class PluginInvoker:
    """This class handles the invocation of a `Plugin` instance."""

    def __init__(
        self,
        project: Project,
        plugin: Plugin,
        run_dir=None,
        config_dir=None,
        venv_service: VenvService = None,
        config_service: PluginConfigService = None,
    ):
        self.project = project
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or PluginConfigService(
            project, plugin, run_dir=run_dir, config_dir=config_dir
        )

        self._prepared = False

    @property
    def files(self):
        plugin_files = {**self.plugin.config_files, **self.plugin.output_files}

        return {
            _key: self.config_service.run_dir.joinpath(filename)
            for _key, filename in plugin_files.items()
        }

    def prepare(self):
        if not self._prepared:
            self.config_service.configure()
            self._prepared = True

    def exec_path(self):
        return self.venv_service.exec_path(self.plugin.name, namespace=self.plugin.type)

    def exec_args(self):
        plugin_args = self.plugin.exec_args(self.files)

        return [str(arg) for arg in (self.exec_path(), *plugin_args)]

    def invoke(self, *args, **Popen):
        try:
            self.prepare()
            with self.plugin.trigger_hooks("invoke", self, args):
                return subprocess.Popen([*self.exec_args(), *args], **Popen)

        except Exception as err:
            logging.error(f"Failed to start plugin {self.plugin}.")
            raise PluginMissingError(self.plugin)
