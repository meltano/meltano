import logging
import subprocess
import asyncio
import os

from .project import Project
from .plugin import PluginInstall
from .plugin.error import PluginMissingError, PluginExecutionError
from .plugin.config_service import PluginConfigService
from .plugin.settings_service import PluginSettingsService
from .venv_service import VenvService
from .error import SubprocessError


def invoker_factory(session, project, plugin, *args, **kwargs):
    return plugin.invoker(session, project, *args, **kwargs) or PluginInvoker(
        session, project, plugin, *args, **kwargs
    )


class PluginInvoker:
    """This class handles the invocation of a `Plugin` instance."""

    def __init__(
        self,
        session,
        project: Project,
        plugin: PluginInstall,
        run_dir=None,
        config_dir=None,
        venv_service: VenvService = None,
        config_service: PluginConfigService = None,
        plugin_settings_service: PluginSettingsService = None,
    ):
        self.project = project
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or PluginConfigService(
            project, plugin, run_dir=run_dir, config_dir=config_dir
        )
        self.plugin_settings = plugin_settings_service or PluginSettingsService(
            session, project
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
            with self.plugin.trigger_hooks("configure", self):
                self.config_service.configure()
                self._prepared = True

    def exec_path(self):
        return self.venv_service.exec_path(
            self.plugin.executable,
            name=self.plugin.canonical_name,
            namespace=self.plugin.type,
        )

    def exec_args(self):
        plugin_args = self.plugin.exec_args(self.files)

        return [str(arg) for arg in (self.exec_path(), *plugin_args)]

    def Popen_options(self):
        return {}

    def invoke(self, *args, prepare=True, **Popen):
        Popen_options = self.Popen_options()
        Popen_options.update(Popen)

        process = None
        try:
            if prepare:
                self.prepare()

            with self.plugin.trigger_hooks("invoke", self, args):
                popen_args = [*self.exec_args(), *args]
                logging.debug(f"Invoking: {popen_args}")
                process = subprocess.Popen(popen_args, **Popen_options)
        except SubprocessError as perr:
            logging.error(f"{self.plugin.name} has failed: {str(perr)}")
            raise
        except Exception as err:
            logging.error(f"Failed to start plugin {self.plugin}.")
            raise

        return process

    async def invoke_async(self, *args, prepare=True, **Popen):
        Popen_options = self.Popen_options()
        Popen_options.update(Popen)

        process = None
        try:
            if prepare:
                self.prepare()

            with self.plugin.trigger_hooks("invoke", self, args):
                process = await asyncio.create_subprocess_exec(
                    *self.exec_args(), *args, **Popen_options
                )
        except SubprocessError as perr:
            logging.error(f"{self.plugin.name} has failed: {str(perr)}")
            raise
        except Exception as err:
            logging.error(f"Failed to start plugin {self.plugin}.")
            raise

        return process
