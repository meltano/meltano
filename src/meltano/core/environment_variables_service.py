"""Env Vars Service."""
import os

from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project_settings_service import ProjectSettingsService


class EnvVarsService:
    """Service for retrieving and collating environment variables."""

    @property
    def env(self) -> dict:
        """Terminal environment variables.

        Returns:
            A dict of env vars from the terminal.
        """
        return {**os.environ}


class ProjectEnvVarsService(EnvVarsService):
    """Project Environment Variables Service.

    Responsible for handling environment variables at the Project level.
    """

    def __init__(
        self,
        project_settings_service: ProjectSettingsService,
    ):
        """Initialise new ProjectEnvVarsService instance.

        Args:
            project_settings_service: A ProjectSettingsService instance to use.
        """
        super().__init__()
        self.project_settings_service = project_settings_service

    @property
    def env(self) -> dict:
        """Project level environment variables.

        Returns:
            A dict of env vars at the Project level.
        """
        return {
            **super().env,  # terminal environment variables
            **self.project_settings_service.project.env,  # static, project-level envs (e.g. MELTANO_ENVIRONMENT)
            **self.project_settings_service.project.dotenv_env,  # env vars stored in the dotenv file
            **self.project_settings_service.env,  # env vars stored in the base `meltano.yml` `env:` key
            **self.project_settings_service.environment_env,  # env vars from the curent meltano environments' `env:` key
        }


class PluginEnvVarsService(EnvVarsService):
    """Plugin Environment Variables Service.

    Responsible for handling environment variables at the Plugin level.
    """

    def __init__(self, plugin_settings_service: PluginSettingsService):
        """Initialise new PluginEnvVarsService instance.

        Args:
            plugin_settings_service: A PluginSettingsService instance to use.
        """
        super().__init__()
        self.plugin_settings_service = plugin_settings_service
        self.plugin = self.plugin_settings_service.plugin
        self.project_settings_service = (
            self.plugin_settings_service.project_settings_service
        )
        self.project_env_vars_service = ProjectEnvVarsService(
            project_settings_service=self.project_settings_service
        )

    @property
    def env(self) -> dict:
        """Plugin level environment variables.

        Returns:
            A dict of env vars at the plugin level.
        """
        return {
            **self.project_env_vars_service.env,  # project level environment variables
            **self.plugin_settings_service.as_env(),  # generated plugin settings as env vars (e.g. TAP_GITLAB_API_URL)
            **self.plugin_settings_service.plugin.info_env,  # generated generic plugin settings as env vars (e.g. MELTANO_EXTRACT_NAME)
            **self.plugin_settings_service.plugin.env,  # env vars stored under the `env:` key of the plugin definition
        }
