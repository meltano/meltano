from .config_service import ConfigService
from .venv_service import VenvService
from .utils import noop
from .plugin import Plugin
from .project import Project
from .error import PluginInstallError, PluginInstallWarning, SubprocessError


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

    def create_venv(self, plugin: Plugin):
        return self.venv_service.create(namespace=plugin.type, name=plugin.name)

    def install_all_plugins(self, status_cb=noop):
        errors = []
        installed = []

        for plugin in self.config_service.plugins():
            status = {"plugin": plugin, "status": "running"}
            status_cb(status)

            try:
                self.create_venv(plugin)
                self.install_plugin(plugin)

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

            status_cb(status)

        return {"errors": errors, "installed": installed}

    def install_plugin(self, plugin: Plugin):
        try:
            with plugin.trigger_hooks("install", self.project):
                return self.venv_service.install(
                    namespace=plugin.type, name=plugin.name, pip_url=plugin.pip_url
                )
        except SubprocessError as err:
            raise PluginInstallError(str(err), err.process)
