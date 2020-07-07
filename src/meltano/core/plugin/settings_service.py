from typing import Iterable, Dict, List

from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import (
    SettingsService,
    SettingMissingError,
    SettingValueSource,
    SettingValueStore,
    REDACTED_VALUE,
)
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin import PluginRef, PluginType, Plugin, PluginInstall, Profile
from meltano.core.plugin.error import PluginMissingError


class PluginSettingsService:
    @classmethod
    def unredact(cls, *args):
        return SettingsService.unredact(*args)

    def __init__(self, *args, env_override={}, config_override={}, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.env_override = env_override
        self.config_override = config_override

    def with_env_override(self, env_override):
        return self.__class__(
            *self._args,
            **self._kwargs,
            env_override={**self.env_override, **env_override},
            config_override=self.config_override,
        )

    def with_config_override(self, config_override):
        return self.__class__(
            *self._args,
            **self._kwargs,
            env_override=self.env_override,
            config_override={**self.config_override, **config_override},
        )

    def build(self, plugin: PluginRef):
        return SpecificPluginSettingsService(
            plugin,
            *self._args,
            **self._kwargs,
            env_override=self.env_override,
            config_override=self.config_override,
        )

    def env(self, plugin: PluginRef):
        return self.build(plugin).env

    def profile_with_config(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).profile_with_config(*args, **kwargs, session=session)

    def profiles_with_config(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).profiles_with_config(*args, **kwargs, session=session)

    def config_with_metadata(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).config_with_metadata(*args, **kwargs, session=session)

    def as_dict(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).as_dict(*args, **kwargs, session=session)

    def as_env(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).as_env(*args, **kwargs, session=session)

    def set(
        self, session, plugin: PluginRef, *args, store=SettingValueStore.DB, **kwargs
    ):
        return self.build(plugin).set(*args, **kwargs, store=store, session=session)

    def unset(
        self, session, plugin: PluginRef, *args, store=SettingValueStore.DB, **kwargs
    ):
        return self.build(plugin).unset(*args, **kwargs, store=store, session=session)

    def reset(
        self, session, plugin: PluginRef, *args, store=SettingValueStore.DB, **kwargs
    ):
        return self.build(plugin).reset(*args, **kwargs, store=store, session=session)

    def get_with_source(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).get_with_source(*args, **kwargs, session=session)

    def get(self, session, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).get(*args, **kwargs, session=session)

    def definitions(self, plugin: PluginRef):
        return self.build(plugin).definitions()

    def find_setting(self, plugin: PluginRef, *args, **kwargs):
        return self.build(plugin).find_setting(*args, **kwargs)

    def setting_env(self, setting_def, plugin: PluginRef):
        return self.build(plugin).setting_env(setting_def)


class SpecificPluginSettingsService(SettingsService):
    def __init__(
        self,
        plugin: PluginRef,
        *args,
        plugin_discovery_service: PluginDiscoveryService = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.plugin = plugin

        discovery_service = plugin_discovery_service or PluginDiscoveryService(
            self.project
        )
        self.plugin_def = discovery_service.find_plugin(
            self.plugin.type, self.plugin.name
        )
        self._plugin_install = None

        project_settings_service = ProjectSettingsService(self.project)

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

        full_config = self.config_with_metadata(**kwargs)

        return {
            **profile.canonical(),
            "config": {key: config["value"] for key, config in full_config.items()},
            "config_sources": {
                key: config["source"] for key, config in full_config.items()
            },
        }

    def profiles_with_config(self, **kwargs) -> List[Dict]:
        return [
            self.profile_with_config(profile, **kwargs)
            for profile in (Profile.DEFAULT, *self.plugin_install.profiles)
        ]
