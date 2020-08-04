import os
import logging
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Iterable, Dict, List

from meltano.core.utils import find_named, setting_env, NotFound, flatten
from .setting_definition import SettingMissingError, SettingDefinition
from .settings_store import StoreNotSupportedError, SettingValueStore
from .config_service import ConfigService


logger = logging.getLogger(__name__)


# sentinel value to use to prevent leaking sensitive data
REDACTED_VALUE = "(redacted)"


class SettingsService(ABC):
    LOGGING = False

    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        show_hidden=True,
        env_override={},
        config_override={},
    ):
        self.project = project

        self.config_service = config_service or ConfigService(project)

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
    @abstractmethod
    def _env_namespace(self) -> str:
        pass

    @property
    @abstractmethod
    def _db_namespace(self) -> str:
        pass

    @property
    @abstractmethod
    def _definitions(self) -> List[SettingDefinition]:
        pass

    @property
    @abstractmethod
    def _meltano_yml_config(self) -> Dict:
        pass

    @abstractmethod
    def _update_meltano_yml_config(self, config):
        pass

    @abstractmethod
    def _process_config(self):
        pass

    @property
    def flat_meltano_yml_config(self):
        return flatten(self._meltano_yml_config, "dot")

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
        self, prefix=None, extras=None, source=SettingValueStore.AUTO, **kwargs
    ):
        manager = source.manager(self, bulk=True, **kwargs)

        config = {}
        for setting_def in self.definitions(extras=extras):
            if prefix and not setting_def.name.startswith(prefix):
                continue

            value, metadata = self.get_with_metadata(
                setting_def.name,
                setting_def=setting_def,
                source=source,
                source_manager=manager,
                **kwargs,
            )

            name = setting_def.name
            if prefix:
                name = name[len(prefix) :]

            config[name] = {**metadata, "value": value}

        return config

    def as_dict(self, *args, process=False, **kwargs) -> Dict:
        config_metadata = self.config_with_metadata(*args, **kwargs)

        config = {key: metadata["value"] for key, metadata in config_metadata.items()}

        if process:
            config = self._process_config(config)

        return config

    def as_env(self, *args, **kwargs) -> Dict[str, str]:
        full_config = self.config_with_metadata(*args, **kwargs)

        return {
            self.setting_env(config["setting"]): str(config["value"])
            for key, config in full_config.items()
            if config["value"] is not None
        }

    def get_with_metadata(
        self,
        name: str,
        redacted=False,
        source=SettingValueStore.AUTO,
        source_manager=None,
        setting_def=None,
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

        manager = source_manager or source.manager(self, **kwargs)
        value, get_metadata = manager.get(name, setting_def=setting_def)
        metadata.update(get_metadata)

        if setting_def:
            if (
                setting_def.kind == "object"
                and metadata["source"] is SettingValueStore.DEFAULT
            ):
                object_value = {}
                object_source = SettingValueStore.DEFAULT
                for setting_key in [setting_def.name, *setting_def.aliases]:
                    flat_config_metadata = self.config_with_metadata(
                        source=source, prefix=f"{setting_key}."
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
            setting_defs = [
                s for s in self._definitions if s.kind != "hidden" or self.show_hidden
            ]

            setting_defs.extend(
                SettingDefinition.from_missing(
                    self._definitions, self.flat_meltano_yml_config
                )
            )

            self._setting_defs = setting_defs

        if extras is not None:
            return [
                s
                for s in self._setting_defs
                if (extras is True and s.is_extra)
                or (extras is False and not s.is_extra)
            ]

        return self._setting_defs

    def find_setting(self, name: str) -> SettingDefinition:
        try:
            return next(
                s for s in self.definitions() if s.name == name or name in s.aliases
            )
        except StopIteration as err:
            raise SettingMissingError(name) from err

    def setting_env(self, setting_def):
        return setting_def.env or setting_env(self._env_namespace, setting_def.name)

    def log(self, message):
        if self.LOGGING:
            logger.debug(message)
