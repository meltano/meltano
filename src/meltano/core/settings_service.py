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
    def _update_meltano_yml_config(self):
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

    def config_with_metadata(self, sources: List[SettingValueStore] = None, **kwargs):
        config = {}
        for setting in self.definitions():
            value, metadata = self.get_with_metadata(setting.name, **kwargs)

            source = metadata["source"]
            if sources and source not in sources:
                continue

            config[setting.name] = {**metadata, "value": value, "setting": setting}

        return config

    def as_dict(self, *args, **kwargs) -> Dict:
        full_config = self.config_with_metadata(*args, **kwargs)

        return {key: config["value"] for key, config in full_config.items()}

    def as_env(self, *args, **kwargs) -> Dict[str, str]:
        full_config = self.config_with_metadata(*args, **kwargs)

        return {
            self.setting_env(config["setting"]): str(config["value"])
            for key, config in full_config.items()
            if config["value"] is not None
        }

    def get_with_metadata(
        self, name: str, redacted=False, source=SettingValueStore.AUTO, **kwargs
    ):
        logger.debug(f"Getting setting '{name}'")

        metadata = {"name": name, "source": source}

        manager = source.manager(self, **kwargs)
        value, get_metadata = manager.get(name)
        metadata.update(get_metadata)

        try:
            setting_def = self.find_setting(name)

            cast_value = setting_def.cast_value(value)
            if cast_value != value:
                metadata["uncast_value"] = value
                value = cast_value

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and setting_def.is_redacted:
                metadata["redacted"] = True
                value = REDACTED_VALUE
        except SettingMissingError:
            pass

        logger.debug(f"Got setting '{name}' with metadata: {metadata}")
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
        logger.debug(f"Setting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        metadata = {"name": name, "path": path, "store": store}

        if value == REDACTED_VALUE:
            metadata["redacted"] = True
            return None, metadata

        try:
            setting_def = self.find_setting(name)

            cast_value = setting_def.cast_value(value)
            if cast_value != value:
                metadata["uncast_value"] = value
                value = cast_value
        except SettingMissingError:
            pass

        manager = store.manager(self, **kwargs)
        set_metadata = manager.set(name, path, value)
        metadata.update(set_metadata)

        logger.debug(f"Set setting '{name}' with metadata: {metadata}")
        return value, metadata

    def set(self, *args, **kwargs):
        value, _ = self.set_with_metadata(*args, **kwargs)
        return value

    def unset(self, path: List[str], store=SettingValueStore.AUTO, **kwargs):
        logger.debug(f"Unsetting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        metadata = {"name": name, "path": path, "store": store}

        manager = store.manager(self, **kwargs)
        unset_metadata = manager.unset(name, path)
        metadata.update(unset_metadata)

        logger.debug(f"Unset setting '{name}' with metadata: {metadata}")
        return metadata

    def reset(self, store=SettingValueStore.AUTO, **kwargs):
        metadata = {"store": store}

        manager = store.manager(self, **kwargs)
        reset_metadata = manager.reset()
        metadata.update(reset_metadata)

        logger.debug(f"Reset settings with metadata: {metadata}")
        return metadata

    def definitions(self) -> Iterable[Dict]:
        definitions = deepcopy(self._definitions)
        definition_names = set(s.name for s in definitions)

        definitions.extend(
            (
                SettingDefinition.from_key_value(k, v)
                for k, v in self.flat_meltano_yml_config.items()
                if k not in definition_names
            )
        )

        settings = []
        for setting in definitions:
            if setting.kind == "hidden" and not self.show_hidden:
                continue

            settings.append(setting)

        return settings

    def find_setting(self, name: str) -> SettingDefinition:
        try:
            return find_named(self.definitions(), name)
        except NotFound as err:
            raise SettingMissingError(name) from err

    def setting_env(self, setting_def):
        return setting_def.env or setting_env(self._env_namespace, setting_def.name)
