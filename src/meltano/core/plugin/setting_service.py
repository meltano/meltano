import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple

from meltano.core.db import project_engine
from meltano.core.utils import nest
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from . import Plugin, PluginType
from .setting import PluginSetting


class PluginSettingsService:
    def __init__(self, project, plugin: Plugin, plugin_discovery=None):
        self.project = project
        self.plugin = plugin
        self.plugin_discovery = plugin_discovery or PluginDiscoveryService(project)
        _, self._session_cls = project_engine(project)

    def settings(self, enabled_only=True):
        try:
            session = self._session_cls()
            q = session.query(PluginSetting) \
              .filter_by(plugin=self.plugin.name)

            if enabled_only:
                q.filter_by(enabled=True)

            return q.all()
        finally:
            session.close()

    @classmethod
    def plugin_namespace(cls, plugin: Plugin) -> str:
        return f"{plugin.type}.{plugin.name}"

    @property
    def namespace(self):
        return self.plugin_namespace(self.plugin)

    def as_config(self) -> Dict:
        plugin_def = self.get_definition()
        config = {}

        for config_def in plugin_def.config:
            print(config_def)
            nest(config,
                 config_def['name'],
                 self.get_value(config_def['name']))

        return config

    def set(self, name: str, value, enabled=True):
        try:
            session = self._session_cls()
            setting = PluginSetting(namespace=self.namespace,
                                    name=name,
                                    enabled=enabled)

            setting.defined_value = value
            session.merge(setting)
            session.commit()
        finally:
            session.close()

    def get_definition(self):
        return self.plugin_discovery.find_plugin(self.plugin.type,
                                                 self.plugin.name)

    # TODO: ensure `kind` is handled
    def get_value(self, name: str):
        session = self._session_cls()

        try:
            plugin_def = self.get_definition()
            config_def = next(
                config for config in plugin_def.config
                if config['name'] == name
            )

            if config_def['env'] in os.environ:
                logging.debug(f"Found ENV variable {key} for {self.plugin.name}:{config_def['name']}")
                return os.environ[config_def['key']]

            setting = session.query(PluginSetting) \
              .filter_by(namespace=self.namespace,
                         name=name,
                         enabled=True) \
              .one() \
              .defined_value
        except StopIteration:
            logging.error(f"Cannot find {key} for {self.plugin.name}.")
        except sqlalchemy.orm.exc.NoResultFound:
            # that means it was not overriden
            return config_def.get("value")
        finally:
            session.close()
