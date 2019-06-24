import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple
from copy import deepcopy

from meltano.core.db import project_engine
from meltano.core.utils import nest
from meltano.core.config_service import ConfigService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from . import PluginRef, PluginType, Plugin, PluginInstall
from .setting import PluginSetting


class PluginSettingsService:
    def __init__(
        self,
        session,
        project,
        plugin: PluginRef,
        config_service: ConfigService = None,
        discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.plugin = plugin
        self.config_service = config_service or ConfigService(project)
        self.plugin_discovery = discovery_service or PluginDiscoveryService(project)
        self._session = session

    def settings(self, enabled_only=True):
        q = self._session.query(PluginSetting).filter_by(plugin=self.plugin.name)

        if enabled_only:
            q.filter_by(enabled=True)

        return q.all()

    @classmethod
    def plugin_namespace(cls, plugin: PluginRef) -> str:
        return f"{plugin.type}.{plugin.name}"

    @property
    def namespace(self):
        return self.plugin_namespace(self.plugin)

    def as_config(self) -> Dict:
        # defaults to the meltano.yml for extraneous settings
        config = deepcopy(self.get_install().config)
        plugin = self.get_definition()

        for setting in plugin.settings:
            nest(config, setting["name"], self.get_value(setting["name"]))

        return config

    def as_env(self) -> Dict[str, str]:
        # defaults to the meltano.yml for extraneous settings
        plugin = self.get_definition()
        env = {}

        for setting in plugin.settings:
            env_key = setting.get(
                "env", self.setting_env(plugin.namespace, setting["name"])
            )
            env[env_key] = str(self.get_value(setting["name"]))

        return env

    def set(self, name: str, value, enabled=True):
        plugin_def = self.get_definition()
        setting = self.find_setting(plugin_def, name)
        env = setting.get("env", self.setting_env(plugin_def.namespace, name))

        if env in os.environ:
            logging.warning(f"Setting {name} is currently set via ${env}.")
            return

        setting = PluginSetting(
            namespace=self.namespace, name=name, value=value, enabled=enabled
        )

        self._session.merge(setting)
        self._session.commit()

        return setting

    def unset(self, name: str):
        self._session.query(PluginSetting).filter_by(
            namespace=self.namespace, name=name
        ).delete()
        self._session.commit()

    def get_definition(self) -> Plugin:
        return self.plugin_discovery.find_plugin(self.plugin.type, self.plugin.name)

    def find_setting(self, plugin_def: Dict, name: str) -> Dict:
        return next(
            setting for setting in plugin_def.settings if setting["name"] == name
        )

    def get_install(self) -> PluginInstall:
        return self.config_service.get_plugin(
            self.plugin.name, plugin_type=self.plugin.type
        )

    def setting_env(self, *parts: Iterable[str]):
        process = lambda s: s.replace(".", "__").upper()

        return "_".join(map(process, parts))

    # TODO: ensure `kind` is handled
    def get_value(self, name: str):
        try:
            plugin_def = self.get_definition()
            plugin_install = self.get_install()
            setting = self.find_setting(plugin_def, name)
            env = setting.get("env", self.setting_env(plugin_def.namespace, name))

            # priority 1: environment variable
            if env in os.environ:
                logging.debug(
                    f"Found ENV variable {env} for {plugin_def.namespace}:{name}"
                )
                return os.environ[env]

            # priority 2: installed configuration
            if setting["name"] in plugin_install.config:
                return plugin_install.config[setting["name"]]

            # priority 3: settings database
            return (
                self._session.query(PluginSetting)
                .filter_by(namespace=self.namespace, name=name, enabled=True)
                .one()
                .value
            )
        except StopIteration:
            logging.error(f"Cannot find {name} for {self.plugin.name}.")
        except sqlalchemy.orm.exc.NoResultFound:
            # priority 4: setting default value
            # that means it was not overriden
            return setting.get("value")
