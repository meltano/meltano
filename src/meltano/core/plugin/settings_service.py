import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple, List
from copy import deepcopy
from enum import Enum

from meltano.core.utils import nest, flatten, find_named, NotFound, truthy
from meltano.core.config_service import ConfigService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.error import Error
from . import PluginRef, PluginType, Plugin, PluginInstall, SettingDefinition, Profile
from .error import PluginMissingError
from .setting import PluginSetting, REDACTED_VALUE


class PluginSettingMissingError(Error):
    """Occurs when a setting is missing."""

    def __init__(self, plugin: PluginRef, name: str):
        super().__init__(f"Cannot find setting {name} in {plugin}")


class PluginSettingValueSource(str, Enum):
    ENV = "env"  # 0
    MELTANO_YML = "meltano_yml"  # 1
    DB = "db"  # 2
    DEFAULT = "default"  # 3


class PluginSettingsService:
    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
        show_hidden=True,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self.show_hidden = show_hidden

    @classmethod
    def unredact(cls, values: dict) -> Dict:
        """
        Removes any redacted values in a dictionary.
        """

        return {k: v for k, v in values.items() if v != REDACTED_VALUE}

    @classmethod
    def is_kind_redacted(cls, kind) -> bool:
        return kind in ("password", "oauth")

    def profile_with_config(
        self, session, plugin: PluginRef, profile: Profile, redacted=False
    ):
        plugin_install = self.get_install(plugin)

        plugin_install.use_profile(profile)

        full_config = self.config_with_sources(
            session, plugin_install, redacted=redacted
        )

        return {
            **profile.canonical(),
            "config": {key: config["value"] for key, config in full_config.items()},
            "config_sources": {
                key: config["source"] for key, config in full_config.items()
            },
        }

    def profiles_with_config(
        self, session, plugin: PluginRef, redacted=False
    ) -> List[Dict]:
        plugin_install = self.get_install(plugin)

        return [
            self.profile_with_config(session, plugin, profile, redacted=redacted)
            for profile in (Profile.DEFAULT, *plugin_install.profiles)
        ]

    def config_with_sources(
        self,
        session,
        plugin: PluginRef,
        sources: List[PluginSettingValueSource] = None,
        redacted=False,
    ):
        # defaults to the meltano.yml for extraneous settings
        plugin_install = self.get_install(plugin)
        config = {
            key: {"value": value, "source": PluginSettingValueSource.MELTANO_YML}
            for key, value in deepcopy(plugin_install.current_config).items()
        }

        # definition settings
        for setting in self.definitions(plugin):
            value, source = self.get_value(session, plugin, setting.name)
            if sources and source not in sources:
                continue

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and self.is_kind_redacted(setting.kind):
                value = REDACTED_VALUE

            config[setting.name] = {"value": value, "source": source}

        return config

    def as_config(self, *args, **kwargs) -> Dict:
        full_config = self.config_with_sources(*args, **kwargs)

        return {key: config["value"] for key, config in full_config.items()}

    def as_env(
        self, session, plugin: PluginRef, sources: List[PluginSettingValueSource] = None
    ) -> Dict[str, str]:
        # defaults to the meltano.yml for extraneous settings
        plugin_def = self.get_definition(plugin)
        env = {}

        for setting in self.definitions(plugin):
            value, source = self.get_value(session, plugin, setting.name)
            if sources and source not in sources:
                logging.debug(f"Setting {setting.name} is not in sources: {sources}.")
                continue

            env_key = self.setting_env(setting, plugin_def)
            env[env_key] = str(value)

        return env

    def set(self, session, plugin: PluginRef, name: str, value, enabled=True):
        try:
            plugin_def = self.get_definition(plugin)
            setting_def = self.find_setting(plugin, name)
            env_key = self.setting_env(setting_def, plugin_def)

            if env_key in os.environ:
                logging.warning(f"Setting `{name}` is currently set via ${env_key}.")
                return

            if value == REDACTED_VALUE:
                return

            setting = PluginSetting(
                namespace=plugin.qualified_name, name=name, value=value, enabled=enabled
            )

            session.merge(setting)
            session.commit()

            return setting
        except StopIteration:
            logging.warning(f"Setting `{name}` not found.")

    def unset(self, session, plugin: PluginRef, name: str):
        session.query(PluginSetting).filter_by(
            namespace=plugin.qualified_name, name=name
        ).delete()
        session.commit()

    def get_definition(self, plugin: PluginRef) -> Plugin:
        return self.discovery_service.find_plugin(plugin.type, plugin.name)

    def find_setting(self, plugin: PluginRef, name: str) -> Dict:
        try:
            return find_named(self.definitions(plugin), name)
        except NotFound as err:
            raise PluginSettingMissingError(plugin, name) from err

    def definitions(self, plugin_ref: PluginRef) -> Iterable[Dict]:
        settings = set()
        plugin_def = self.get_definition(plugin_ref)
        only_visible = lambda s: s.kind != "hidden" or self.show_hidden

        return list(filter(only_visible, plugin_def.settings))

    def get_install(self, plugin: PluginRef) -> PluginInstall:
        return self.config_service.get_plugin(plugin)

    def setting_env(self, setting_def, plugin_def):
        if setting_def.env:
            return setting_def.env

        parts = (plugin_def.namespace, setting_def["name"])
        process = lambda s: s.replace(".", "__").upper()
        return "_".join(map(process, parts))

    def get_value(self, session, plugin: PluginRef, name: str):
        plugin_install = self.get_install(plugin)
        plugin_def = self.get_definition(plugin)
        setting_def = self.find_setting(plugin, name)

        try:
            env_key = self.setting_env(setting_def, plugin_def)

            # priority 1: environment variable
            if env_key in os.environ:
                logging.debug(
                    f"Found ENV variable {env_key} for {plugin_def.namespace}:{name}"
                )

                value = os.environ[env_key]
                if setting_def.kind == "boolean":
                    value = truthy(value)

                return (value, PluginSettingValueSource.ENV)

            # priority 2: installed configuration
            if setting_def.name in plugin_install.current_config:
                return (
                    plugin_install.current_config[setting_def.name],
                    PluginSettingValueSource.MELTANO_YML,
                )

            # priority 3: settings database
            return (
                (
                    session.query(PluginSetting)
                    .filter_by(namespace=plugin.qualified_name, name=name, enabled=True)
                    .one()
                    .value
                ),
                PluginSettingValueSource.DB,
            )
        except sqlalchemy.orm.exc.NoResultFound:
            # priority 4: setting default value
            # that means it was not overriden
            return setting_def.value, PluginSettingValueSource.DEFAULT
