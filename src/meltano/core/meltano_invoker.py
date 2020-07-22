import subprocess

from .project import Project
from .project_settings_service import ProjectSettingsService, SettingValueStore


class MeltanoInvoker:
    def __init__(self, project, settings_service: ProjectSettingsService = None):
        self.project = project
        self.settings_service = settings_service or ProjectSettingsService(project)

    def invoke(self, args, command="meltano", env={}, **kwargs):
        base_env = self.settings_service.env
        overridden_config_env = self.settings_service.as_env(
            source=SettingValueStore.CONFIG_OVERRIDE
        )

        return subprocess.run(
            [command, *args], **kwargs, env={**base_env, **overridden_config_env, **env}
        )
