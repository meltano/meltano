"""Settings manager for Meltano plugins."""

from __future__ import annotations

import typing as t
from functools import cached_property

from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.settings_service import FeatureFlags, SettingsService
from meltano.core.utils import EnvVarMissingBehavior, expand_env_vars

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.setting_definition import SettingDefinition


class PluginSettingsService(SettingsService):
    """Settings manager for Meltano plugins."""

    def __init__(
        self,
        project: Project,
        plugin: ProjectPlugin,
        *args,  # noqa: ANN002
        **kwargs,  # noqa: ANN003
    ):
        """Create a new plugin settings manager.

        Args:
            project: The Meltano project.
            plugin: The Meltano plugin.
            args: Positional arguments to pass to the superclass.
            kwargs: Keyword arguments to pass to the superclass.
        """
        super().__init__(project, *args, **kwargs)
        self.plugin = plugin

        if self.project.environment:
            environment = self.project.environment
            self.environment_plugin_config = environment.get_plugin_config(
                self.plugin.type,
                self.plugin.name,
            )
        else:
            self.environment_plugin_config = None

        self.env_override = {
            # project level environment variables:
            **self.project.settings.env,
            # project level settings as env vars (e.g. `MELTANO_PROJECT_ID`):
            **self.project.settings.as_env(),
            # plugin level overrides, passed in as `**kwargs` and set to
            # `self.env_overrides` by `super().__init__` above:
            **self.env_override,
            # generated generic plugin settings as env vars
            # (e.g. `MELTANO_EXTRACT_NAME`):
            **self.plugin.info_env,
            # env vars stored under the `env:` key of the plugin definition:
            **self.plugin.env,
        }

        environment_env = {}
        if self.project.environment:
            with self.project.settings.feature_flag(
                FeatureFlags.STRICT_ENV_VAR_MODE,
                raise_error=False,
            ) as strict_env_var_mode:
                environment_env = {
                    var: expand_env_vars(
                        value,
                        self.env_override,
                        if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                    )
                    for var, value in self.project.environment.env.items()
                }
                # expand state_id_suffix
                self.project.environment.state_id_suffix = expand_env_vars(
                    self.project.environment.state_id_suffix,
                    {
                        **self.project.dotenv_env,
                        **self.env_override,
                    },
                    if_missing=EnvVarMissingBehavior(strict_env_var_mode),
                )

            # active Meltano Environment top level `env:` key
            self.env_override.update(environment_env)

        environment_plugin_env = (
            self.environment_plugin_config.env if self.environment_plugin_config else {}
        )
        # env vars stored under the `env:` key of the plugin definition of the
        # active meltano Environment
        self.env_override.update(environment_plugin_env)

    @property
    def project_settings_service(self):  # noqa: ANN201
        """Get the settings service for the active project.

        Returns:
            A project settings service for the active project.
        """
        return self.project.settings

    @property
    def label(self) -> str:
        """Get the label for this plugin.

        Returns:
            The label for this plugin.
        """
        return f"{self.plugin.type.descriptor} '{self.plugin.name}'"

    @property
    def docs_url(self):  # noqa: ANN201
        """Get the documentation URL for this plugin.

        Returns:
            The documentation URL for this plugin.
        """
        return self.plugin.docs

    def setting_env_vars(self, setting_def: SettingDefinition, *, for_writing=False):  # noqa: ANN001, ANN201
        """Get environment variables for a setting.

        Args:
            setting_def: The setting definition.
            for_writing: Whether to get environment variables for writing.

        Returns:
            Environment variables for a setting.
        """
        return setting_def.env_vars(
            prefixes=self.plugin.env_prefixes(for_writing=for_writing),
            include_custom=self.plugin.is_shadowing or for_writing,
            for_writing=for_writing,
        )

    @property
    def db_namespace(self):  # noqa: ANN201
        """Return namespace for setting value records in system database.

        Returns:
            Namespace for setting value records in system database.
        """
        # "default" is included for legacy reasons
        return ".".join((self.plugin.type, self.plugin.name, "default"))

    @property
    def setting_definitions(self) -> list[SettingDefinition]:
        """Return definitions of supported settings.

        Returns:
            A list of setting definitions.
        """
        settings = self.plugin.settings_with_extras

        if self.environment_plugin_config is not None:
            settings.extend(
                self.environment_plugin_config.get_orphan_settings(settings),
            )

        return settings

    @property
    def meltano_yml_config(self):  # noqa: ANN201
        """Return current configuration in `meltano.yml`.

        Returns:
            Current configuration in `meltano.yml`.
        """
        return self.plugin.config_with_extras

    @property
    def environment_config(self):  # noqa: ANN201
        """Return current environment configuration in `meltano.yml`.

        Returns:
            Current environment configuration in `meltano.yml`.
        """
        if self.environment_plugin_config:
            return self.environment_plugin_config.config_with_extras
        return {}

    def update_meltano_yml_config(self, config_with_extras) -> None:  # noqa: ANN001
        """Update configuration in `meltano.yml`.

        Args:
            config_with_extras: Configuration to update.
        """
        self.plugin.config_with_extras = config_with_extras
        self.project.plugins.update_plugin(self.plugin)

    def update_meltano_environment_config(
        self,
        config_with_extras: dict[str, t.Any],
    ) -> None:
        """Update environment configuration in `meltano.yml`.

        Args:
            config_with_extras: Configuration to update.
        """
        self.environment_plugin_config.config_with_extras = config_with_extras
        self.project.plugins.update_environment_plugin(self.environment_plugin_config)

    @cached_property
    def inherited_settings_service(self):  # noqa: ANN201
        """Return settings service to inherit configuration from.

        Returns:
            Settings service to inherit configuration from.
        """
        return (
            type(self)(
                self.project,
                self.plugin.parent,
                env_override=self.env_override,
            )
            if isinstance(self.plugin.parent, ProjectPlugin)
            else None
        )

    def process_config(self, config):  # noqa: ANN001, ANN201
        """Process configuration dictionary to be passed to plugin.

        Args:
            config: Configuration dictionary to process.

        Returns:
            Processed configuration dictionary.
        """
        return self.plugin.process_config(config)
