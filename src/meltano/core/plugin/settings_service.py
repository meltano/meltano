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
from meltano.core.plugin import (
    PluginRef,
    PluginType,
    PluginDefinition,
    ProjectPlugin,
    Profile,
)
from meltano.core.plugin.error import PluginMissingError


class PluginSettingsService(SettingsService):
    def __init__(
        self,
        project: Project,
        plugin_ref: PluginRef,
        *args,
        plugin_discovery_service: PluginDiscoveryService = None,
        **kwargs,
    ):
        super().__init__(project, *args, **kwargs)

        self.plugin_ref = plugin_ref

        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            self.project, config_service=self.config_service
        )
        self._plugin_def = None
        self._project_plugin = None

        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.config_service
        )

        self.env_override = {
            **project_settings_service.env,
            **project_settings_service.as_env(),
            **self.env_override,
            **self.plugin_def.info_env,
            **self.project_plugin.info_env,
        }

    @property
    def plugin_def(self):
        if self._plugin_def is None:
            self._plugin_def = (
                self.plugin_ref
                if isinstance(self.plugin_ref, PluginDefinition)
                else self.discovery_service.find_plugin(
                    self.plugin_ref.type, self.plugin_ref.name
                )
            )

        return self._plugin_def

    @property
    def project_plugin(self):
        if self._project_plugin is None:
            self._project_plugin = (
                self.plugin_ref
                if isinstance(self.plugin_ref, ProjectPlugin)
                else self.config_service.get_plugin(self.plugin_ref)
            )

        return self._project_plugin

    @property
    def label(self):
        return f"{self.plugin_ref.type.descriptor} '{self.plugin_ref.name}'"

    @property
    def docs_url(self):
        return self.plugin_def.docs

    @property
    def _env_prefixes(self):
        return [self.plugin_ref.name, self.plugin_def.namespace]

    @property
    def _generic_env_prefix(self):
        return f"meltano_{self.plugin_ref.type.verb}"

    @property
    def _db_namespace(self):
        return self.plugin_ref.qualified_name

    @property
    def extra_setting_definitions(self):
        extra_settings = deepcopy(self.project_plugin.extra_settings)

        if self.project_plugin.is_custom():
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
            project_plugin = self.project_plugin
        except PluginMissingError:
            return {}

        return {
            **project_plugin.current_config,
            **{f"_{k}": v for k, v in project_plugin.current_extras.items()},
        }

    def _update_meltano_yml_config(self, config_with_extras):
        try:
            project_plugin = self.project_plugin
        except PluginMissingError:
            return

        config = project_plugin.current_config
        extras = project_plugin.current_extras

        config.clear()
        extras.clear()

        for k, v in config_with_extras.items():
            if k.startswith("_"):
                extras[k[1:]] = v
            else:
                config[k] = v

        self.config_service.update_plugin(project_plugin)

    def _process_config(self, config):
        return self.project_plugin.process_config(config)

    def profile_with_config(self, profile: Profile, extras=False, **kwargs):
        self.project_plugin.use_profile(profile)

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
            for profile in (Profile.DEFAULT, *self.project_plugin.profiles)
        ]
