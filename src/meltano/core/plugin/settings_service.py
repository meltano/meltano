import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple, List
from copy import deepcopy
from enum import Enum

from meltano.core.db import project_engine
from meltano.core.utils import nest
from meltano.core.config_service import ConfigService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.error import Error
from . import PluginRef, PluginType, Plugin, PluginInstall
from .setting import PluginSetting


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
        session,
        project,
        config_service: ConfigService = None,
        discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.plugin_discovery = discovery_service or PluginDiscoveryService(project)
        self._session = session

    def settings(self, plugin: PluginRef, enabled_only=True):
        q = self._session.query(PluginSetting).filter_by(
            namespace=plugin.qualified_name
        )

        if enabled_only:
            q.filter_by(enabled=True)

        return q.all()

    def as_config(
        self, plugin: PluginRef, sources: List[PluginSettingValueSource] = None
    ) -> Dict:
        # defaults to the meltano.yml for extraneous settings
        config = deepcopy(self.get_install(plugin).config)
        plugin_def = self.get_definition(plugin)

        for setting in plugin_def.settings:
            value, source = self.get_value(plugin, setting["name"])
            if sources and source not in sources:
                continue

            nest(config, setting["name"], value)

        return config

    def as_env(
        self, plugin: PluginRef, sources: List[PluginSettingValueSource] = None
    ) -> Dict[str, str]:
        # defaults to the meltano.yml for extraneous settings
        plugin_def = self.get_definition(plugin)
        env = {}

        for setting in plugin_def.settings:
            value, source = self.get_value(plugin, setting["name"])
            if sources and source not in sources:
                continue

            env_key = self.setting_env(setting, plugin_def)
            env[env_key] = str(value)

        return env

    def set(self, plugin: PluginRef, name: str, value, enabled=True):
        try:
            plugin_def = self.get_definition(plugin)
            setting_def = self.find_setting(plugin_def, name)
            env_key = self.setting_env(setting_def, plugin_def)

            if env_key in os.environ:
                logging.warning(f"Setting `{name}` is currently set via ${env_key}.")
                return

            setting = PluginSetting(
                namespace=plugin.qualified_name, name=name, value=value, enabled=enabled
            )

            self._session.merge(setting)
            self._session.commit()

            return setting
        except StopIteration:
            logging.warning(f"Setting `{name}` not found.")

    def unset(self, plugin: PluginRef, name: str):
        self._session.query(PluginSetting).filter_by(
            namespace=plugin.qualified_name, name=name
        ).delete()
        self._session.commit()

    def get_definition(self, plugin: PluginRef) -> Plugin:
        return self.plugin_discovery.find_plugin(plugin.type, plugin.name)

    def find_setting(self, plugin_def: Dict, name: str) -> Dict:
        return next(
            setting for setting in plugin_def.settings if setting["name"] == name
        )

    def get_install(self, plugin: PluginRef) -> PluginInstall:
        return self.config_service.find_plugin(plugin.name, plugin_type=plugin.type)

    def setting_env(self, setting_def, plugin_def):
        try:
            return setting_def["env"]
        except KeyError:
            parts = (plugin_def.namespace, setting_def["name"])
            process = lambda s: s.replace(".", "__").upper()
            return "_".join(map(process, parts))

    # TODO: ensure `kind` is handled
    def get_value(self, plugin: PluginRef, name: str):
        plugin_install = self.get_install(plugin)
        plugin_def = self.get_definition(plugin)

        try:
            setting_def = self.find_setting(plugin_def, name)
        except StopIteration:
            raise PluginSettingMissingError(plugin_def, name)

        try:
            env_key = self.setting_env(setting_def, plugin_def)

            # priority 1: environment variable
            if env_key in os.environ:
                logging.debug(
                    f"Found ENV variable {env_key} for {plugin_def.namespace}:{name}"
                )
                return (os.environ[env_key], PluginSettingValueSource.ENV)

            # priority 2: installed configuration
            if setting_def["name"] in plugin_install.config:
                return (
                    plugin_install.config[setting_def["name"]],
                    PluginSettingValueSource.MELTANO_YML,
                )

            # priority 3: settings database
            return (
                (
                    self._session.query(PluginSetting)
                    .filter_by(namespace=plugin.qualified_name, name=name, enabled=True)
                    .one()
                    .value
                ),
                PluginSettingValueSource.DB,
            )
        except sqlalchemy.orm.exc.NoResultFound:
            # priority 4: setting default value
            # that means it was not overriden
            return setting_def.get("value"), PluginSettingValueSource.DEFAULT
