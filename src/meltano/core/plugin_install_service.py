import logging
from typing import Iterable
from enum import Enum

from .compiler.project_compiler import ProjectCompiler
from .plugin_discovery_service import PluginDiscoveryService
from .project_add_service import ProjectAddService
from .config_service import ConfigService
from .venv_service import VenvService
from .utils import noop
from .plugin import PluginType, ProjectPlugin, PluginDefinition, PluginRef
from .project import Project
from .error import (
    PluginInstallError,
    PluginInstallWarning,
    SubprocessError,
    PluginNotInstallable,
)


class PluginInstallReason(str, Enum):
    ADD = "add"
    INSTALL = "install"
    UPGRADE = "upgrade"


def installer_factory(project, plugin: ProjectPlugin, *args, **kwargs):
    cls = PipPluginInstaller

    if hasattr(plugin.__class__, "__installer_cls__"):
        cls = plugin.__class__.__installer_cls__

    return cls(project, plugin, *args, **kwargs)


class PluginInstallService:
    def __init__(self, project: Project, config_service: ConfigService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)

    def install_all_plugins(self, reason=PluginInstallReason.INSTALL, status_cb=noop):
        return self.install_plugins(
            self.config_service.plugins(), reason=reason, status_cb=status_cb
        )

    def install_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        reason=PluginInstallReason.INSTALL,
        status_cb=noop,
    ):
        errors = []
        installed = []
        has_model = False

        for plugin in plugins:
            status = {"plugin": plugin, "status": "running"}
            status_cb(status, reason)

            try:
                self.install_plugin(plugin, compile_models=False, reason=reason)

                if plugin.type is PluginType.MODELS:
                    has_model = True

                status["status"] = "success"
                installed.append(status)
            except PluginInstallError as err:
                status["status"] = "error"
                status["message"] = str(err)
                status["details"] = err.stderr
                errors.append(status)
            except PluginInstallWarning as warn:
                status["status"] = "warning"
                status["message"] = str(warn)
                errors.append(status)
            except PluginNotInstallable as info:
                # let's totally ignore these plugins
                pass

            status_cb(status, reason)

        if has_model:
            self.compile_models()

        return {"errors": errors, "installed": installed}

    def install_plugin(
        self,
        plugin: ProjectPlugin,
        reason=PluginInstallReason.INSTALL,
        compile_models=True,
    ):
        if not plugin.is_installable():
            raise PluginNotInstallable()

        try:
            with plugin.trigger_hooks("install", self.project, reason):
                run = installer_factory(self.project, plugin).install(reason)

                if compile_models and plugin.type is PluginType.MODELS:
                    self.compile_models()

                return run
        except PluginInstallError:
            raise
        except SubprocessError as err:
            raise PluginInstallError(
                f"{plugin.type.descriptor} '{plugin.name}' could not be installed: {err}".capitalize(),
                err.process,
            ) from err

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass


class PipPluginInstaller:
    def __init__(
        self, project, plugin: ProjectPlugin, venv_service: VenvService = None
    ):
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)

    def install(self, reason):
        self.venv_service.clean(namespace=self.plugin.type, name=self.plugin.name)
        self.venv_service.create(namespace=self.plugin.type, name=self.plugin.name)
        return self.venv_service.install(
            namespace=self.plugin.type,
            name=self.plugin.name,
            pip_url=self.plugin.pip_url,
        )
