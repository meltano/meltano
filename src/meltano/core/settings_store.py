import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from enum import Enum
from typing import Any, Dict, List

import dotenv
import sqlalchemy

from .environment import NoActiveEnvironment
from .error import Error
from .project import ProjectReadonly
from .setting import Setting
from .setting_definition import SettingDefinition, SettingMissingError
from .utils import pop_at_path, set_at_path

logger = logging.getLogger(__name__)


class StoreNotSupportedError(Error):
    pass


class SettingValueStore(str, Enum):
    CONFIG_OVERRIDE = "config_override"
    MELTANO_ENV = "meltano_environment"
    ENV = "env"
    DOTENV = "dotenv"
    MELTANO_YML = "meltano_yml"
    DB = "db"
    INHERITED = "inherited"
    DEFAULT = "default"
    AUTO = "auto"

    @classmethod
    def readables(cls):
        return list(cls)

    @classmethod
    def writables(cls):
        return [store for store in cls if store.writable]

    @property
    def manager(self):
        managers = {
            self.CONFIG_OVERRIDE: ConfigOverrideStoreManager,
            self.ENV: EnvStoreManager,
            self.DOTENV: DotEnvStoreManager,
            self.MELTANO_YML: MeltanoYmlStoreManager,
            self.DB: DbStoreManager,
            self.DEFAULT: DefaultStoreManager,
            self.INHERITED: InheritedStoreManager,
            self.AUTO: AutoStoreManager,
            self.MELTANO_ENV: MeltanoEnvStoreManager,
        }
        return managers[self]

    @property
    def label(self):
        return self.manager.label

    @property
    def writable(self):
        return self.manager.writable

    def overrides(self, source):
        stores_list = list(self.__class__)
        return stores_list.index(self) < stores_list.index(source)

    def can_overwrite(self, source):
        return self.writable and (source is self or self.overrides(source))


class SettingsStoreManager(ABC):
    readable = True
    writable = False

    def __init__(self, settings_service, **kwargs):
        self.settings_service = settings_service
        self.project = self.settings_service.project

    @abstractmethod
    def get(self, name: str, setting_def=None):
        pass

    def set(self, name: str, path: List[str], value, setting_def=None):
        raise NotImplementedError

    def unset(self, name: str, path: List[str], setting_def=None):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def ensure_supported(self, method="get"):
        if method != "get" and not self.writable:
            raise StoreNotSupportedError

    def log(self, message):
        self.settings_service.log(message)


class ConfigOverrideStoreManager(SettingsStoreManager):
    label = "a command line flag"

    def get(self, name: str, setting_def=None):
        try:
            value = self.settings_service.config_override[name]
            self.log(f"Read key '{name}' from config override: {value!r}")
            return value, {}
        except KeyError:
            return None, {}


class BaseEnvStoreManager(SettingsStoreManager):
    @property
    @abstractmethod
    def env(self):
        pass

    def get(self, name: str, setting_def=None):
        if not setting_def:
            raise StoreNotSupportedError

        for env_var in self.setting_env_vars(setting_def):
            try:
                value = env_var.get(self.env)
                return value, {"env_var": env_var.key}
            except KeyError:
                pass

        return None, {}

    def setting_env_vars(self, *args, **kwargs):
        return self.settings_service.setting_env_vars(*args, **kwargs)


class EnvStoreManager(BaseEnvStoreManager):
    label = "the environment"

    @property
    def env(self):
        return self.settings_service.env

    def get(self, *args, **kwargs):
        value, metadata = super().get(*args, **kwargs)

        if value is not None:
            env_key = metadata["env_var"]
            self.log(f"Read key '{env_key}' from the environment: {value!r}")

        return value, metadata


