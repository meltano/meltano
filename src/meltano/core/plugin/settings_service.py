import os
import sqlalchemy
import logging
from typing import Iterable, Dict, Tuple, List
from copy import deepcopy
from enum import Enum
import re

from meltano.core.utils import nest, find_named, setting_env, NotFound, truthy
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
    CONFIG_OVERRIDE = "config_override"  # 0
    ENV = "env"  # 1
    MELTANO_YML = "meltano_yml"  # 2
    DB = "db"  # 3
    DEFAULT = "default"  # 4


class PluginSettingsService:
    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
        show_hidden=True,
        env_override={},
        config_override={},
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self.show_hidden = show_hidden
        self.env_override = env_override
        self.config_override = config_override

        self._env = None

    @classmethod
    def unredact(cls, values: dict) -> Dict:
        """
        Removes any redacted values in a dictionary.
        """

        return {k: v for k, v in values.items() if v != REDACTED_VALUE}

    @classmethod
    def is_kind_redacted(cls, kind) -> bool:
        return kind in ("password", "oauth")

    def with_env_override(self, env_override):
        return self.__class__(
            self.project,
            self.config_service,
            self.discovery_service,
            self.show_hidden,
            {**self.env_override, **env_override},
            self.config_override,
        )

    def with_config_override(self, config_override):
        return self.__class__(
            self.project,
            self.config_service,
            self.discovery_service,
            self.show_hidden,
            self.env_override,
            {**self.config_override, **config_override},
        )

    @property
    def env(self):
        if not self._env:
            self._env = {**os.environ, **self.env_override}

        return self._env

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
        setting_names = [
            *(setting.name for setting in self.definitions(plugin)),
            *(key for key in self.get_install(plugin).current_config.keys()),
        ]

        config = {}
        for name in setting_names:
            value, source = self.get_value(session, plugin, name, redacted=redacted)
            if sources and source not in sources:
                continue

            config[name] = {"value": value, "source": source}

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

            if value is None:
                continue

            env_key = self.setting_env(setting, plugin_def)
            env[env_key] = str(value)

        return env

    def set(self, session, plugin: PluginRef, name: str, value, enabled=True):
        try:
            plugin_def = self.get_definition(plugin)
            setting_def = self.find_setting(plugin, name)
            env_key = self.setting_env(setting_def, plugin_def)

            if env_key in self.env:
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
        return setting_def.env or setting_env(plugin_def.namespace, setting_def.name)

    def cast_value(self, setting_def, value):
        if isinstance(value, str) and setting_def.kind == "boolean":
            value = truthy(value)

        return value

    def get_value(self, session, plugin: PluginRef, name: str, redacted=False):
        plugin_install = self.get_install(plugin)
        plugin_def = self.get_definition(plugin)

        try:
            setting_def = self.find_setting(plugin, name)
        except PluginSettingMissingError:
            setting_def = None

        def config_override_getter():
            try:
                return self.config_override[name]
            except KeyError:
                return None

        def env_getter():
            if not setting_def:
                return None

            env_key = self.setting_env(setting_def, plugin_def)

            try:
                return self.env[env_key]
            except KeyError:
                return None
            else:
                logging.debug(
                    f"Found ENV variable {env_key} for {plugin_def.namespace}:{name}"
                )

        def meltano_yml_getter():
            try:
                value = plugin_install.current_config[name]
                return self.expand_env_vars(value)
            except KeyError:
                return None

        def db_getter():
            try:
                return (
                    session.query(PluginSetting)
                    .filter_by(namespace=plugin.qualified_name, name=name, enabled=True)
                    .one()
                    .value
                )
            except sqlalchemy.orm.exc.NoResultFound:
                return None

        def default_getter():
            if not setting_def:
                return None
            return self.expand_env_vars(setting_def.value)

        config_getters = {
            PluginSettingValueSource.CONFIG_OVERRIDE: config_override_getter,
            PluginSettingValueSource.ENV: env_getter,
            PluginSettingValueSource.MELTANO_YML: meltano_yml_getter,
            PluginSettingValueSource.DB: db_getter,
            PluginSettingValueSource.DEFAULT: default_getter,
        }

        for source, getter in config_getters.items():
            value = getter()
            if value is not None:
                break

        if setting_def:
            value = self.cast_value(setting_def, value)

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and self.is_kind_redacted(setting_def.kind):
                value = REDACTED_VALUE

        return value, source

    def expand_env_vars(self, raw_value):
        if not isinstance(raw_value, str):
            return raw_value

        # find viable substitutions
        var_matcher = re.compile(
            """
            \$                 # starts with a '$'
            (?:                # either $VAR or ${VAR}
                {(\w+)}|(\w+)  # capture the variable name as group[0] or group[1]
            )
            """,
            re.VERBOSE,
        )

        def subst(match) -> str:
            try:
                # the variable can be in either group
                var = next(var for var in match.groups() if var)
                val = str(self.env[var])

                if not val:
                    logging.warning(f"Variable {var} is empty.")

                return val
            except KeyError as e:
                logging.warning(f"Variable {var} is missing from the environment.")
                return None

        fullmatch = re.fullmatch(var_matcher, raw_value)
        if fullmatch:
            # If the entire value is an env var reference, return None if it isn't set
            return subst(fullmatch)

        return re.sub(var_matcher, subst, raw_value)
