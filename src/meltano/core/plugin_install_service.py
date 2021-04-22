"""Install plugins into the project, using pip in separate virtual environments by default."""
import asyncio
import logging
from enum import Enum
from typing import Iterable

from meltano.core.plugin.project_plugin import ProjectPlugin

from .compiler.project_compiler import ProjectCompiler
from .error import (
    PluginInstallError,
    PluginInstallWarning,
    PluginNotInstallable,
    SubprocessError,
)
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


def installer_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    cls = PipPluginInstaller

    if hasattr(plugin, "installer_class"):
        cls = plugin.installer_class

    return cls(project, plugin, *args, **kwargs)


class PluginInstallService:
    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def install_all_plugins(self, reason=PluginInstallReason.INSTALL, status_cb=noop):
        return self.install_plugins(
            self.plugins_service.plugins(), reason=reason, status_cb=status_cb
        )

    def install_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
        status_cb=noop,
    ):
        """
        Install all the provided plugins.

        Blocks until all plugins are installed.
        """
        return run_async(self.install_plugins_async(plugins, reason, status_cb))

    async def install_plugins_async(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
        status_cb=noop,
    ):
        """Install all the provided plugins."""
        statuses = await asyncio.gather(
            *[
                self._install_with_status(plugin, reason, status_cb)
                for plugin in plugins
            ]
        )
        for plugin in plugins:
            if plugin.type is PluginType.MODELS:
                self.compile_models()
                break

        return {
            "installed": [
                status for status in statuses if status["status"] == "success"
            ],
            "errors": [status for status in statuses if status["status"] != "success"],
        }

    def install_plugin(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
        compile_models=True,
    ):
        """
        Install a plugin.

        Blocks until the plugin is installed.
        """
        res = run_async(self.install_plugin_async(plugin, reason=reason))

        if compile_models and plugin.type is PluginType.MODELS:
            self.compile_models()

        return res

    async def install_plugin_async(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
    ):
        """Install a plugin."""
        if not plugin.is_installable():
            raise PluginNotInstallable()

        try:
            with plugin.trigger_hooks("install", self, plugin, reason):
                return await installer_factory(self.project, plugin).install(reason)

        except PluginInstallError:
            raise
        except SubprocessError as err:
            raise PluginInstallError(
                f"{plugin.type.descriptor} '{plugin.name}' could not be installed: {err}".capitalize(),
                err.process,
                stderr=err.stderr,
            ) from err

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass

    async def _install_with_status(self, plugin, reason, status_cb=noop):
        status = {"plugin": plugin, "status": "running"}
        status_cb(status, reason)
        try:
            await self.install_plugin_async(plugin, reason=reason)

            status["status"] = "success"
        except PluginInstallError as err:
            status["status"] = "error"
            status["message"] = str(err)
            status["details"] = err.stderr
        except PluginInstallWarning as warn:
            status["status"] = "warning"
            status["message"] = str(warn)
        except PluginNotInstallable as info:
            # let's totally ignore these plugins
            pass

        status_cb(status, reason)
        return status


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
