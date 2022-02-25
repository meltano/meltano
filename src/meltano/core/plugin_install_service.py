"""Install plugins into the project, using pip in separate virtual environments by default."""
import asyncio
import functools
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


class PluginInstallReason(str, Enum):
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
        # TODO: use dataclasses.dataclass for this when 3.6 support is dropped
        self.plugin = plugin
        self.reason = reason
        self.status = status
        self.message = message
        self.details = details

    @property
    def successful(self):
        """If the installation completed without error."""
        return self.status in {PluginInstallStatus.SUCCESS, PluginInstallStatus.SKIPPED}

    @property
    def skipped(self):
        """Return 'True' if the installation was skipped / not needed."""
        return self.status == PluginInstallStatus.SKIPPED

    @property  # noqa: WPS212  # Too many return statements
    def verb(self):
        """Verb form of status."""
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
    cls = PipPluginInstaller

    if hasattr(plugin, "installer_class"):
        cls = plugin.installer_class

    return cls(project, plugin, *args, **kwargs)


def with_semaphore(func):
    """Gate access to the method using its class's semaphore."""

    @functools.wraps(func)  # noqa: WPS430
    async def wrapper(self, *args, **kwargs):  # noqa: WPS430
        async with self.semaphore:
            return await func(self, *args, **kwargs)

    return wrapper


class PluginInstallService:
    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
        status_cb: Callable[[PluginInstallState], Any] = noop,
        parallelism=None,
        clean=False,
    ):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.status_cb = status_cb

        if parallelism is None:
            parallelism = cpu_count()
        if parallelism < 1:
            parallelism = sys.maxsize  # unbounded
        self.semaphore = asyncio.Semaphore(parallelism)
        self.clean = clean

    def install_all_plugins(
        self, reason=PluginInstallReason.INSTALL
    ) -> Tuple[PluginInstallState]:
        """
        Install all the plugins for the project.

        Blocks until all plugins are installed.
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
        """
        return run_async(self.install_plugins_async(plugins, reason=reason))

    async def install_plugins_async(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> Tuple[PluginInstallState]:
        """Install all the provided plugins."""
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
        """Install a plugin."""
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
                message=f"{plugin.type.descriptor} '{plugin.name}' could not be installed: {err}".capitalize(),
                details=await err.stderr,
            )
            self.status_cb(state)
            return state

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass

    @staticmethod
    def _is_mapping(plugin: ProjectPlugin) -> bool:
        """Check if a plugin is a mapping as mappings are not installed.

        Mappings are PluginType.MAPPERS with extra attribute of `_mapping` which will indicate
        that this instance of the plugin is actually a mapping - and should not be installed.
        """
        return plugin.type == PluginType.MAPPERS and plugin.extra_config.get("_mapping")


class PipPluginInstaller:
    def __init__(
        self,
        project,
        plugin: ProjectPlugin,
        venv_service: VenvService = None,
    ):
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(
            project,
            namespace=self.plugin.type,
            name=self.plugin.name,
        )

    async def install(self, reason, clean):
        """Install the plugin into the virtual environment using pip."""
        return await self.venv_service.install(
            self.plugin.formatted_pip_url, clean=clean
        )
