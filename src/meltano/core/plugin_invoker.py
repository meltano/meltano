"""Plugin invoker class."""

from __future__ import annotations

import asyncio
import enum
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Generator

from structlog.stdlib import get_logger

from meltano.core.container.container_service import ContainerService
from meltano.core.logging.utils import SubprocessOutputWriter

from .error import Error
from .plugin import PluginRef
from .plugin.config_service import PluginConfigService
from .plugin.project_plugin import ProjectPlugin
from .plugin.settings_service import PluginSettingsService
from .project import Project
from .project_plugins_service import ProjectPluginsService
from .project_settings_service import ProjectSettingsService
from .settings_service import FeatureFlags
from .utils import expand_env_vars
from .venv_service import VenvService, VirtualEnv

logger = get_logger(__name__)


def invoker_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    """Instantiate a plugin invoker from a project plugin.

    Args:
        project: Meltano project.
        plugin: Plugin instance.
        args: Invoker constructor positional arguments.
        kwargs: Invoker constructor keyword arguments.

    Returns:
        A plugin invoker.
    """
    cls = PluginInvoker  # noqa: WPS117

    if hasattr(plugin, "invoker_class"):  # noqa: WPS421
        cls = plugin.invoker_class  # noqa: WPS117

    return cls(project, plugin, *args, **kwargs)


class InvokerError(Error):
    """Generic plugin invoker error."""


class ExecutableNotFoundError(InvokerError):
    """Occurs when the executable could not be found."""

    def __init__(self, plugin: PluginRef, executable: str):
        """Initialize ExecutableNotFoundError.

        Args:
            plugin: Meltano plugin reference.
            executable: Plugin command executable.
        """
        plugin_type_descriptor = plugin.type.descriptor.capitalize()
        plugin_type = plugin.type.singular
        super().__init__(
            f"Executable '{executable}' could not be found. "
            + f"{plugin_type_descriptor} '{plugin.name}' may not have "
            + "been installed yet using "
            + f"`meltano install {plugin_type} {plugin.name}`, "
            + "or the executable name may be incorrect."
        )


class InvokerNotPreparedError(InvokerError):
    """Occurs when `invoke` is called before `prepare`."""


class UnknownCommandError(InvokerError):
    """Occurs when `invoke` is called in command mode with an undefined command."""

    def __init__(self, plugin: PluginRef, command):
        """Initialize UnknownCommandError.

        Args:
            plugin: Meltano plugin reference.
            command: Plugin command name.
        """
        self.plugin = plugin
        self.command = command

    def __str__(self):
        """Return error message.

        Returns:
            String representation of this exception.
        """
        if self.plugin.supported_commands:
            supported_commands = ", ".join(self.plugin.supported_commands)
            desc = f"supports the following commands: {supported_commands}"
        else:
            desc = "does not define any commands."
        plugin_type_descriptor = self.plugin.type.descriptor.capitalize()
        plugin_name = self.plugin.name
        return " ".join(
            [
                f"Command '{self.command}' could not be found.",
                f"{plugin_type_descriptor} '{plugin_name}'",
                desc,
            ]
        )


