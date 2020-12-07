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
from meltano.core.plugin import PluginRef, PluginType, PluginDefinition
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.error import PluginMissingError


class PluginSettingsService(SettingsService):
    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
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

        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.config_service
        )

        self.env_override = {
            **project_settings_service.env,
            **project_settings_service.as_env(),
            **self.env_override,
            **self.plugin_def.info_env,
            **self.plugin.info_env,
        }

    @property
    def plugin_def(self):
        if self._plugin_def is None:
            self._plugin_def = self.discovery_service.get_definition(self.plugin)

        return self._plugin_def

    @property
    def label(self):
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"

    @property
    def docs_url(self):
        return self.plugin_def.docs

    @property
    def _env_prefixes(self):
        return [self.plugin.name, self.plugin_def.namespace]

    @property
    def _generic_env_prefix(self):
        return f"meltano_{self.plugin.type.verb}"

    @property
    def _db_namespace(self):
        # "default" is included for legacy reasons
        return ".".join((self.plugin.type, self.plugin.name, "default"))

    @property
    def extra_setting_definitions(self):
        defaults = {f"_{k}": v for k, v in self.plugin_def.all_extras.items()}

        existing_settings = []
        for setting in self.plugin.extra_settings:
            default_value = defaults.get(setting.name)
            if default_value is not None:
                setting = setting.with_attrs(value=default_value)

            existing_settings.append(setting)

        # Create setting definitions for unknown defaults,
        # including flattened keys of default nested object items
        existing_settings.extend(
            SettingDefinition.from_missing(
                existing_settings, defaults, custom=False, default=True
            )
        )

        return existing_settings

    @property
    def _definitions(self):
        return [*self.plugin_def.settings, *self.extra_setting_definitions]

    @property
    def _meltano_yml_config(self):
        return self.plugin.config_with_extras

    def _update_meltano_yml_config(self, config_with_extras):
        self.plugin.config_with_extras = config_with_extras

        self.config_service.update_plugin(self.plugin)

    def _process_config(self, config):
        return self.plugin.process_config(config)
