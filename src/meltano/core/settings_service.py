import logging
import os
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, Iterable, List

from meltano.core.utils import NotFound
from meltano.core.utils import expand_env_vars as do_expand_env_vars
from meltano.core.utils import find_named, flatten

from .setting_definition import SettingDefinition, SettingKind, SettingMissingError
from .settings_store import SettingValueStore, StoreNotSupportedError

logger = logging.getLogger(__name__)


# sentinel value to use to prevent leaking sensitive data
REDACTED_VALUE = "(redacted)"


class SettingsService(ABC):
    LOGGING = False

    def __init__(self, project, show_hidden=True, env_override={}, config_override={}):
        self.project = project

        self.show_hidden = show_hidden

        self.env_override = env_override
        self.config_override = config_override

        self._setting_defs = None

    @property
    @abstractmethod
    def label(self):
        pass

    @property
    @abstractmethod
    def docs_url(self):
        pass

    @property
    def env_prefixes(self) -> [str]:
        """Return prefixes for setting environment variables."""
        return []

    @property
    @abstractmethod
    def db_namespace(self) -> str:
        """Return namespace for setting value records in system database."""
        pass

    @property
    @abstractmethod
    def setting_definitions(self) -> List[SettingDefinition]:
        """Return definitions of supported settings."""
        pass

    @property
    def inherited_settings_service(self):
        """Return settings service to inherit configuration from."""
        pass

    @property
    @abstractmethod
    def meltano_yml_config(self) -> Dict:
        """Return current configuration in `meltano.yml`."""
        pass

    @abstractmethod
    def update_meltano_yml_config(self, config):
        """Update configuration in `meltano.yml`."""
        pass

    @abstractmethod
    def process_config(self):
        """Process configuration dictionary to be used downstream."""
        pass

    @property
    def flat_meltano_yml_config(self):
        return flatten(self.meltano_yml_config, "dot")

    @property
    def env(self):
        return {**os.environ, **self.env_override}

    @classmethod
    def unredact(cls, values: dict) -> Dict:
        """
        Removes any redacted values in a dictionary.
        """

        return {k: v for k, v in values.items() if v != REDACTED_VALUE}

    def config_with_metadata(
        self,
        prefix=None,
        extras=None,
        source=SettingValueStore.AUTO,
        source_manager=None,
        **kwargs,
    ):
        if source_manager:
            source_manager.bulk = True
        else:
            source_manager = source.manager(self, bulk=True, **kwargs)

        config = {}
        for setting_def in self.definitions(extras=extras):
            if prefix and not setting_def.name.startswith(prefix):
                continue

            value, metadata = self.get_with_metadata(
                setting_def.name,
                setting_def=setting_def,
                source=source,
                source_manager=source_manager,
                **kwargs,
            )

            name = setting_def.name
            if prefix:
                name = name[len(prefix) :]

            config[name] = {**metadata, "value": value}

        return config

    def as_dict(self, *args, process=False, **kwargs) -> Dict:
        config_metadata = self.config_with_metadata(*args, **kwargs)

        if process:
            config = {
                key: metadata["setting"].post_process_value(metadata["value"])
                for key, metadata in config_metadata.items()
            }
            config = self.process_config(config)
        else:
            config = {
                key: metadata["value"] for key, metadata in config_metadata.items()
            }

        return config

    def as_env(self, *args, **kwargs) -> Dict[str, str]:
        full_config = self.config_with_metadata(*args, **kwargs)

        env = {}
        for key, config in full_config.items():
            value = config["value"]
            if value is None:
                continue

            setting_def = config["setting"]
            value = setting_def.stringify_value(value)

            for env_var in self.setting_env_vars(setting_def, for_writing=True):
                if env_var.negated:
                    continue

                env[env_var.key] = value

        return env

    def get_with_metadata(
        self,
        name: str,
        redacted=False,
        source=SettingValueStore.AUTO,
        source_manager=None,
        setting_def=None,
        expand_env_vars=True,
        **kwargs,
    ):
        try:
            setting_def = setting_def or self.find_setting(name)
        except SettingMissingError:
            pass

        if setting_def:
            name = setting_def.name

        self.log(f"Getting setting '{name}'")

        metadata = {"name": name, "source": source, "setting": setting_def}

        expandable_env = {**self.project.dotenv_env, **self.env}
        if setting_def and setting_def.is_extra:
            expandable_env.update(
                self.as_env(
                    extras=False,
                    redacted=redacted,
                    source=source,
                    source_manager=source_manager,
                )
            )

        manager = source_manager or source.manager(self, **kwargs)
        value, get_metadata = manager.get(name, setting_def=setting_def)
        metadata.update(get_metadata)

        if expand_env_vars and metadata.get("expandable", False):
            metadata["expandable"] = False

            expanded_value = do_expand_env_vars(value, env=expandable_env)

            if expanded_value != value:
                metadata["expanded"] = True
                metadata["unexpanded_value"] = value
                value = expanded_value

        if setting_def:
            if (
                setting_def.kind == SettingKind.OBJECT
                and metadata["source"] is SettingValueStore.DEFAULT
            ):
                object_value = {}
                object_source = SettingValueStore.DEFAULT
                for setting_key in [setting_def.name, *setting_def.aliases]:
                    flat_config_metadata = self.config_with_metadata(
                        prefix=f"{setting_key}.",
                        redacted=redacted,
                        source=source,
                        source_manager=source_manager,
                        expand_env_vars=expand_env_vars,
                    )
                    for nested_key, config_metadata in flat_config_metadata.items():
                        if nested_key in object_value:
                            continue

                        object_value[nested_key] = config_metadata["value"]

                        nested_source = config_metadata["source"]
                        if nested_source.overrides(object_source):
                            object_source = nested_source

                if object_value:
                    value = object_value
                    metadata["source"] = object_source

            cast_value = setting_def.cast_value(value)
            if cast_value != value:
                metadata["uncast_value"] = value
                value = cast_value

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and setting_def.is_redacted:
                metadata["redacted"] = True
                value = REDACTED_VALUE

        self.log(f"Got setting '{name}' with metadata: {metadata}")
        return value, metadata

    def get_with_source(self, *args, **kwargs):
        value, metadata = self.get_with_metadata(*args, **kwargs)
        return value, metadata["source"]

    def get(self, *args, **kwargs):
        value, _ = self.get_with_source(*args, **kwargs)
        return value

    def set_with_metadata(
        self, path: List[str], value, store=SettingValueStore.AUTO, **kwargs
    ):
        self.log(f"Setting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            setting_def = None

        metadata = {"name": name, "path": path, "store": store, "setting": setting_def}

        if value == REDACTED_VALUE:
            metadata["redacted"] = True
            return None, metadata

        if setting_def:
            cast_value = setting_def.cast_value(value)
            if cast_value != value:
                metadata["uncast_value"] = value
                value = cast_value

        manager = store.manager(self, **kwargs)
        set_metadata = manager.set(name, path, value, setting_def=setting_def)
        metadata.update(set_metadata)

        self.log(f"Set setting '{name}' with metadata: {metadata}")
        return value, metadata

    def set(self, *args, **kwargs):
        value, _ = self.set_with_metadata(*args, **kwargs)
        return value

    def unset(self, path: List[str], store=SettingValueStore.AUTO, **kwargs):
        self.log(f"Unsetting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            setting_def = None

        metadata = {"name": name, "path": path, "store": store, "setting": setting_def}

        manager = store.manager(self, **kwargs)
        unset_metadata = manager.unset(name, path, setting_def=setting_def)
        metadata.update(unset_metadata)

        self.log(f"Unset setting '{name}' with metadata: {metadata}")
        return metadata

    def reset(self, store=SettingValueStore.AUTO, **kwargs):
        metadata = {"store": store}

        manager = store.manager(self, **kwargs)
        reset_metadata = manager.reset()
        metadata.update(reset_metadata)

        self.log(f"Reset settings with metadata: {metadata}")
        return metadata

    def definitions(self, extras=None) -> Iterable[Dict]:
        if self._setting_defs is None:
            self._setting_defs = [
                setting
                for setting in self.setting_definitions
                if setting.kind != SettingKind.HIDDEN or self.show_hidden
            ]

        if extras is not None:
            return [
                setting
                for setting in self._setting_defs
                if (extras is True and setting.is_extra)  # noqa: WPS408
                or (extras is False and not setting.is_extra)
            ]

        return self._setting_defs

    def find_setting(self, name: str) -> SettingDefinition:
        try:
            return next(
                s for s in self.definitions() if s.name == name or name in s.aliases
            )
        except StopIteration as err:
            raise SettingMissingError(name) from err

    def setting_env_vars(self, setting_def, for_writing=False):
        return setting_def.env_vars(self.env_prefixes)

    def setting_env(self, setting_def):
        return self.setting_env_vars(setting_def)[0].key

    def log(self, message):
        if self.LOGGING:
            logger.debug(message)