class DotEnvStoreManager(BaseEnvStoreManager):
    label = "`.env`"
    writable = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._env = None

    def ensure_supported(self, method="get"):
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    @property
    def env(self):
        if self._env is None:
            self._env = self.project.dotenv_env
        return self._env

    def get(self, *args, **kwargs):
        value, metadata = super().get(*args, **kwargs)

        if value is not None:
            env_key = metadata["env_var"]
            self.log(f"Read key '{env_key}' from `.env`: {value!r}")

        return value, metadata

    def set(self, name: str, path: List[str], value, setting_def=None):
        if not setting_def:
            raise StoreNotSupportedError

        primary_var, *other_vars = self.setting_env_vars(setting_def)
        primary_key = primary_var.key
        other_keys = [var.key for var in other_vars]

        with self.update_dotenv() as dotenv_file:
            if dotenv_file.exists():
                for key in other_keys:
                    dotenv.unset_key(dotenv_file, key)
                    self.log(f"Unset key '{key}' in `.env`")
            else:
                dotenv_file.touch()

            dotenv.set_key(dotenv_file, primary_key, setting_def.stringify_value(value))

        self.log(f"Set key '{primary_key}' in `.env`: {value!r}")
        return {"env_var": primary_key}

    def unset(self, name: str, path: List[str], setting_def=None):
        if not setting_def:
            raise StoreNotSupportedError

        env_vars = self.setting_env_vars(setting_def)
        env_keys = [var.key for var in env_vars]

        with self.update_dotenv() as dotenv_file:
            if not dotenv_file.exists():
                return {}

            for key in env_keys:
                dotenv.unset_key(dotenv_file, key)
                self.log(f"Unset key '{key}' in `.env`")

        return {}

    def reset(self):
        with self.update_dotenv() as dotenv_file:
            if dotenv_file.exists():
                dotenv_file.unlink()

        return {}

    @contextmanager
    def update_dotenv(self):
        try:
            with self.project.dotenv_update() as dotenv_file:
                yield dotenv_file
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err)

        self._env = None


class MeltanoYmlStoreManager(SettingsStoreManager):
    label = "`meltano.yml`"
    writable = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flat_config = None

    def ensure_supported(self, method="get"):
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    def get(self, name: str, setting_def=None):
        keys = [name]
        if setting_def:
            keys = [setting_def.name, *setting_def.aliases]

        flat_config = self.flat_config

        for key in keys:
            try:
                value = flat_config[key]
                self.log(f"Read key '{key}' from `meltano.yml`: {value!r}")
                return value, {"key": key, "expandable": True}
            except KeyError:
                pass

        return None, {}

    def set(self, name: str, path: List[str], value, setting_def=None):
        keys_to_unset = [name]
        if setting_def:
            keys_to_unset = [setting_def.name, *setting_def.aliases]

        paths_to_unset = [k for k in keys_to_unset if "." in k]

        if len(path) == 1:
            # No need to unset `name`,
            # since it will be overridden anyway
            keys_to_unset.remove(name)
        elif name.split(".") == path:
            # No need to unset `name` as path,
            # since it will be overridden anyway
            paths_to_unset.remove(name)

        with self.update_config() as config:
            for key in keys_to_unset:
                config.pop(key, None)
                self.log(f"Popped key '{key}' in `meltano.yml`")

            for path_to_unset in paths_to_unset:
                pop_at_path(config, path_to_unset, None)
                self.log(f"Popped path '{path_to_unset}' in `meltano.yml`")

            set_at_path(config, path, value)
            self.log(f"Set path '{path}' in `meltano.yml`: {value!r}")

        return {}

    def unset(self, name: str, path: List[str], setting_def=None):
        keys_to_unset = [name]
        if setting_def:
            keys_to_unset = [setting_def.name, *setting_def.aliases]

        paths_to_unset = [k for k in keys_to_unset if "." in k]

        with self.update_config() as config:
            for key in keys_to_unset:
                config.pop(key, None)
                self.log(f"Popped key '{key}' in `meltano.yml`")

            for path_to_unset in paths_to_unset:
                pop_at_path(config, path_to_unset, None)
                self.log(f"Popped path '{path_to_unset}' in `meltano.yml`")

            pop_at_path(config, path, None)
            self.log(f"Popped path '{path}' in `meltano.yml`")

        return {}

    def reset(self):
        with self.update_config() as config:
            config.clear()

        return {}

    @property
    def flat_config(self):
        if self._flat_config is None:
            self._flat_config = self.settings_service.flat_meltano_yml_config
        return self._flat_config

    @contextmanager
    def update_config(self):
        config = deepcopy(self.settings_service.meltano_yml_config)
        yield config

        try:
            self.settings_service.update_meltano_yml_config(config)
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err)

        self._flat_config = None

        # This is not quite the right place for this, but we need to create
        # setting defs for missing keys again when `meltano.yml` changes
        self.settings_service._setting_defs = None


