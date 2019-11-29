import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple, List
from copy import deepcopy
from enum import Enum

from meltano.core.utils import nest, flatten, find_named, NotFound
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


class PluginSettingValueSource(int, Enum):
    ENV = 0
    MELTANO_YML = 1
    DB = 2
    DEFAULT = 3


class PluginSettingsService:
    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )

    @classmethod
    def unredact(cls, values: dict) -> Dict:
        """
        Removes any redacted values in a dictionary.
        """

        return {k: v for k, v in values.items() if v != REDACTED_VALUE}

    def as_config(
        self,
        session,
        plugin: PluginRef,
        sources: List[PluginSettingValueSource] = None,
        redacted=False,
    ) -> Dict:
        # defaults to the meltano.yml for extraneous settings
        plugin_install = self.get_install(plugin)
        plugin_def = self.get_definition(plugin)
        config = deepcopy(plugin_install.config)

        # definition settings
        for setting in self.definitions(plugin):
            value, source = self.get_value(session, plugin, setting.name)
            if sources and source not in sources:
                continue

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and setting.kind == "password":
                value = REDACTED_VALUE

            nest(config, setting.name, value)

        return flatten(config, reducer="dot")

    def as_profile_configs(
        self, session, plugin: PluginRef, redacted=False
    ) -> List[Dict]:
        plugin_install = self.get_install(plugin)

        profiles = []
        for profile in (Profile.DEFAULT, *plugin_install.profiles):
            plugin_install.use_profile(profile)

            # set the loaded configuration
            profile.config = self.as_config(session, plugin_install, redacted=redacted)
            profiles.append(profile.canonical())

        return profiles

    def as_env(
        self, session, plugin: PluginRef, sources: List[PluginSettingValueSource] = None
    ) -> Dict[str, str]:
        # defaults to the meltano.yml for extraneous settings
        plugin_def = self.get_definition(plugin)
        env = {}

        for setting in self.definitions(plugin):
            value, source = self.get_value(session, plugin, setting.name)
            if sources and source not in sources:
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

        return plugin_def.settings

    def get_install(self, plugin: PluginRef) -> PluginInstall:
        return self.config_service.get_plugin(plugin)

    def setting_env(self, setting_def, plugin_def):
        if setting_def.env:
            return setting_def.env

        parts = (plugin_def.namespace, setting_def["name"])
        process = lambda s: s.replace(".", "__").upper()
        return "_".join(map(process, parts))

    # TODO: ensure `kind` is handled
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
                return (os.environ[env_key], PluginSettingValueSource.ENV)

            # priority 2: installed configuration
            if setting_def.name in plugin_install.config:
                return (
                    plugin_install.config[setting_def.name],
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
