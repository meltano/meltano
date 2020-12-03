from typing import Iterable, Dict, List

from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_service import (
    SettingsService,
    SettingMissingError,
    SettingValueStore,
    REDACTED_VALUE,
)
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import BasePlugin
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.error import PluginMissingError


class PluginSettingsService(SettingsService):
    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        *args,
        plugins_service: ProjectPluginsService = None,
        **kwargs,
    ):
        super().__init__(project, *args, **kwargs)

        self.plugin = plugin
        self.plugins_service = plugins_service or ProjectPluginsService(self.project)

        project_settings_service = ProjectSettingsService(
            self.project, config_service=self.plugins_service.config_service
        )

        self.env_override = {
            **project_settings_service.env,
            **project_settings_service.as_env(),
            **self.env_override,
            **self.plugin.info_env,
        }

    @property
    def label(self):
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"

    @property
    def docs_url(self):
        return self.plugin.docs

    @property
    def _env_prefixes(self):
        return [self.plugin.name, self.plugin.namespace]

    @property
    def _generic_env_prefix(self):
        return f"meltano_{self.plugin.type.verb}"

    @property
    def _db_namespace(self):
        # "default" is included for legacy reasons
        return ".".join((self.plugin.type, self.plugin.name, "default"))

    @property
    def _definitions(self):
        return self.plugin.settings_with_extras

    @property
    def _meltano_yml_config(self):
        return self.plugin.config_with_extras

    def _update_meltano_yml_config(self, config_with_extras):
        self.plugin.config_with_extras = config_with_extras
        self.plugins_service.update_plugin(self.plugin)

    def _process_config(self, config):
        return self.plugin.process_config(config)
