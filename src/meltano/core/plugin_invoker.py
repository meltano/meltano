import subprocess

from .project import Project
from .plugin import Plugin
from .venv_service import VenvService
from .runner.config_service import ConfigService


class PluginInvoker():
    """
    Expects the `run_dir` to be correctly configured
    """
    _prepared = False

    def __init__(self,
                 project: Project,
                 plugin: Plugin,
                 run_dir=None,
                 config_dir=None,
                 venv_service: VenvService = None,
                 config_service: ConfigService = None):
        self.project = project
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or ConfigService(project, plugin,
                                                              run_dir=run_dir,
                                                              config_dir=config_dir)

    @property
    def files(self):
        plugin_files = {
            **self.plugin.config_files,
            **self.plugin.output_files
        }

        return {_key: self.config_service.run_dir.joinpath(filename)
                for _key, filename in plugin_files.items()}

    def exec_path(self):
        return self.venv_service.exec_path(self.plugin.name, namespace=self.plugin.type)

    def exec_args(self):
        plugin_args = self.plugin.exec_args(self.files)

        return [str(arg) for arg in (self.exec_path(), *plugin_args)]

    def prepare(self):
        if not self._prepared:
            self.config_service.perform()
            self._prepared = True

    def invoke(self, **Popen):
        try:
            self.prepare()
            return subprocess.Popen(
                self.exec_args(),
                **Popen)

            return handle
        except Exception as err:
            logging.fatal(f"Failed to start plugin {self.plugin}.")
            raise
