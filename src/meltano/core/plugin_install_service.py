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


class PluginInstallService:
    def __init__(
        self,
        project: Project,
        venv_service: VenvService = None,
        config_service: ConfigService = None,
    ):
        self.project = project
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or ConfigService(project)

    def create_venv(self, plugin: PluginRef):
        return self.venv_service.create(namespace=plugin.type, name=plugin.name)

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

        try:
            with plugin.trigger_hooks("install", self.project):
                self.create_venv(plugin)
                run = self.venv_service.install(
                    namespace=plugin.type, name=plugin.name, pip_url=plugin.pip_url
                )

                if compile_models and plugin.type is PluginType.MODELS:
                    self.compile_models()

                return run
        except SubprocessError as err:
            raise PluginInstallError(
                f"{plugin.name} has an installation issue. {err}", err.process
            )

    def compile_models(self):
        compiler = ProjectCompiler(self.project)
        try:
            compiler.compile()
        except Exception:
            pass
