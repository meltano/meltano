"""Install plugins into the project, using pip in separate virtual environments by default."""
import asyncio
import functools
import logging
import sys
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, Callable, Iterable, Tuple

from meltano.core.plugin.project_plugin import ProjectPlugin

from .compiler.project_compiler import ProjectCompiler
from .error import AsyncSubprocessError, PluginInstallError, PluginInstallWarning
from .plugin import PluginType
from .project import Project
from .project_plugins_service import ProjectPluginsService
from .utils import noop, run_async
from .venv_service import VenvService

logger = logging.getLogger(__name__)


class PluginInstallReason(str, Enum):
    """Plugin install reason enum."""

    ADD = "add"
    INSTALL = "install"
    UPGRADE = "upgrade"


class PluginInstallStatus(Enum):
    """The status of the process of installing a plugin."""

    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"
    WARNING = "warning"


class PluginInstallState:
    """A message reporting the progress of installing a plugin."""

    def __init__(
        self,
        plugin: ProjectPlugin,
        reason: PluginInstallReason,
        status: PluginInstallStatus,
        message: str = None,
        details: str = None,
    ):
        """Initialize PluginInstallState instance.

        Args:
            plugin: Plugin related to this install state.
            reason: Reason for plugin install.
            status: Status of plugin install.
            message: Formatted install state message.
            details: Extra details relating to install (including error details if failed).
        """
        # TODO: use dataclasses.dataclass for this when 3.6 support is dropped
        self.plugin = plugin
        self.reason = reason
        self.status = status
        self.message = message
        self.details = details

    @property
    def successful(self):
        """Plugin install success status.

        Returns:
            'True' if plugin install successful.
        """
        return self.status in {PluginInstallStatus.SUCCESS, PluginInstallStatus.SKIPPED}

    @property
    def skipped(self):
        """Plugin install skipped status.

        Returns:
            'True' if the installation was skipped / not needed.
        """
        return self.status == PluginInstallStatus.SKIPPED

    @property  # noqa: WPS212  # Too many return statements
    def verb(self):
        """Verb form of status.

        Returns:
            Verb form of status.
        """
        if self.status is PluginInstallStatus.RUNNING:
            if self.reason is PluginInstallReason.UPGRADE:
                return "Updating"
            return "Installing"

        if self.status is PluginInstallStatus.SUCCESS:
            if self.reason is PluginInstallReason.UPGRADE:
                return "Updated"

            return "Installed"

        if self.status is PluginInstallStatus.SKIPPED:
            return "Skipped installing"

        return "Errored"


def installer_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    """Installer Factory.

    Args:
        project: Meltano Project.
        plugin: Plugin to be installed.
        args: Positional arguments to instantiate installer with.
        kwargs: Keyword arguments to instantiate installer with.

    Returns:
        An instantiated plugin installer for the given plugin.
    """
    installer_class = PipPluginInstaller
    try:
        installer_class = plugin.installer_class
    except AttributeError:
        pass

    return installer_class(project, plugin, *args, **kwargs)


def with_semaphore(func):
    """Gate access to the method using its class's semaphore.

    Args:
        func: Function to wrap.

    Returns:
        Wrapped function.
    """

    @functools.wraps(func)  # noqa: WPS430
    async def wrapper(self, *args, **kwargs):  # noqa: WPS430
        async with self.semaphore:
            return await func(self, *args, **kwargs)

    return wrapper


