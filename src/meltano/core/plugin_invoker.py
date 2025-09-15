"""Plugin invoker class."""

from __future__ import annotations

import asyncio
import enum
import os
import sys
import typing as t
from contextlib import asynccontextmanager

from structlog.stdlib import get_logger

from meltano.core.container.container_service import ContainerService
from meltano.core.error import Error
from meltano.core.manifest.loader import load_or_compile_manifest
from meltano.core.plugin.config_service import PluginConfigService
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.settings_service import FeatureFlags
from meltano.core.tracking import Tracker
from meltano.core.utils import EnvVarMissingBehavior, expand_env_vars, uuid7
from meltano.core.venv_service import VenvService, VirtualEnv

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Unpack  # noqa: ICN003
else:
    from backports.strenum import StrEnum
    from typing_extensions import Unpack

if t.TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

    from sqlalchemy.orm import Session

    from meltano.core.block.extract_load import ELBContext
    from meltano.core.elt_context import ELTContext, PluginContext
    from meltano.core.logging.utils import SubprocessOutputWriter
    from meltano.core.plugin import PluginRef
    from meltano.core.plugin.command import Command
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

    class InvokerInitKwargs(t.TypedDict, total=False):
        """Keyword arguments for the Invoker constructor."""

        context: ELTContext | ELBContext | PluginContext | None
        output_handlers: dict | None
        run_dir: Path | None
        config_dir: Path | None
        plugin_config_service: PluginConfigService | None
        plugin_settings_service: PluginSettingsService | None


logger = get_logger(__name__)


def invoker_factory(
    project: Project,
    plugin: ProjectPlugin,
    **kwargs: Unpack[InvokerInitKwargs],
) -> PluginInvoker:
    """Instantiate a plugin invoker from a project plugin.

    Args:
        project: Meltano project.
        plugin: Plugin instance.
        kwargs: Invoker constructor keyword arguments.

    Returns:
        A plugin invoker.
    """
    cls = PluginInvoker

    if hasattr(plugin, "invoker_class"):
        cls = plugin.invoker_class

    return cls(project, plugin, **kwargs)


class InvokerError(Error):
    """Generic plugin invoker error."""


class ExecutableNotFoundError(InvokerError):
    """The executable could not be found."""

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
            f"{plugin_type_descriptor} '{plugin.name}' may not have "
            "been installed yet using "
            f"`meltano install {plugin_type} {plugin.name}`, "
            "or the executable name may be incorrect.",
        )


class InvokerNotPreparedError(InvokerError):
    """Occurs when `invoke` is called before `prepare`."""


class UnknownCommandError(InvokerError):
    """Occurs when `invoke` is called in command mode with an undefined command."""

    def __init__(self, plugin: PluginRef, command: str) -> None:
        """Initialize UnknownCommandError.

        Args:
            plugin: Meltano plugin reference.
            command: Plugin command name.
        """
        self.plugin = plugin
        self.command = command

    def __str__(self) -> str:
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
            ],
        )