class PluginInvoker:  # noqa: WPS214, WPS230
    """This class handles the invocation of a `ProjectPlugin` instance."""

    class StdioSource(str, enum.Enum):
        """Describes the available unix style std io sources."""

        STDIN = "stdin"
        STDOUT = "stdout"
        STDERR = "stderr"

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        context: Any | None = None,
        output_handlers: dict | None = None,
        run_dir: Path | None = None,
        config_dir: Path | None = None,
        venv_service: VenvService | None = None,
        plugins_service: ProjectPluginsService | None = None,
        plugin_config_service: PluginConfigService | None = None,
        plugin_settings_service: PluginSettingsService | None = None,
    ):
        """Create a new plugin invoker.

        Args:
            project: Meltano Project.
            plugin: Meltano Plugin.
            context: Invocation context.
            output_handlers: Logging and output handlers.
            run_dir: Execution directory.
            config_dir: Configuration files directory.
            venv_service: Virtual Environment manager.
            plugins_service: Plugin manager.
            plugin_config_service: Plugin Configuration manager.
            plugin_settings_service: Plugin Settings manager.
        """
        self.project = project
        self.plugin = plugin
        self.context = context
        self.output_handlers = output_handlers

        self.venv_service: VenvService | None = None
        if plugin.pip_url or venv_service:
            self.venv_service = venv_service or VenvService(
                project,
                name=plugin.venv_name,
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
        """Get plugin immutable capabilities.

        Makes sure the capabilities are immutable from the `PluginInvoker` interface.

        Returns:
            The set of plugin capabilities.
        """
        return frozenset(self.plugin.capabilities)

    @property
    def files(self) -> dict[str, Path]:
        """Get all config and output files of the plugin.

        Returns:
            A mapping of file IDs to file names.
        """
        plugin_files = {**self.plugin.config_files, **self.plugin.output_files}

        return {
            _key: self.plugin_config_service.run_dir.joinpath(filename)
            for _key, filename in plugin_files.items()
        }

    async def prepare(self, session):
        """Prepare plugin config.

        Args:
            session: Database session.
        """
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
        """Context manager that prepares plugin config.

        Args:
            session: Database session.

        Yields:
            Yields to the caller, then resetting the config.
        """
        try:  # noqa: WPS229. Allow try body of length > 1.
            await self.prepare(session)
            yield
        finally:
            await self.cleanup()

    def exec_path(self, executable: str | None = None) -> str | Path:
        """Return the absolute path to the executable.

        Uses the plugin executable if none is specified.

        Args:
            executable: Optional executable string.

        Returns:
            Full path to the executable.
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

        Args:
            args: Optional plugin args.
            command: Plugin command name.
            env: Environment variables

        Returns:
            List of plugin invocation arguments.
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
        """Find a Command by name.

        Args:
            name: Command name.

        Returns:
            Command instance.

        Raises:
            UnknownCommandError: If command is not defined.
        """
        try:
            return self.plugin.all_commands[name]
        except KeyError as err:
            raise UnknownCommandError(self.plugin, name) from err

    def env(self):
        """Environment variable mapping.

        Returns:
            Dictionary of environment variables.
        """
        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.plugins_service.config_service
        )
        with project_settings_service.feature_flag(
            FeatureFlags.STRICT_ENV_VAR_MODE, raise_error=False
        ) as strict_env_var_mode:

            # Expand root env w/ os.environ
            expanded_project_env = expand_env_vars(
                project_settings_service.env,
                os.environ,
                raise_if_missing=strict_env_var_mode,
            )
            expanded_project_env.update(
                expand_env_vars(
                    self.settings_service.project.dotenv_env,
                    os.environ,
                    raise_if_missing=strict_env_var_mode,
                )
            )
            # Expand active env w/ expanded root env
            expanded_active_env = (
                expand_env_vars(
                    self.settings_service.project.active_environment.env,
                    expanded_project_env,
                    raise_if_missing=strict_env_var_mode,
                )
                if self.settings_service.project.active_environment
                else {}
            )

            # Expand root plugin env w/ expanded active env
            expanded_root_plugin_env = expand_env_vars(
                self.settings_service.plugin.env,
                expanded_active_env,
                raise_if_missing=strict_env_var_mode,
            )

            # Expand active env plugin env w/ expanded root plugin env
            expanded_active_env_plugin_env = (
                expand_env_vars(
                    self.settings_service.environment_plugin_config.env,
                    expanded_root_plugin_env,
                    raise_if_missing=strict_env_var_mode,
                )
                if self.settings_service.environment_plugin_config
                else {}
            )

        env = {
            **expanded_project_env,
            **self.project.dotenv_env,
            **self.settings_service.env,
            **self.plugin_config_env,
            **expanded_root_plugin_env,
            **expanded_active_env,
            **expanded_active_env_plugin_env,
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

    def Popen_options(self) -> dict[str, Any]:  # noqa: N802
        """Get options for subprocess.Popen.

        Returns:
            Mapping of subprocess options.
        """
        return {}

    @asynccontextmanager
    async def _invoke(
        self,
        *args: str,
        require_preparation: bool = True,
        env: dict[str, Any] | None = None,
        command: str | None = None,
        **kwargs,
    ) -> Generator[list[str], dict[str, Any], dict[str, Any]]:  # noqa: WPS221
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

    async def invoke_async(self, *args, **kwargs) -> asyncio.subprocess.Process:
        """Invoke a command.

        Args:
            args: Positional arguments.
            kwargs: Keyword arguments.

        Returns:
            Subprocess.
        """
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

    async def invoke_docker(self, plugin_command: str, *args, **kwargs) -> int:
        """Invoke a containerized command.

        Args:
            plugin_command: Plugin command name.
            args: Command line invocation arguments.
            kwargs: Command line invocation keyword arguments.

        Raises:
            ValueError: If the command doesn't declare a container spec.

        Returns:
            The container run exit code.
        """
        command_config = self.find_command(plugin_command)

        if not command_config.container_spec:
            raise ValueError("Command is missing a container spec")

        spec = command_config.container_spec
        service = ContainerService()

        logger.debug("Running containerized command", command=plugin_command)
        async with self._invoke(*args, **kwargs) as (proc_args, _, proc_env):
            plugin_name = self.plugin.name
            random_id = uuid.uuid4()
            name = f"meltano-{plugin_name}--{plugin_command}-{random_id}"

            info = await service.run_container(spec, name, env=proc_env)

        return info["State"]["ExitCode"]

    async def dump(self, file_id: str) -> str:
        """Dump a plugin file by id.

        Args:
            file_id: Dump this file identifier.

        Returns:
            File contents.

        Raises:
            __cause__: If file is not found.
        """
        try:  # noqa: WPS229. Allow try body of length > 1.
            if file_id != "config":
                async with self._invoke():
                    return self.files[file_id].read_text()

            return self.files[file_id].read_text()
        except ExecutableNotFoundError as err:  # noqa: WPS329. Allow "useless" except.
            # Unwrap FileNotFoundError
            raise err.__cause__  # noqa: WPS609. Allow accessing magic attribute.

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
