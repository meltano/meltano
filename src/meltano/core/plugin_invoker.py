import logging
import subprocess
import asyncio
import os
import copy
from typing import Optional

from .project import Project
from .plugin import PluginInstall
from .plugin.error import PluginMissingError, PluginExecutionError
from .plugin.config_service import PluginConfigService
from .plugin.settings_service import PluginSettingsService
from .plugin_discovery_service import PluginDiscoveryService
from .venv_service import VenvService, VirtualEnv
from .error import Error, SubprocessError


def invoker_factory(project, plugin, *args, prepare_with_session=None, **kwargs):
    cls = PluginInvoker

    if hasattr(plugin.__class__, "__invoker_cls__"):
        cls = plugin.__class__.__invoker_cls__

    invoker = cls(project, plugin, *args, **kwargs)

    if prepare_with_session:
        invoker.prepare(prepare_with_session)

    return invoker


class InvokerNotPreparedError(Error):
    """Occurs when `invoke` is called before `prepare`"""

    pass


class PluginInvoker:
    """This class handles the invocation of a `Plugin` instance."""

    def __init__(
        self,
        project: Project,
        plugin: PluginInstall,
        plugin_config: Optional[dict] = None,
        run_dir=None,
        config_dir=None,
        venv_service: VenvService = None,
        plugin_config_service: PluginConfigService = None,
        plugin_settings_service: PluginSettingsService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)
        self.config_service = plugin_config_service or PluginConfigService(
            plugin,
            config_dir or self.project.plugin_dir(plugin),
            run_dir or self.project.run_dir(plugin.name),
        )
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self.settings_service = plugin_settings_service or PluginSettingsService(
            project,
            plugin,
            config_service=self.discovery_service.config_service,
            plugin_discovery_service=self.discovery_service,
        )
        self.plugin_def = self.discovery_service.find_plugin(
            self.plugin.type, self.plugin.name
        )
        self._prepared = False
        self.plugin_config = {}
        self.plugin_config_processed = {}
        self.plugin_config_extras = {}
        self.plugin_config_env = {}

    @property
    def capabilities(self):
        # we want to make sure the capabilites are immutable from the `PluginInvoker` interface
        return frozenset(self.plugin_def.capabilities)

    @property
    def files(self):
        plugin_files = {**self.plugin.config_files, **self.plugin.output_files}

        return {
            _key: self.config_service.run_dir.joinpath(filename)
            for _key, filename in plugin_files.items()
        }

    def prepare(self, session):
        self.plugin_config = self.settings_service.as_dict(
            extras=False, session=session
        )
        self.plugin_config_processed = self.settings_service.as_dict(
            extras=False, process=True, session=session
        )
        self.plugin_config_extras = self.settings_service.as_dict(
            extras=True, session=session
        )
        self.plugin_config_env = self.settings_service.as_env(
            extras=False, session=session
        )

        with self.plugin.trigger_hooks("configure", self, session):
            self.config_service.configure()
            self._prepared = True

    def exec_path(self):
        return self.venv_service.exec_path(
            self.plugin.executable or self.plugin.name,
            name=self.plugin.name,
            namespace=self.plugin.type,
        )

    def exec_args(self, *args):
        plugin_args = self.plugin.exec_args(self)

        return [str(arg) for arg in (self.exec_path(), *plugin_args, *args)]

    def env(self):
        env = {**self.settings_service.env, **self.plugin_config_env}

        # Ensure Meltano venv is not inherited
        venv = VirtualEnv(self.project.venvs_dir(self.plugin.type, self.plugin.name))
        env["VIRTUAL_ENV"] = str(venv.root)
        env["PATH"] = os.pathsep.join([str(venv.bin_dir), env["PATH"]])
        env.pop("PYTHONPATH", None)

        return env

    def Popen_options(self):
        return {}

    def invoke(self, *args, require_preparation=True, env={}, **Popen):
        if require_preparation and not self._prepared:
            raise InvokerNotPreparedError()

        process = None
        try:
            with self.plugin.trigger_hooks("invoke", self, args):
                popen_args = self.exec_args(*args)
                popen_options = {**self.Popen_options(), **Popen}
                popen_env = {**self.env(), **env}
                logging.debug(f"Invoking: {popen_args}")
                logging.debug(f"Env: {popen_env}")

                process = subprocess.Popen(popen_args, **popen_options, env=popen_env)
        except SubprocessError as perr:
            logging.error(f"{self.plugin.name} has failed: {str(perr)}")
            raise
        except Exception as err:
            logging.error(f"Failed to start plugin {self.plugin}.")
            raise

        return process

    async def invoke_async(self, *args, require_preparation=True, env={}, **Popen):
        if require_preparation and not self._prepared:
            raise InvokerNotPreparedError()

        process = None
        try:
            with self.plugin.trigger_hooks("invoke", self, args):
                popen_args = self.exec_args(*args)
                popen_options = {**self.Popen_options(), **Popen}
                popen_env = {**self.env(), **env}
                logging.debug(f"Invoking: {popen_args}")
                logging.debug(f"Env: {popen_env}")

                process = await asyncio.create_subprocess_exec(
                    *popen_args, limit=1024 * 128, **popen_options, env=popen_env
                )
        except SubprocessError as perr:
            logging.error(f"{self.plugin.name} has failed: {str(perr)}")
            raise
        except Exception as err:
            logging.error(f"Failed to start plugin {self.plugin}.")
            raise

        return process
