"""Project Settings Service."""

from __future__ import annotations

import json

import structlog
from dotenv import dotenv_values

from meltano.core.project import ProjectReadonly
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_service import SettingsService, SettingValueStore
from meltano.core.utils import nest_object

from .config_service import ConfigService

logger = structlog.get_logger(__name__)

UI_CFG_SETTINGS = {
    "ui.server_name": "SERVER_NAME",
    "ui.secret_key": "SECRET_KEY",
    "ui.password_salt": "SECURITY_PASSWORD_SALT",
}


class ProjectSettingsService(SettingsService):
    """Project Settings Service."""

    config_override = {}
    supports_environments = False

    def __init__(self, *args, config_service: ConfigService = None, **kwargs):
        """Instantiate ProjectSettingsService instance.

        Args:
            args: Positional arguments to pass to the superclass.
            config_service: Project configuration service instance.
            kwargs: Keyword arguments to pass to the superclass.
        """
        super().__init__(*args, **kwargs)

        self.config_service = config_service or ConfigService(self.project)

        self.env_override = {
            # terminal environment variables already present from SettingService.env
            **self.project.env,  # static, project-level envs (e.g. MELTANO_ENVIRONMENT)
            **self.project.meltano.env,  # env vars stored in the base `meltano.yml` `env:` key
            **self.env_override,  # overrides
        }

        self.config_override = {  # noqa: WPS601
            **self.__class__.config_override,
            **self.config_override,
        }

        try:
            self.ensure_project_id()
        except ProjectReadonly:
            logger.debug(
                "Cannot update `project_id` in `meltano.yml`: project is read-only."
            )

    def ensure_project_id(self) -> None:
        """Ensure `project_id` is configured properly.

        Every `meltano.yml` file should contain the `project_id` key-value pair. It should be
        present in the top-level config, rather than in any environment-level configs.

        If it is not present, it will be restored from `analytics.json` if possible.
        """
        try:
            project_id = self.get("project_id")
        except OSError:
            project_id = None

        if project_id is None:
            try:
                with open(
                    self.project.meltano_dir() / "analytics.json"
                ) as analytics_json_file:
                    project_id = json.load(analytics_json_file)["project_id"]
            except (OSError, KeyError, json.JSONDecodeError) as err:
                logger.debug(
                    "Unable to restore 'project_id' from 'analytics.json'", err=err
                )
            else:
                self.set("project_id", project_id, store=SettingValueStore.MELTANO_YML)
                logger.debug("Restored 'project_id' from 'analytics.json'")

    @property
    def label(self) -> str:
        """Return label.

        Returns:
            Project label.
        """
        return "Meltano"

    @property
    def docs_url(self) -> str:
        """Return docs URL.

        Returns:
            URL for Meltano doc site.
        """
        return "https://docs.meltano.com/reference/settings"

    @property
    def db_namespace(self) -> str:
        """Return namespace for setting value records in system database.

        Returns:
            Namespace for setting value records in system database.
        """
        return "meltano"

    @property
    def setting_definitions(self) -> list[SettingDefinition]:
        """Return definitions of supported settings.

        Returns:
            A list of defined settings.
        """
        return self.config_service.settings

    @property
    def meltano_yml_config(self):
        """Return current configuration in `meltano.yml`.

        Returns:
            Current configuration in `meltano.yml`.
        """
        return self.config_service.current_config

    def update_meltano_yml_config(self, config):
        """Update configuration in `meltano.yml`.

        Args:
            config: Updated config.
        """
        self.config_service.update_config(config)

    def process_config(self, config) -> dict:
        """Process configuration dictionary for presentation in `meltano config meltano`.

        Args:
            config: Config to process.

        Returns:
            Processed configuration dictionary for presentation in `meltano config meltano`.
        """
        return nest_object(config)

    def get_with_metadata(self, name: str, *args, **kwargs):
        """Return setting value with metadata.

        Args:
            name: Name of setting to get.
            args: Positional arguments to pass to the superclass method.
            kwargs: Keyword arguments to pass to the superclass method.

        Returns:
            Setting value with metadata.
        """
        value, metadata = super().get_with_metadata(name, *args, **kwargs)
        source = metadata["source"]

        if source is SettingValueStore.DEFAULT:
            # Support legacy `ui.cfg` files generated by `meltano ui setup`
            ui_cfg_value = self.get_from_ui_cfg(name)
            if ui_cfg_value is not None:
                value = ui_cfg_value
                metadata["source"] = SettingValueStore.ENV
        return value, metadata

    def get_from_ui_cfg(self, name: str):
        """Return setting value from UI config.

        Args:
            name: Name of setting to get.

        Returns:
            Setting value from UI config.
        """
        try:
            key = UI_CFG_SETTINGS[name]
            config = dotenv_values(self.project.root_dir("ui.cfg"))
            value = config[key]

            # Since `ui.cfg` is technically a Python file, `'None'` means `None`
            if value == "None":
                value = None

            return value
        except KeyError:
            return None
