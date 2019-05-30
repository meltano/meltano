from . import Plugin
from typing import Iterable, Dict

from meltano.core.plugin.setting import PluginSetting
from meltano.core.db import project_engine
from meltano.core.utils import nest


class PluginSettingsService:
    def __init__(self, project, plugin: Plugin):
        self.project = project
        self.plugin = plugin
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
    def as_config(self, settings: Iterable[PluginSetting]) -> Dict:
        config = {}

        for setting in settings:
            nest(config, setting.name, setting.value)

        return config

    def set(self, key: str, attr: str, value, default=False, enabled=True):
        try:
            value_key = 'default_value' if default else 'defined_value'

            session = self._session_cls()
            setting = PluginSetting(name=attr,
                                    plugin=self.plugin.name,
                                    enabled=enabled,
                                    key=key)

            # set either the default/defined value
            setattr(setting, value_key, value)

            session.merge(setting)
            session.commit()
        finally:
            session.close()

    def get_value(self, attr):
        try:
            session = self._session_cls()
            setting = session.query(PluginSetting) \
              .filter_by(plugin=self.plugin.name,
                         name=attr) \
              .one() \
              .value
        finally:
            session.close()
