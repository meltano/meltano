import logging

from .compiler.project_compiler import ProjectCompiler
from .plugin_discovery_service import PluginDiscoveryService
from .project_add_service import ProjectAddService
from .config_service import ConfigService
from .venv_service import VenvService
from .utils import noop
from .plugin import PluginType, PluginInstall, Plugin, PluginRef
from .project import Project
from .error import (
    PluginInstallError,
    PluginInstallWarning,
    SubprocessError,
    PluginNotInstallable,
)


def installer_factory(project, plugin, *args, **kwargs):
    cls = PipPluginInstaller

    if hasattr(plugin.__class__, "__installer_cls__"):
        cls = plugin.__class__.__installer_cls__

    return cls(project, plugin, *args, **kwargs)


class PluginInstallService:
    def __init__(self, project: Project, config_service: ConfigService = None):
        self.project = project
        self.config_service = config_service or ConfigService(project)

    def install_all_plugins(self, status_cb=noop):
        # TODO: config service returns PluginInstall, not Plugin
        return self.install_plugins(self.config_service.plugins())

    def install_plugins(self, plugins, status_cb=noop):
        errors = []
        installed = []
        has_model = False

        for plugin in plugins:
            status = {"plugin": plugin, "status": "running"}
            status_cb(status)

            try:
                self.install_plugin(plugin, compile_models=False)

                if plugin.type is PluginType.MODELS:
                    has_model = True

                status["status"] = "success"
                installed.append(status)
            except PluginInstallError as err:
                status["status"] = "error"
                status["message"] = str(err)
                status["details"] = err.process.stderr
                errors.append(status)
            except PluginInstallWarning as warn:
                status["status"] = "warning"
                status["message"] = str(warn)
                errors.append(status)
            except PluginNotInstallable as info:
                # let's totally ignore these plugins
                pass

            status_cb(status)

        if has_model:
            self.compile_models()

        return {"errors": errors, "installed": installed}

    def install_plugin(self, plugin: PluginInstall, compile_models=True):
        if not plugin.is_installable():
            raise PluginNotInstallable()

        with plugin.trigger_hooks("install", self.project):
            run = installer_factory(self.project, plugin).install()

            if compile_models and plugin.type is PluginType.MODELS:
                self.compile_models()

            return run

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass


class PipPluginInstaller:
    def __init__(self, project, plugin: PluginRef, venv_service: VenvService = None):
        self.plugin = plugin
        self.venv_service = venv_service or VenvService(project)

    def install(self):
        try:
            self.venv_service.create(namespace=self.plugin.type, name=self.plugin.name)
            return self.venv_service.install(
                namespace=self.plugin.type,
                name=self.plugin.name,
                pip_url=self.plugin.pip_url,
            )
        except SubprocessError as err:
            raise PluginInstallError(
                f"{self.plugin.name} has an installation issue. {err}", err.process
            )
