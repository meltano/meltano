from typing import Iterable, Dict, List

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import (
    SettingsService,
    SettingMissingError,
    SettingValueStore,
    REDACTED_VALUE,
)
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginRef, PluginType, Plugin, PluginInstall, Profile
from meltano.core.plugin.error import PluginMissingError


class PluginSettingsService(SettingsService):
    def __init__(
        self,
        project: Project,
        plugin: PluginRef,
        *args,
        plugin_discovery_service: PluginDiscoveryService = None,
        **kwargs,
    ):
        super().__init__(project, *args, **kwargs)

        self.plugin = plugin

        discovery_service = plugin_discovery_service or PluginDiscoveryService(
            self.project, config_service=self.config_service
        )
        self.plugin_def = discovery_service.find_plugin(
            self.plugin.type, self.plugin.name
        )
        self._plugin_install = None

        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.config_service
        )

        self.env_override = {
            **project_settings_service.env,
            **project_settings_service.as_env(),
            **self.env_override,
        }

    @property
    def plugin_install(self):
        if self._plugin_install is None:
            self._plugin_install = self.config_service.get_plugin(self.plugin)

        return self._plugin_install

    @property
    def _env_namespace(self):
        return self.plugin_def.namespace

    @property
    def _db_namespace(self):
        return self.plugin.qualified_name

    @property
    def _definitions(self):
        return self.plugin_def.settings

    @property
    def _meltano_yml_config(self):
        try:
            return self.plugin_install.current_config
        except PluginMissingError:
            return {}

    def _update_meltano_yml_config(self):
        self.config_service.update_plugin(self.plugin_install)

    def profile_with_config(self, profile: Profile, **kwargs):
        self.plugin_install.use_profile(profile)

        config_dict = {}
        config_metadata = {}

        config_with_metadata = self.config_with_metadata(**kwargs)
        for key, metadata in config_with_metadata.items():
            config_dict[key] = metadata.pop("value")

            metadata.pop("setting", None)

            config_metadata[key] = metadata

        return {
            **profile.canonical(),
            "config": config_dict,
            "config_metadata": config_metadata,
        }

    def profiles_with_config(self, **kwargs) -> List[Dict]:
        return [
            self.profile_with_config(profile, **kwargs)
            for profile in (Profile.DEFAULT, *self.plugin_install.profiles)
        ]