class MeltanoEnvStoreManager(MeltanoYmlStoreManager):
    """Configuration stored in an environment within `meltano.yml`."""

    label = "`meltano_environment`"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_supported()

    @property
    def flat_config(self) -> Dict[str, Any]:
        """Get dictionary of flattened configuration."""
        if self._flat_config is None:
            self._flat_config = self.settings_service.environment_config
        return self._flat_config

    def ensure_supported(self, method="get"):
        """Ensure project is not read-only and an environment is active.

        Args:
            method: Setting method (get, set, etc.)

        Raises:
            StoreNotSupportedError: if the project is read-only or
            no environment is active.
        """
        super().ensure_supported(method)
        if self.settings_service.project.active_environment is None:
            raise StoreNotSupportedError(NoActiveEnvironment())

    @contextmanager
    def update_config(self):
        config = deepcopy(self.settings_service.environment_config)
        yield config

        try:
            self.settings_service.update_meltano_environment_config(config)
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err)

        self._flat_config = None

        # This is not quite the right place for this, but we need to create
        # setting defs for missing keys again when `meltano.yml` changes
        self.settings_service._setting_defs = None


class DbStoreManager(SettingsStoreManager):
    label = "the system database"
    writable = True

    def __init__(self, *args, bulk=False, session=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.session = session

        self.ensure_supported()

        self.bulk = bulk
        self._all_settings = None

    def ensure_supported(self, method="get"):
        if not self.session:
            raise StoreNotSupportedError("No database session provided")

    def get(self, name: str, setting_def=None):
        try:
            if self.bulk:
                value = self.all_settings[name]
            else:
                value = (
                    self.session.query(Setting)
                    .filter_by(namespace=self.namespace, name=name, enabled=True)
                    .one()
                    .value
                )

            self.log(f"Read key '{name}' from system database: {value!r}")
            return value, {}
        except (sqlalchemy.orm.exc.NoResultFound, KeyError):
            return None, {}

    def set(self, name: str, path: List[str], value, setting_def=None):
        setting = Setting(
            namespace=self.namespace, name=name, value=value, enabled=True
        )
        self.session.merge(setting)
        self.session.commit()

        self._all_settings = None

        self.log(f"Set key '{name}' in system database: {value!r}")
        return {}

    def unset(self, name: str, path: List[str], setting_def=None):
        self.session.query(Setting).filter_by(
            namespace=self.namespace, name=name
        ).delete()
        self.session.commit()

        self._all_settings = None

        self.log(f"Deleted key '{name}' from system database")
        return {}

    def reset(self):
        self.session.query(Setting).filter_by(namespace=self.namespace).delete()
        self.session.commit()

        self._all_settings = None

        return {}

    @property
    def namespace(self):
        return self.settings_service.db_namespace

    @property
    def all_settings(self):
        if self._all_settings is None:
            self._all_settings = {
                s.name: s.value
                for s in self.session.query(Setting)
                .filter_by(namespace=self.namespace, enabled=True)
                .all()
            }

        return self._all_settings


class InheritedStoreManager(SettingsStoreManager):
    """Store manager for settings inherited from a parent plugin."""

    label = "inherited"

    def __init__(self, settings_service, *args, bulk=False, **kwargs):
        """Initialize inherited store manager."""
        super().__init__(settings_service, *args, **kwargs)

        self._kwargs = {**kwargs, "expand_env_vars": False}

        self.bulk = bulk
        self._config_with_metadata = None

    def get(self, name: str, setting_def=None):
        if not setting_def:
            raise StoreNotSupportedError("Setting is missing")

        if not self.inherited_settings_service:
            raise StoreNotSupportedError("Inherited settings service is missing")

        value, metadata = self.get_with_metadata(setting_def.name)
        if value is None or metadata["source"] is SettingValueStore.DEFAULT:
            return None, {}

        self.log(f"Read key '{name}' from inherited: {value!r}")
        return value, {
            "inherited_source": metadata["source"],
            "expandable": metadata.get("expandable", False),
        }

    @property
    def inherited_settings_service(self):
        """Return settings service to inherit configuration from."""
        return self.settings_service.inherited_settings_service

    @property
    def config_with_metadata(self):
        """Return all inherited config and metadata."""
        if self._config_with_metadata is None:
            self._config_with_metadata = (
                self.inherited_settings_service.config_with_metadata(**self._kwargs)
            )
        return self._config_with_metadata

    def get_with_metadata(self, name):
        """Return inherited config and metadata for the named setting."""
        if self.bulk:
            metadata = self.config_with_metadata[name]
            return metadata["value"], metadata

        return self.inherited_settings_service.get_with_metadata(name, **self._kwargs)


class DefaultStoreManager(SettingsStoreManager):
    label = "the default"

    def get(self, name: str, setting_def=None):
        if not setting_def:
            raise StoreNotSupportedError("Setting is missing")

        value = setting_def.value
        if value is None:
            return None, {}

        self.log(f"Read key '{name}' from default: {value!r}")
        return value, {"expandable": True}


class AutoStoreManager(SettingsStoreManager):
    label = "the system database, `meltano.yml`, and `.env`"
    writable = True

    def __init__(self, *args, cache=True, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache = cache

        self._kwargs = {"settings_service": self.settings_service, **kwargs}

        self._managers = {}

    def manager_for(self, store: SettingValueStore) -> SettingsStoreManager:
        """Get setting store manager for this a value store.

        Args:
            store: A setting value store.

        Returns:
            Setting store manager.
        """
        if not self.cache or store not in self._managers:
            self._managers[store] = store.manager(**self._kwargs)
        return self._managers[store]

    @property
    def sources(self):
        sources = SettingValueStore.readables()
        sources.remove(SettingValueStore.AUTO)
        return sources

    @property
    def stores(self):
        stores = SettingValueStore.writables()
        stores.remove(SettingValueStore.AUTO)
        return stores

    def auto_store(  # noqa: WPS231 # Too complex
        self,
        name: str,
        source: SettingValueStore,
        setting_def: SettingDefinition = None,
    ):
        """Get first valid setting value store for a setting.

        Args:
            name: Setting name.
            source: Default setting value store.
            setting_def: Setting definition (kind, etc.). Defaults to None.
        """
        setting_def = setting_def or self.find_setting(name)

        store: SettingValueStore = source

        prefer_dotenv = (
            setting_def and (setting_def.is_redacted or setting_def.env_specific)
        ) or source is SettingValueStore.ENV

        tried = set()
        while True:
            try:
                manager = self.manager_for(store)
                manager.ensure_supported("set")
                return store
            except StoreNotSupportedError:
                tried.add(store)

                if SettingValueStore.MELTANO_ENV not in tried and not prefer_dotenv:
                    store = SettingValueStore.MELTANO_ENV
                    continue

                if SettingValueStore.MELTANO_YML not in tried and not prefer_dotenv:
                    store = SettingValueStore.MELTANO_YML
                    continue

                if SettingValueStore.DOTENV not in tried:
                    store = SettingValueStore.DOTENV
                    continue

                if SettingValueStore.DB not in tried:
                    store = SettingValueStore.DB
                    continue

                break

        return None

    def get(self, name: str, setting_def=None, **kwargs):
        setting_def = setting_def or self.find_setting(name)

        metadata = {}
        value = None

        for source in self.sources:
            try:
                manager = self.manager_for(source)
                value, metadata = manager.get(name, setting_def=setting_def, **kwargs)
            except StoreNotSupportedError:
                continue

            if value is not None:
                break

        metadata["source"] = source

        auto_store = self.auto_store(name, source, setting_def=setting_def)
        if auto_store:
            metadata["auto_store"] = auto_store
            metadata["overwritable"] = auto_store.can_overwrite(source)

        return value, metadata

    def set(self, name: str, path: List[str], value, setting_def=None):
        setting_def = setting_def or self.find_setting(name)

        current_value, metadata = self.get(name, setting_def=setting_def)
        source = metadata["source"]

        if value == current_value:
            # No need to do anything
            return {"store": source}

        if setting_def:
            if value == setting_def.value:
                # Unset everything so we fall down on default
                self.unset(name, path, setting_def=setting_def)

                return {"store": SettingValueStore.DEFAULT}

        store = self.auto_store(name, source, setting_def=setting_def)
        if store is None:
            raise StoreNotSupportedError("No storage method available")

        # May raise StoreNotSupportedError, but that's good.
        manager = self.manager_for(store)

        # Even if the global current value isn't equal,
        # the value in this store might be
        current_value, _ = manager.get(name, setting_def=setting_def)
        if value == current_value:
            # No need to do anything
            return {"store": store}

        metadata = manager.set(name, path, value, setting_def=setting_def)

        metadata["store"] = store
        return metadata

    def unset(self, name: str, path: List[str], setting_def=None):
        setting_def = setting_def or self.find_setting(name)

        error = None
        metadata = {}

        for store in self.stores:
            try:
                manager = self.manager_for(store)
                value, _ = manager.get(name, setting_def=setting_def)
            except StoreNotSupportedError:
                continue

            try:
                metadata = manager.unset(name, path, setting_def=setting_def)
                metadata["store"] = store
            except StoreNotSupportedError as err:
                # Only raise if we're sure we were going to unset something
                if value is not None:
                    error = err

        if error:
            raise error

        return metadata

    def reset(self):
        for store in self.stores:
            try:
                manager = self.manager_for(store)
                manager.reset()
            except StoreNotSupportedError:
                pass

        return {}

    def find_setting(self, name: str):
        try:
            return self.settings_service.find_setting(name)
        except SettingMissingError:
            return None
