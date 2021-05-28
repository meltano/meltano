import asyncio
import copy
import logging
import os
import subprocess
from contextlib import contextmanager
from typing import Optional

from .error import Error, SubprocessError
from .plugin import PluginRef
from .plugin.config_service import PluginConfigService
from .plugin.project_plugin import ProjectPlugin
from .plugin.settings_service import PluginSettingsService
from .project import Project
from .project_plugins_service import ProjectPluginsService
from .venv_service import VenvService, VirtualEnv


def invoker_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    cls = PluginInvoker

    if hasattr(plugin, "invoker_class"):
        cls = plugin.invoker_class

    invoker = cls(project, plugin, *args, **kwargs)

    return invoker


class InvokerError(Error):
    pass


class ExecutableNotFoundError(InvokerError):
    """Occurs when the executable could not be found"""

    def __init__(self, plugin: PluginRef, executable):
        super().__init__(
            f"Executable '{executable}' could not be found. "
            f"{plugin.type.descriptor.capitalize()} '{plugin.name}' may not have been installed yet using `meltano install {plugin.type.singular} {plugin.name}`, or the executable name may be incorrect."
        )


class InvokerNotPreparedError(InvokerError):
    """Occurs when `invoke` is called before `prepare`"""

    pass


class UnknownCommandError(InvokerError):
    """Occurs when `invoke` is called in command mode with an undefined command."""

    def __init__(self, plugin: PluginRef, command):
        """Initialize UnknownCommandError."""
        self.plugin = plugin
        self.command = command

    def __str__(self):
        """Return error message."""
        if self.plugin.supported_commands:
            supported_commands = ", ".join(self.plugin.supported_commands)
            desc = f"supports the following commands: {supported_commands}"
        else:
            desc = "does not define any commands."
        return " ".join(
            [
                f"Command '{self.command}' could not be found.",
                f"{self.plugin.type.descriptor.capitalize()} '{self.plugin.name}'",
                desc,
            ]
        )


class PluginInvoker:
    """This class handles the invocation of a `ProjectPlugin` instance."""

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        context: Optional[object] = None,
        run_dir=None,
        config_dir=None,
        venv_service: VenvService = None,
        plugins_service: ProjectPluginsService = None,
        plugin_config_service: PluginConfigService = None,
        plugin_settings_service: PluginSettingsService = None,
    ):
        self.project = project
        self.plugin = plugin
        self.context = context

        self.venv_service: Optional[VenvService] = None
        if plugin.pip_url or venv_service:
            self.venv_service = venv_service or VenvService(
                project,
                name=plugin.name,
                namespace=plugin.type,
            )
        self.plugin_config_service = plugin_config_service or PluginConfigService(
            plugin,
            config_dir or self.project.plugin_dir(plugin),
            run_dir or self.project.run_dir(plugin.name),
        )

        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.settings_service = plugin_settings_service or PluginSettingsService(
            project, plugin, plugins_service=self.plugins_service
        )

        self._prepared = False
        self.plugin_config = {}
        self.plugin_config_processed = {}
        self.plugin_config_extras = {}
        self.plugin_config_env = {}

    @property
    def capabilities(self):
        # we want to make sure the capabilites are immutable from the `PluginInvoker` interface
        return frozenset(self.plugin.capabilities)

    @property
    def files(self):
        plugin_files = {**self.plugin.config_files, **self.plugin.output_files}

        return {
            _key: self.plugin_config_service.run_dir.joinpath(filename)
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
        self.plugin_config_env = self.settings_service.as_env(session=session)

        with self.plugin.trigger_hooks("configure", self, session):
            self.plugin_config_service.configure()
            self._prepared = True

    def cleanup(self):
        self.plugin_config = {}
        self.plugin_config_processed = {}
        self.plugin_config_extras = {}
        self.plugin_config_env = {}

        with self.plugin.trigger_hooks("cleanup", self):
            self._prepared = False

    @contextmanager
    def prepared(self, session):
        try:
            self.prepare(session)
            yield
        finally:
            self.cleanup()

    def exec_path(self):
        if not self.venv_service:
            if "/" not in self.plugin.executable.replace("\\", "/"):
                # Expect executable on path
                return self.plugin.executable

            # Return executable relative to project directory
            return self.project.root.joinpath(self.plugin.executable)

        # Return executable within venv
        return self.venv_service.exec_path(self.plugin.executable)

    def exec_args(self, *args, command=None, env=None):
        """Materialize the arguments to be passed to the executable."""
        env = env or {}
        if command:
            try:
                plugin_args = self.plugin.all_commands[command].expanded_args(
                    command, env
                )
            except KeyError as err:
                raise UnknownCommandError(self.plugin, command) from err
        else:
            plugin_args = self.plugin.exec_args(self)

        return [str(arg) for arg in (self.exec_path(), *plugin_args, *args)]

    def env(self):
        env = {
            **self.project.dotenv_env,
            **self.settings_service.env,
            **self.plugin_config_env,
        }

        # Ensure Meltano venv is not inherited
        env.pop("VIRTUAL_ENV", None)
        env.pop("PYTHONPATH", None)
        if self.venv_service:
            # Switch to plugin-specific venv
            venv = VirtualEnv(
                self.project.venvs_dir(self.plugin.type, self.plugin.name)
            )
            venv_dir = str(venv.bin_dir)
            env["VIRTUAL_ENV"] = str(venv.root)
            env["PATH"] = os.pathsep.join([venv_dir, env["PATH"]])

        return env

    def Popen_options(self):
        return {}

    @contextmanager
    def _invoke(
        self,
        *args,
        require_preparation=True,
        env=None,
        command=None,
        **kwargs,
    ):
        env = env or {}

        if require_preparation and not self._prepared:
            raise InvokerNotPreparedError()

        with self.plugin.trigger_hooks("invoke", self, args):
            popen_options = {**self.Popen_options(), **kwargs}
            popen_env = {**self.env(), **env}
            popen_args = self.exec_args(*args, command=command, env=popen_env)
            logging.debug(f"Invoking: {popen_args}")
            logging.debug(f"Env: {popen_env}")

            try:
                yield (popen_args, popen_options, popen_env)
            except FileNotFoundError as err:
                raise ExecutableNotFoundError(
                    self.plugin, self.plugin.executable
                ) from err

    def invoke(self, *args, **kwargs):
        with self._invoke(*args, **kwargs) as (popen_args, popen_options, popen_env):
            return subprocess.Popen(popen_args, **popen_options, env=popen_env)

    async def invoke_async(self, *args, **kwargs):
        with self._invoke(*args, **kwargs) as (popen_args, popen_options, popen_env):
            return await asyncio.create_subprocess_exec(
                *popen_args,
                **popen_options,
                env=popen_env,
            )

    def dump(self, file_id):
        try:
            with self._invoke():
                return self.files[file_id].read_text()
        except ExecutableNotFoundError as err:
            # Unwrap FileNotFoundError
            raise err.__cause__
