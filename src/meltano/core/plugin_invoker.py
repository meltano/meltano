import asyncio
import enum
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from async_generator import asynccontextmanager
from meltano.core.logging.utils import SubprocessOutputWriter

from .error import Error
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

    class StdioSource(str, enum.Enum):  # noqa: WPS431
        """Describes the available unix style std io sources."""

        STDIN = "stdin"
        STDOUT = "stdout"
        STDERR = "stderr"

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        context: Optional[object] = None,
        output_handlers: Optional[dict] = None,
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
        self.output_handlers = output_handlers

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
            project,
            plugin,
            plugins_service=self.plugins_service,
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
    def files(self) -> Dict[str, Path]:
        """Get all config and output files of the plugin."""
        plugin_files = {**self.plugin.config_files, **self.plugin.output_files}

        return {
            _key: self.plugin_config_service.run_dir.joinpath(filename)
            for _key, filename in plugin_files.items()
        }

    async def prepare(self, session):
        """Prepare plugin config."""
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

        async with self.plugin.trigger_hooks("configure", self, session):
            self.plugin_config_service.configure()
            self._prepared = True

    async def cleanup(self):
        """Reset the plugin config."""
        self.plugin_config = {}
        self.plugin_config_processed = {}
        self.plugin_config_extras = {}
        self.plugin_config_env = {}

        async with self.plugin.trigger_hooks("cleanup", self):
            self._prepared = False

    @asynccontextmanager
    async def prepared(self, session):
        """Context manager that prepares plugin config , yielding to the caller, and then resetting the config."""
        try:
            await self.prepare(session)
            yield
        finally:
            await self.cleanup()

    def exec_path(self, executable: Optional[str] = None) -> Union[str, Path]:
        """
        Return the absolute path to the executable.

        Uses the plugin executable if none is specified.
        """
        executable = executable or self.plugin.executable
        if not self.venv_service:
            if "/" not in executable.replace("\\", "/"):
                # Expect executable on path
                return executable

            # Return executable relative to project directory
            return self.project.root.joinpath(executable)

        # Return executable within venv
        return self.venv_service.exec_path(executable)

    def exec_args(self, *args, command=None, env=None):
        """Materialize the arguments to be passed to the executable.

        Raises `UnknownCommandError` if requested command is not defined.
        """
        env = env or {}
        executable = self.exec_path()
        if command:
            command_config = self.find_command(command)
            plugin_args = command_config.expanded_args(command, env)
            if command_config.executable:
                executable = self.exec_path(command_config.executable)
        else:
            plugin_args = self.plugin.exec_args(self)

        return [str(arg) for arg in (executable, *plugin_args, *args)]

    def find_command(self, name):
        """Find a Command by name. Raises `UnknownCommandError` if not defined."""
        try:
            return self.plugin.all_commands[name]
        except KeyError as err:
            raise UnknownCommandError(self.plugin, name) from err

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

    def Popen_options(self) -> Dict[str, Any]:  # noqa: N802
        """Get options for subprocess.Popen."""
        return {}

    @asynccontextmanager
    async def _invoke(
        self,
        *args: str,
        require_preparation: bool = True,
        env: Optional[Dict[str, Any]] = None,
        command: Optional[str] = None,
        **kwargs,
    ):
        env = env or {}

        if require_preparation and not self._prepared:
            raise InvokerNotPreparedError()

        async with self.plugin.trigger_hooks("invoke", self, args):
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

    async def invoke_async(self, *args, **kwargs):
        async with self._invoke(*args, **kwargs) as (
            popen_args,
            popen_options,
            popen_env,
        ):
            return await asyncio.create_subprocess_exec(
                *popen_args,
                **popen_options,
                env=popen_env,
            )

    async def dump(self, file_id: str) -> str:
        """Dump a plugin file by id."""
        try:
            if file_id != "config":
                async with self._invoke():
                    return self.files[file_id].read_text()

            return self.files[file_id].read_text()
        except ExecutableNotFoundError as err:
            # Unwrap FileNotFoundError
            raise err.__cause__

    def add_output_handler(self, src: str, handler: SubprocessOutputWriter):
        """Append an output handler for a given stdio stream.

        Args:
            src: stdio source you'd like to subscribe, likely either 'stdout' or 'stderr'
            handler: either a StreamWriter or an object matching the utils.SubprocessOutputWriter proto
        """
        if self.output_handlers:
            self.output_handlers[src].append(handler)
        else:
            self.output_handlers = {src: [handler]}