class PluginInstallService:
    """Plugin install service."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
        status_cb: Callable[[PluginInstallState], Any] = noop,
        parallelism=None,
        clean=False,
    ):
        """Initialize new PluginInstallService instance.

        Args:
            project: Meltano Project.
            plugins_service: (optional) Project plugins service to use.
            status_cb: (optional) Status call-back function.
            parallelism: (optional) Number of parallel installation processes to use.
            clean: (optional) Clean install flag.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.status_cb = status_cb

        if parallelism is None:
            parallelism = cpu_count()
        if parallelism < 1:
            parallelism = sys.maxsize  # unbounded
        self.semaphore = asyncio.Semaphore(parallelism)
        self.clean = clean

    @staticmethod
    def remove_duplicates(
        plugins: Iterable[ProjectPlugin], reason: PluginInstallReason
    ):
        """Deduplicate list of plugins, keeping the last occurrences.

        Trying to install multiple plugins into the same venv via `run_async` will fail
        due to a race condition between the duplicate installs. This is particularly
        problematic if `clean` is set as one async `clean` operation causes the other
        install to fail.

        Args:
            plugins: An iterable containing plugins to dedupe.
            reason: Plugins install reason.

        Returns:
            A tuple containing a list of PluginInstallState instance (for skipped plugins)
            and a deduplicated list of plugins to install.
        """
        states = []
        seen_venvs = set()
        deduped_plugins = []
        for plugin in list(plugins):
            if (plugin.type, plugin.venv_name) not in seen_venvs:
                deduped_plugins.append(plugin)
                seen_venvs.add((plugin.type, plugin.venv_name))
            else:
                state = PluginInstallState(
                    plugin=plugin,
                    reason=reason,
                    status=PluginInstallStatus.SKIPPED,
                    message=(
                        f"Plugin '{plugin.name}' does not require installation: "
                        + "reusing parent virtualenv"
                    ),
                )
                states.append(state)
        return states, deduped_plugins

    def install_all_plugins(
        self, reason=PluginInstallReason.INSTALL
    ) -> Tuple[PluginInstallState]:
        """
        Install all the plugins for the project.

        Blocks until all plugins are installed.

        Args:
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        return self.install_plugins(self.plugins_service.plugins(), reason=reason)

    def install_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> Tuple[PluginInstallState]:
        """
        Install all the provided plugins.

        Blocks until all plugins are installed.

        Args:
            plugins: ProjectPlugin instances to install.
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        states, new_plugins = self.remove_duplicates(plugins=plugins, reason=reason)
        for state in states:
            self.status_cb(state)
        states.extend(run_async(self.install_plugins_async(new_plugins, reason=reason)))
        return states

    async def install_plugins_async(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> Tuple[PluginInstallState]:
        """Install all the provided plugins.

        Args:
            plugins: ProjectPlugin instances to install.
            reason: Plugin install reason.

        Returns:
            Install state of installed plugins.
        """
        results = await asyncio.gather(
            *[
                self.install_plugin_async(plugin, reason, compile_models=False)
                for plugin in plugins
            ]
        )
        for plugin in plugins:
            if plugin.type is PluginType.MODELS:
                self.compile_models()
                break

        return results

    def install_plugin(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
        compile_models=True,
    ) -> PluginInstallState:
        """
        Install a plugin.

        Blocks until the plugin is installed.

        Args:
            plugin: ProjectPlugin to install.
            reason: Install reason.
            compile_models: (optional) Compile .m50 models flag.

        Returns:
            PluginInstallState state instance.
        """
        return run_async(
            self.install_plugin_async(
                plugin,
                reason=reason,
                compile_models=compile_models,
            )
        )

    @with_semaphore
    async def install_plugin_async(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
        compile_models=True,
    ) -> PluginInstallState:
        """Install a plugin asynchronously.

        Args:
            plugin: ProjectPlugin to install.
            reason: Install reason.
            compile_models: (optional) Compile .m50 models flag.

        Returns:
            PluginInstallState state instance.
        """
        self.status_cb(
            PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.RUNNING,
            )
        )

        if not plugin.is_installable() or self._is_mapping(plugin):
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.SKIPPED,
                message=f"Plugin '{plugin.name}' does not require installation",
            )
            self.status_cb(state)
            return state

        try:
            async with plugin.trigger_hooks("install", self, plugin, reason):
                await installer_factory(self.project, plugin).install(
                    reason, self.clean
                )
                state = PluginInstallState(
                    plugin=plugin, reason=reason, status=PluginInstallStatus.SUCCESS
                )
                if compile_models and plugin.type is PluginType.MODELS:
                    self.compile_models()
                self.status_cb(state)
                return state

        except PluginInstallError as err:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=str(err),
            )
            self.status_cb(state)
            return state

        except PluginInstallWarning as warn:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.WARNING,
                message=str(warn),
            )
            self.status_cb(state)
            return state

        except AsyncSubprocessError as err:
            state = PluginInstallState(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=(
                    f"{plugin.type.descriptor} '{plugin.name}' "
                    + f"could not be installed: {err}"
                ).capitalize(),
                details=await err.stderr,
            )
            self.status_cb(state)
            return state

    def compile_models(self):
        """Compile .m50 models."""
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception as exp:  # noqa: S110
            logger.debug("Failed to compile models: %s", exp)  # noqa: WPS323

    @staticmethod
    def _is_mapping(plugin: ProjectPlugin) -> bool:
        """Check if a plugin is a mapping, as mappings are not installed.

        Mappings are PluginType.MAPPERS with extra attribute of `_mapping` which will indicate
        that this instance of the plugin is actually a mapping - and should not be installed.

        Args:
            plugin: ProjectPlugin to evaluate.

        Returns:
            A boolean determining if the given plugin is a mapping (of type PluginType.MAPPERS).
        """
        return plugin.type == PluginType.MAPPERS and plugin.extra_config.get("_mapping")


class PipPluginInstaller:
    """Plugin installer for pip-based plugins."""

    def __init__(
        self,
        project,
        plugin: ProjectPlugin,
        venv_service: VenvService = None,
    ):
        """Initialize PipPluginInstaller instance.

        Args:
            project: Meltano Project.
            plugin: ProjectPlugin to install.
            venv_service: (optional) VenvService instance to use when installing.
        """
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(
            project,
            namespace=self.plugin.type,
            name=self.plugin.venv_name,
        )

    async def install(self, reason, clean):
        """Install the plugin into the virtual environment using pip.

        Args:
            reason: Install reason.
            clean: Flag to clean install.

        Returns:
            None.
        """
        return await self.venv_service.install(
            self.plugin.formatted_pip_url, clean=clean
        )
