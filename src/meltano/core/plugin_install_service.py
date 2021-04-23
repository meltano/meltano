"""Install plugins into the project, using pip in separate virtual environments by default."""
import asyncio
import functools
import logging
import sys
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, Callable, Iterable

from meltano.core.plugin.project_plugin import ProjectPlugin

from .compiler.project_compiler import ProjectCompiler
from .error import PluginInstallError, PluginInstallWarning, SubprocessError
from .plugin import PluginType
from .plugin_discovery_service import PluginDiscoveryService
from .project import Project
from .project_add_service import ProjectAddService
from .project_plugins_service import ProjectPluginsService
from .utils import noop, run_async
from .venv_service import VenvService


class PluginInstallReason(str, Enum):
    ADD = "add"
    INSTALL = "install"
    UPGRADE = "upgrade"


class PluginInstallStatus(Enum):
    """The status of installing a plugin."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class PluginInstallUpdate:
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
        return self.status is PluginInstallStatus.SUCCESS

    @property
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

        return "Errored"


def installer_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    cls = PipPluginInstaller

    if hasattr(plugin, "installer_class"):
        cls = plugin.installer_class

    return cls(project, plugin, *args, **kwargs)


def with_semaphore(func):
    """Gate acess to the method using its class's semaphore."""

    @functools.wraps(func) # noqa: WPS430
    async def wrapper(self, *args, **kwargs):  # noqa: WPS430
        async with self.semaphore:
            return await func(self, *args, **kwargs)

    return wrapper


class PluginInstallService:
    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
        status_cb: Callable[[PluginInstallUpdate], Any] = noop,
        parallelism=None,
    ):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.status_cb = status_cb

        if parallelism is None:
            parallelism = cpu_count()
        if parallelism < 1:
            parallelism = sys.maxsize  # unbounded
        self.semaphore = asyncio.Semaphore(parallelism)

    def install_all_plugins(
        self, reason=PluginInstallReason.INSTALL
    ) -> [PluginInstallUpdate]:
        """
        Install all the plugins for the project.

        Blocks until all plugins are installed.
        """
        return self.install_plugins(self.plugins_service.plugins(), reason=reason)

    def install_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> [PluginInstallUpdate]:
        """
        Install all the provided plugins.

        Blocks until all plugins are installed.
        """
        return run_async(self.install_plugins_async(plugins, reason=reason))

    async def install_plugins_async(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
    ) -> [PluginInstallUpdate]:
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
    ) -> PluginInstallUpdate:
        """
        Install a plugin.

        Blocks until the plugin is installed.
        """
        return run_async(
            self.install_plugin_async(
                plugin, reason=reason, compile_models=compile_models
            )
        )

    @with_semaphore
    async def install_plugin_async(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
        compile_models=True,
    ) -> PluginInstallUpdate:
        """Install a plugin."""
        self.status_cb(
            PluginInstallUpdate(
                plugin=plugin, reason=reason, status=PluginInstallStatus.RUNNING
            )
        )
        if not plugin.is_installable():
            status = PluginInstallUpdate(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.WARNING,
                message=f"Plugin '{plugin.name}' is not installable",
            )
            self.status_cb(status)
            return status

        try:
            with plugin.trigger_hooks("install", self, plugin, reason):
                await installer_factory(self.project, plugin).install(reason)
                status = PluginInstallUpdate(
                    plugin=plugin, reason=reason, status=PluginInstallStatus.SUCCESS
                )
                if compile_models and plugin.type is PluginType.MODELS:
                    self.compile_models()
                self.status_cb(status)
                return status

        except PluginInstallError as err:
            status = PluginInstallUpdate(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=str(err),
                details=err.stderr,
            )
            self.status_cb(status)
            return status

        except PluginInstallWarning as warn:
            status = PluginInstallUpdate(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.WARNING,
                message=str(warn),
            )
            self.status_cb(status)
            return status

        except SubprocessError as err:
            status = PluginInstallUpdate(
                plugin=plugin,
                reason=reason,
                status=PluginInstallStatus.ERROR,
                message=f"{plugin.type.descriptor} '{plugin.name}' could not be installed: {err}".capitalize(),
                details=err.stderr,
            )
            self.status_cb(status)
            return status

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass


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

    async def install(self, reason):
        """Install the plugin into the virtual environment using pip."""
        return await self.venv_service.clean_install(self.plugin.pip_url)
