"""Settings manager for Meltano plugins."""

from typing import Any, Dict, List

from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.setting_definition import SettingDefinition
from meltano.core.settings_service import REDACTED_VALUE  # noqa: F401
from meltano.core.settings_service import SettingMissingError  # noqa: F401
from meltano.core.settings_service import SettingValueStore  # noqa: F401
from meltano.core.settings_service import SettingsService


class PluginSettingsService(SettingsService):
    """Settings manager for Meltano plugins."""

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        *args,
        plugins_service: ProjectPluginsService = None,
        **kwargs,
    ):
        """Create a new plugin settings manager.

        Args:
            project: The Meltano project.
            plugin: The Meltano plugin.
            args: Positional arguments to pass to the superclass.
            plugins_service: The Meltano plugins service.
            kwargs: Keyword arguments to pass to the superclass.
        """
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
        if self.project.active_environment:
            environment = self.project.active_environment
            self.environment_plugin_config = environment.get_plugin_config(
                self.plugin.type,
                self.plugin.name,
            )
        else:
            self.environment_plugin_config = None

    @property
    def label(self):
        """Get the label for this plugin.

        Returns:
            The label for this plugin.
        """
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"  # noqa: WPS237

    @property
    def docs_url(self):
        """Get the documentation URL for this plugin.

        Returns:
            The documentation URL for this plugin.
        """
        return self.plugin.docs

    def setting_env_vars(self, setting_def, for_writing=False):
        """Get environment variables for a setting.

        Args:
            setting_def: The setting definition.
            for_writing: Whether to get environment variables for writing.

        Returns:
            Environment variables for a setting.
        """
        return setting_def.env_vars(
            self.plugin.env_prefixes(for_writing=for_writing),
            include_custom=self.plugin.is_shadowing or for_writing,
        )

    @property
    def db_namespace(self):
        """Return namespace for setting value records in system database.

        Returns:
            Namespace for setting value records in system database.
        """
        # "default" is included for legacy reasons
        return ".".join((self.plugin.type, self.plugin.name, "default"))

    @property
    def setting_definitions(self) -> List[SettingDefinition]:
        """Return definitions of supported settings.

        Returns:
            A list of setting definitions.
        """
        settings = self.plugin.settings_with_extras

        if self.environment_plugin_config is not None:
            settings.extend(
                self.environment_plugin_config.get_orphan_settings(settings)
            )

        return settings

    @property
    def meltano_yml_config(self):
        """Return current configuration in `meltano.yml`.

        Returns:
            Current configuration in `meltano.yml`.
        """
        return self.plugin.config_with_extras

    @property
    def environment_config(self):
        """Return current environment configuration in `meltano.yml`.

        Returns:
            Current environment configuration in `meltano.yml`.
        """
        if self.environment_plugin_config:
            return self.environment_plugin_config.config_with_extras
        return {}

    def update_meltano_yml_config(self, config_with_extras):
        """Update configuration in `meltano.yml`.

        Args:
            config_with_extras: Configuration to update.
        """
        self.plugin.config_with_extras = config_with_extras
        self.plugins_service.update_plugin(self.plugin)

    def update_meltano_environment_config(self, config_with_extras: Dict[str, Any]):
        """Update environment configuration in `meltano.yml`.

        Args:
            config_with_extras: Configuration to update.
        """
        self.environment_plugin_config.config_with_extras = config_with_extras
        self.plugins_service.update_environment_plugin(self.environment_plugin_config)

    @property
    def inherited_settings_service(self):
        """Return settings service to inherit configuration from.

        Returns:
            Settings service to inherit configuration from.
        """
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
        """Process configuration dictionary to be passed to plugin.

        Args:
            config: Configuration dictionary to process.

        Returns:
            Processed configuration dictionary.
        """
        return self.plugin.process_config(config)