class PluginInvoker:
    """This class handles the invocation of a `ProjectPlugin` instance."""

    class StdioSource(StrEnum):
        """Describes the available unix style std io sources."""

        STDIN = enum.auto()
        STDOUT = enum.auto()
        STDERR = enum.auto()

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        *,
        context: ELTContext | ELBContext | PluginContext | None = None,
        output_handlers: dict | None = None,
        run_dir: Path | None = None,
        config_dir: Path | None = None,
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
            plugin_config_service: Plugin Configuration manager.
            plugin_settings_service: Plugin Settings manager.
        """
        self.project = project
        self.tracker = Tracker(project)
        self.plugin = plugin
        self.context = context
        self.output_handlers = output_handlers
        self.venv_service: VenvService | None

        if plugin.pip_url:
            self.venv_service = VenvService(
                project=project,
                python=self.plugin.python,
                name=plugin.plugin_dir_name,
                namespace=plugin.type,
            )
        else:
            self.venv_service = None

        self.plugin_config_service = plugin_config_service or PluginConfigService(
            plugin,
            config_dir or self.project.plugin_dir(plugin),
            run_dir or self.project.run_dir(plugin.name),
        )

        self.settings_service = plugin_settings_service or PluginSettingsService(
            project,
            plugin,
        )

        self._prepared = False
        self.plugin_config: dict = {}
        self.plugin_config_processed: dict = {}
        self.plugin_config_extras: dict = {}
        self.plugin_config_env: dict[str, str] = {}

        # Manifest data is loaded lazily when needed
        self._manifest_data: dict[str, t.Any] | None = None
        self._manifest_loaded = False

    @property
    def capabilities(self) -> frozenset[str]:
        """Get plugin immutable capabilities.

        Makes sure the capabilities are immutable from the `PluginInvoker` interface.

        Returns:
            The set of plugin capabilities.
        """
        return frozenset(self.plugin.capabilities)  # type: ignore[arg-type]

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

    async def prepare(self, session: Session) -> None:
        """Prepare plugin config.

        Args:
            session: Database session.
        """
        self.plugin_config = self.settings_service.as_dict(
            extras=False,
            session=session,
        )
        self.plugin_config_processed = self.settings_service.as_dict(
            extras=False,
            process=True,
            session=session,
        )
        self.plugin_config_extras = self.settings_service.as_dict(
            extras=True,
            session=session,
        )
        self.plugin_config_env = self.settings_service.as_env(session=session)
        async with self.plugin.trigger_hooks("configure", self, session):
            self.plugin_config_service.configure()
            self._prepared = True

    async def cleanup(self) -> None:
        """Reset the plugin config."""
        self.plugin_config = {}
        self.plugin_config_processed = {}
        self.plugin_config_extras = {}
        self.plugin_config_env = {}

        async with self.plugin.trigger_hooks("cleanup", self):
            self._prepared = False

    @asynccontextmanager
    async def prepared(self, session: Session) -> t.AsyncGenerator[None, None]:
        """Context manager that prepares plugin config.

        Args:
            session: Database session.

        Yields:
            Yields to the caller, then resetting the config.
        """
        try:
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

    def exec_args(
        self,
        *args: t.Any,
        command: str | None = None,
        env: dict[str, t.Any] | None = None,
    ) -> list[str]:
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

    def find_command(self, name: str) -> Command:
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

    def _load_manifest(self) -> dict[str, t.Any] | None:
        """Load or compile the manifest if not already loaded.

        Returns:
            The manifest data, or None if loading failed.
        """
        if not self._manifest_loaded:
            self._manifest_data = load_or_compile_manifest(self.project)
            self._manifest_loaded = True
        return self._manifest_data

    def env(self) -> dict[str, t.Any]:
        """Environment variable mapping.

        Returns:
            Dictionary of environment variables.
        """
        # Try to load manifest for env var data
        manifest_data = self._load_manifest()

        with self.project.settings.feature_flag(
            FeatureFlags.STRICT_ENV_VAR_MODE,
            raise_error=False,
        ) as strict_env_var_mode:
            # Get env var sources - either from manifest or settings service
            if manifest_data:
                # The manifest already contains merged values for the current
                # environment. For env vars, we just need project and plugin values
                project_env = manifest_data.get("env", {})

                # Find plugin env in the manifest
                plugin_env = {}
                plugin_type_key = self.plugin.type.value
                plugins_of_type = manifest_data.get("plugins", {}).get(
                    plugin_type_key, []
                )
                for p in plugins_of_type:
                    if p.get("name") == self.plugin.name:
                        plugin_env = p.get("env", {})
                        break

                # The manifest has already merged environment-specific values,
                # so we don't need to look for them separately
                environment_env = {}
                env_plugin_env = {}
            else:
                # Fall back to settings service
                project_env = self.project.settings.env
                environment_env = (
                    self.settings_service.project.environment.env
                    if self.settings_service.project.environment
                    else {}
                )
                plugin_env = self.settings_service.plugin.env
                env_plugin_env = (
                    self.settings_service.environment_plugin_config.env
                    if self.settings_service.environment_plugin_config
                    else {}
                )

            # Now apply the same expansion logic regardless of source
            # When using manifest, we need to expand in the right order
            # to match the original behavior

            # Start with os.environ as the base
            base_env = os.environ.copy()

            # If using manifest, plugin env already includes all merged values
            # Just expand it with the current environment
            if manifest_data:
                # First expand project env with os.environ
                # This handles cases like ${STACKED}23 -> 123
                expanded_project_env = expand_env_vars(
                    project_env,
                    base_env,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

                # Add dotenv vars
                expanded_project_env.update(
                    expand_env_vars(
                        self.settings_service.project.dotenv_env,
                        base_env,
                        if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                    )
                )

                # Now expand plugin env with the expanded project env
                # This handles cases like ${STACKED}45 -> 12345 (using STACKED=123)
                expanded_plugin_env = expand_env_vars(
                    plugin_env,
                    {**base_env, **expanded_project_env},
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

                expanded_env = {
                    **expanded_project_env,
                    **expanded_plugin_env,
                }
            else:
                # Original expansion logic for non-manifest path
                # First expand project env
                expanded_env = dict(
                    expand_env_vars(
                        project_env,
                        base_env,
                        if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                    )
                )

                # Expand dotenv
                expanded_project_env = {
                    **expanded_env,
                    **expand_env_vars(
                        self.settings_service.project.dotenv_env,
                        base_env,
                        if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                    ),
                }

                # Expand active env w/ expanded root env
                expanded_active_env = expand_env_vars(
                    environment_env,
                    expanded_project_env,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

                # Expand root plugin env w/ expanded active env
                expanded_root_plugin_env = expand_env_vars(
                    plugin_env,
                    expanded_active_env,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

                # Expand active env plugin env w/ expanded root plugin env
                expanded_plugin_env = expand_env_vars(
                    env_plugin_env,
                    expanded_root_plugin_env,
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

                expanded_env = {
                    **expanded_project_env,
                    **expanded_active_env,
                    **expanded_plugin_env,
                }

            # When using manifest, expanded_env already contains all the env vars
            # so we should prioritize it over settings_service.env
            if manifest_data:
                env = {
                    **self.plugin.exec_env(self),
                    **self.project.dotenv_env,
                    **self.settings_service.env,
                    **self.plugin_config_env,
                    **expanded_env,  # Put expanded_env last so it takes precedence
                    **self.tracker.env,
                }
            else:
                # Original order for non-manifest path
                env = {
                    **self.plugin.exec_env(self),
                    **expanded_env,
                    **self.project.dotenv_env,
                    **self.settings_service.env,
                    **self.plugin_config_env,
                    **self.tracker.env,
                }

        # Ensure Meltano venv is not inherited
        env.pop("VIRTUAL_ENV", None)
        env.pop("PYTHONPATH", None)
        if self.venv_service:
            # Switch to plugin-specific venv
            venv = VirtualEnv(
                self.project.venvs_dir(
                    self.plugin.type,
                    self.plugin.name,
                    make_dirs=False,
                ),
            )
            venv_dir = str(venv.bin_dir)
            env["VIRTUAL_ENV"] = str(venv.root)
            env["PATH"] = os.pathsep.join([venv_dir, env["PATH"]])

        return env

    def Popen_options(self) -> dict[str, t.Any]:  # noqa: N802
        """Get options for subprocess.Popen.

        Returns:
            Mapping of subprocess options.
        """
        return {}

    @asynccontextmanager
    async def _invoke(  # (overly complex annotation)
        self,
        *args: str,
        require_preparation: bool = True,
        env: dict[str, t.Any] | None = None,
        command: str | None = None,
        **kwargs: t.Any,
    ) -> AsyncGenerator[tuple[list[str], dict[str, t.Any], dict[str, t.Any]], None]:
        """Invoke a command.

        Args:
            args: Positional arguments.
            require_preparation: Whether to fail if the invoker is not "prepared", i.e.
                if the plugin config has not been loaded.
            env: Environment variables to pass to the subprocess.
            command: Plugin command name, if any.
            kwargs: Keyword arguments to pass to the subprocess constructor.

        Yields:
            Tuple of command arguments, subprocess call options, and environment dict.

        Raises:
            InvokerNotPreparedError: If the plugin config has not been loaded and
                `require_preparation` is True.
            ExecutableNotFoundError: If the executable is not found.
        """
        env = env or {}

        if require_preparation and not self._prepared:
            raise InvokerNotPreparedError

        async with self.plugin.trigger_hooks("invoke", self, args):
            popen_options = {**self.Popen_options(), **kwargs}
            popen_env = {**self.env(), **env}
            popen_args = self.exec_args(*args, command=command, env=popen_env)
            logger.debug(f"Invoking: {popen_args}")  # noqa: G004

            try:
                yield (popen_args, popen_options, popen_env)
            except FileNotFoundError as err:
                raise ExecutableNotFoundError(
                    self.plugin,
                    self.plugin.executable,
                ) from err

    async def invoke_async(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> asyncio.subprocess.Process:
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

    async def invoke_docker(
        self,
        plugin_command: str,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> int:
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
            raise ValueError("Command is missing a container spec")  # noqa: EM101

        spec = command_config.container_spec
        service = ContainerService()

        logger.debug("Running containerized command", command=plugin_command)
        async with self._invoke(*args, **kwargs) as (_proc_args, _, proc_env):
            plugin_name = self.plugin.name
            random_id = uuid7()
            name = f"meltano-{plugin_name}--{plugin_command}-{random_id}"

            info = await service.run_container(spec, name, env=proc_env)

        return info["State"]["ExitCode"]

    async def dump(self, file_id: str) -> str:
        """Dump a plugin file by ID.

        Args:
            file_id: Dump this file identifier.

        Returns:
            File contents.

        Raises:
            __cause__: If file is not found.
        """
        try:
            if file_id != "config":
                async with self._invoke():
                    return self.files[file_id].read_text()

            return self.files[file_id].read_text()
        except ExecutableNotFoundError as err:  # . Allow "useless" except.
            # Unwrap FileNotFoundError
            raise err.__cause__ from None  # type: ignore[misc]

    def add_output_handler(self, src: str, handler: SubprocessOutputWriter) -> None:
        """Append an output handler for a given stdio stream.

        Args:
            src: stdio source you'd like to subscribe, likely either 'stdout'
                or 'stderr'
            handler: A `StreamWriter` or object matching the
                `utils.SubprocessOutputWriter` protocol
        """
        if self.output_handlers:
            self.output_handlers[src].append(handler)
        else:
            self.output_handlers = {src: [handler]}
