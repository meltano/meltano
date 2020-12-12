from typing import Dict, Iterable, List

from meltano.core.plugin import BasePlugin
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_service import (
    REDACTED_VALUE,
    SettingMissingError,
    SettingsService,
    SettingValueStore,
)


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

        self._inherited_settings_service = None

    @property
    def label(self):
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"

    @property
    def docs_url(self):
        return self.plugin.docs

    def setting_env_vars(self, setting_def, for_writing=False):
        return setting_def.env_vars(
            self.plugin.env_prefixes(for_writing=for_writing),
            include_custom=self.plugin.is_shadowing or for_writing,
        )

    @property
    def db_namespace(self):
        """Return namespace for setting value records in system database."""
        # "default" is included for legacy reasons
        return ".".join((self.plugin.type, self.plugin.name, "default"))

    @property
    def setting_definitions(self):
        """Return definitions of supported settings."""
        return self.plugin.settings_with_extras

    @property
    def meltano_yml_config(self):
        """Return current configuration in `meltano.yml`."""
        return self.plugin.config_with_extras

    def update_meltano_yml_config(self, config_with_extras):
        """Update configuration in `meltano.yml`."""
        self.plugin.config_with_extras = config_with_extras
        self.plugins_service.update_plugin(self.plugin)

    @property
    def inherited_settings_service(self):
        """Return settings service to inherit configuration from."""
        parent_plugin = self.plugin.parent
        if not isinstance(parent_plugin, ProjectPlugin):
            return None

        if self._inherited_settings_service is None:
            self._inherited_settings_service = self.__class__(
                self.project,
                parent_plugin,
                env_override=self.env_override,
                plugins_service=self.plugins_service,
            )
        return self._inherited_settings_service

    def process_config(self, config):
        """Process configuration dictionary to be passed to plugin."""
        return self.plugin.process_config(config)
