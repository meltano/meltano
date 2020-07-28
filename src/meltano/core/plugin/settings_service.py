from copy import deepcopy
from typing import Iterable, Dict, List

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.setting_definition import SettingDefinition
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

        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            self.project, config_service=self.config_service
        )
        self._plugin_def = None
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
    def plugin_def(self):
        if self._plugin_def is None:
            self._plugin_def = (
                self.plugin
                if isinstance(self.plugin, Plugin)
                else self.discovery_service.find_plugin(
                    self.plugin.type, self.plugin.name
                )
            )

        return self._plugin_def

    @property
    def plugin_install(self):
        if self._plugin_install is None:
            self._plugin_install = (
                self.plugin
                if isinstance(self.plugin, PluginInstall)
                else self.config_service.get_plugin(self.plugin)
            )

        return self._plugin_install

    @property
    def label(self):
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"

    @property
    def docs_url(self):
        return self.plugin_def.docs

    @property
    def _env_namespace(self):
        return self.plugin_def.namespace

    @property
    def _db_namespace(self):
        return self.plugin.qualified_name

    @property
    def extra_setting_definitions(self):
        extra_settings = deepcopy(self.plugin_install.extra_settings)

        if self.plugin_install.is_custom():
            # No need to set defaults, because values will already be picked up
            # from `meltano.yml`
            return extra_settings

        # Set defaults from plugin definition
        defaults = {f"_{k}": v for k, v in self.plugin_def.extras.items()}

        for setting in extra_settings:
            default_value = defaults.get(setting.name)
            if default_value is not None:
                setting.value = default_value

        # Create setting definitions for unknown defaults,
        # including flattened keys of default nested object items
        extra_settings.extend(
            SettingDefinition.from_missing(
                extra_settings, defaults, custom=False, default=True
            )
        )

        return extra_settings

    @property
    def _definitions(self):
        return [*self.plugin_def.settings, *self.extra_setting_definitions]

    @property
    def _meltano_yml_config(self):
        try:
            plugin_install = self.plugin_install
        except PluginMissingError:
            return {}

        return {
            **plugin_install.current_config,
            **{f"_{k}": v for k, v in plugin_install.current_extras.items()},
        }

    def _update_meltano_yml_config(self, config_with_extras):
        try:
            plugin_install = self.plugin_install
        except PluginMissingError:
            return

        config = plugin_install.current_config
        extras = plugin_install.current_extras

        config.clear()
        extras.clear()

        for k, v in config_with_extras.items():
            if k.startswith("_"):
                extras[k[1:]] = v
            else:
                config[k] = v

        self.config_service.update_plugin(plugin_install)

    def _process_config(self, config):
        return self.plugin_install.process_config(config)

    def profile_with_config(self, profile: Profile, extras=False, **kwargs):
        self.plugin_install.use_profile(profile)

        config_dict = {}
        config_metadata = {}

        config_with_metadata = self.config_with_metadata(extras=extras, **kwargs)
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
