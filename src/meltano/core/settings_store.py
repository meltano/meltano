import sqlalchemy
import logging
import dotenv
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from contextlib import contextmanager

from .utils import set_at_path, pop_at_path, expand_env_vars
from .error import Error
from .project import ProjectReadonly
from .setting import Setting
from .setting_definition import SettingMissingError

logger = logging.getLogger(__name__)


class StoreNotSupportedError(Error):
    pass


class SettingValueStore(str, Enum):
    CONFIG_OVERRIDE = "config_override"  # 0
    ENV = "env"  # 1
    DOTENV = "dotenv"  # 2
    MELTANO_YML = "meltano_yml"  # 3
    DB = "db"  # 4
    DEFAULT = "default"  # 5
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
            self.AUTO: AutoStoreManager,
        }
        return managers[self]

    @property
    def label(self):
        return self.manager.label

    @property
    def writable(self):
        return self.manager.writable

    def can_overwrite(self, source):
        if not self.writable:
            return False

        if source is self:
            return True

        stores_list = list(self.__class__)
        return stores_list.index(self) <= stores_list.index(source)


class SettingsStoreManager(ABC):
    readable = True
    writable = False

    def __init__(self, settings_service, **kwargs):
        self.settings_service = settings_service
        self.project = self.settings_service.project

    @abstractmethod
    def get(self, name: str):
        pass

    def set(self, name: str, path: List[str], value):
        raise NotImplementedError

    def unset(self, name: str, path: List[str]):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def ensure_supported(self, method="get"):
        if method != "get" and not self.writable:
            raise StoreNotSupportedError

    def find_setting(self, name: str):
        return self.settings_service.find_setting(name)

    def expand_env_vars(self, value):
        env = {**self.project.dotenv_env, **self.settings_service.env}

        expanded_value = expand_env_vars(value, env=env)
        if expanded_value == value:
            return value, {}

        return expanded_value, {"expanded": True, "unexpanded_value": value}


class ConfigOverrideStoreManager(SettingsStoreManager):
    label = "a command line flag"

    def get(self, name: str):
        try:
            value = self.settings_service.config_override[name]
            logger.debug(f"Read key '{name}' from config override: {value!r}")
            return value, {}
        except KeyError:
            return None, {}


class BaseEnvStoreManager(SettingsStoreManager):
    @property
    @abstractmethod
    def env(self):
        pass

    def ensure_supported(self, method="get"):
        if method == "get":
            self.find_setting()
        else:
            super().ensure_supported(method)

    def get(self, name: str):
        setting_def = self.find_setting(name)

        env_key = self.setting_env(setting_def)
        env_getters = {
            env_key: lambda env: env[env_key],
            **setting_def.env_alias_getters,
        }

        for key, getter in env_getters.items():
            try:
                value = getter(self.env)
                return value, {"env_var": key}
            except KeyError:
                pass

        return None, {}

    def setting_env(self, setting_def):
        return self.settings_service.setting_env(setting_def)

    def find_setting(self, *args):
        try:
            return super().find_setting(*args)
        except SettingMissingError:
            raise StoreNotSupportedError


class EnvStoreManager(BaseEnvStoreManager):
    label = "the environment"

    @property
    def env(self):
        return self.settings_service.env

    def get(self, *args):
        value, metadata = super().get(*args)

        if value is not None:
            env_key = metadata["env_var"]
            logger.debug(f"Read key '{env_key}' from the environment: {value!r}")

        return value, metadata


class DotEnvStoreManager(BaseEnvStoreManager):
    label = "`.env`"
    writable = True

    def ensure_supported(self, method="get"):
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    @property
    def env(self):
        return self.project.dotenv_env

    def get(self, name: str):
        value, metadata = super().get(name)

        if value is not None:
            env_key = metadata["env_var"]
            logger.debug(f"Read key '{env_key}' from `.env`: {value!r}")

        return value, metadata

    def set(self, name: str, path: List[str], value):
        setting_def = self.find_setting(name)
        env_key = self.setting_env(setting_def)

        with self.update_dotenv() as dotenv_file:
            if dotenv_file.exists():
                for key in setting_def.env_alias_getters.keys():
                    dotenv.unset_key(dotenv_file, key)
                    logger.debug(f"Unset key '{key}' in `.env`")
            else:
                dotenv_file.touch()

            dotenv.set_key(dotenv_file, env_key, str(value))

        logger.debug(f"Set key '{env_key}' in `.env`: {value!r}")
        return {"env_var": env_key}

    def unset(self, name: str, path: List[str]):
        setting_def = self.find_setting(name)
        env_key = self.setting_env(setting_def)

        with self.update_dotenv() as dotenv_file:
            if not dotenv_file.exists():
                return {}

            for key in [env_key, *setting_def.env_alias_getters.keys()]:
                dotenv.unset_key(dotenv_file, key)
                logger.debug(f"Unset key '{key}' in `.env`")

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


class MeltanoYmlStoreManager(SettingsStoreManager):
    label = "`meltano.yml`"
    writable = True

    def ensure_supported(self, method="get"):
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    def get(self, name: str):
        try:
            value = self.flat_config[name]
            value, metadata = self.expand_env_vars(value)

            logger.debug(f"Read key '{name}' from `meltano.yml`: {value!r}")
            return value, metadata
        except KeyError:
            return None, {}

    def set(self, name: str, path: List[str], value):
        with self.update_config() as config:
            if len(path) > 1:
                config.pop(name, None)
                logger.debug(f"Popped key '{name}' in `meltano.yml`")

            if name.split(".") != path:
                pop_at_path(config, name, None)
                logger.debug(f"Popped path '{name}' in `meltano.yml`")

            set_at_path(config, path, value)
            logger.debug(f"Set path '{path}' in `meltano.yml`: {value!r}")

        return {}

    def unset(self, name: str, path: List[str]):
        with self.update_config() as config:
            config.pop(name, None)
            logger.debug(f"Popped key '{name}' in `meltano.yml`")

            pop_at_path(config, name, None)
            logger.debug(f"Popped path '{name}' in `meltano.yml`")

            pop_at_path(config, path, None)
            logger.debug(f"Popped path '{path}' in `meltano.yml`")

        return {}

    def reset(self):
        with self.update_config() as config:
            config.clear()

        return {}

    @property
    def flat_config(self):
        return self.settings_service.flat_meltano_yml_config

    @contextmanager
    def update_config(self):
        yield self.settings_service._meltano_yml_config

        try:
            self.settings_service._update_meltano_yml_config()
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err)


class DbStoreManager(SettingsStoreManager):
    label = "the system database"
    writable = True

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.session = session

        self.ensure_supported()

    def ensure_supported(self, method="get"):
        if not self.session:
            raise StoreNotSupportedError("No database session provided")

    def get(self, name: str):
        try:
            value = (
                self.session.query(Setting)
                .filter_by(namespace=self.namespace, name=name, enabled=True)
                .one()
                .value
            )

            logger.debug(f"Read key '{name}' from system database: {value!r}")
            return value, {}
        except sqlalchemy.orm.exc.NoResultFound:
            return None, {}

    def set(self, name: str, path: List[str], value):
        setting = Setting(
            namespace=self.namespace, name=name, value=value, enabled=True
        )
        self.session.merge(setting)
        self.session.commit()

        logger.debug(f"Set key '{name}' in system database: {value!r}")
        return {}

    def unset(self, name: str, path: List[str]):
        self.session.query(Setting).filter_by(
            namespace=self.namespace, name=name
        ).delete()
        self.session.commit()

        logger.debug(f"Deleted key '{name}' from system database")
        return {}

    def reset(self):
        self.session.query(Setting).filter_by(namespace=self.namespace).delete()
        self.session.commit()

        return {}

    @property
    def namespace(self):
        return self.settings_service._db_namespace


class DefaultStoreManager(SettingsStoreManager):
    label = "the default"

    def get(self, name: str):
        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            raise StoreNotSupportedError("Setting is missing")

        value = setting_def.value

        value, metadata = self.expand_env_vars(value)

        logger.debug(f"Read key '{name}' from default: {value!r}")
        return value, metadata


class AutoStoreManager(SettingsStoreManager):
    label = "the system database, `meltano.yml`, and `.env`"
    writable = True

    def __init__(self, *args, force=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.force_set = force

        self._kwargs = {"settings_service": self.settings_service, **kwargs}

    def manager_for(self, store):
        return store.manager(**self._kwargs)

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

    def auto_store(self, name, source):
        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            setting_def = None

        store = source

        tried = set()
        while True:
            try:
                manager = self.manager_for(store)
                manager.ensure_supported("set")
                return store
            except StoreNotSupportedError:
                tried.add(store)

                prefer_dotenv = (
                    setting_def
                    and (setting_def.is_redacted or setting_def.env_specific)
                ) or source is SettingValueStore.ENV

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

    def get(self, name: str):
        metadata = {}
        value = None

        for source in self.sources:
            try:
                manager = self.manager_for(source)
                value, metadata = manager.get(name)
            except StoreNotSupportedError:
                continue

            if value is not None:
                break

        metadata["source"] = source

        auto_store = self.auto_store(name, source)
        if auto_store:
            metadata["auto_store"] = auto_store
            metadata["overwritable"] = auto_store.can_overwrite(source)

        return value, metadata

    def set(self, name: str, path: List[str], value):
        current_value, metadata = self.get(name)
        source = metadata["source"]

        if value == current_value and not self.force_set:
            # No need to do anything
            return {"store": source}

        try:
            setting_def = self.find_setting(name)

            if value == setting_def.value:
                # Unset everything so we fall down on default
                self.unset(name, path)

                return {"store": SettingValueStore.DEFAULT}
        except SettingMissingError:
            setting_def = None

        store = self.auto_store(name, source)
        if store is None:
            raise StoreNotSupportedError("No storage method available")

        # May raise StoreNotSupportedError, but that's good.
        manager = self.manager_for(store)

        # Even if the global current value isn't equal,
        # the value in this store might be
        current_value, _ = manager.get(name)
        if value == current_value:
            # No need to do anything
            return {"store": store}

        metadata = manager.set(name, path, value)

        metadata["store"] = store
        return metadata

    def unset(self, name: str, path: List[str]):
        error = None
        metadata = {}

        for store in self.stores:
            try:
                manager = self.manager_for(store)
                value, _ = manager.get(name)
            except StoreNotSupportedError:
                continue

            if value is None:
                continue

            try:
                metadata = manager.unset(name, path)
                metadata["store"] = store
            except StoreNotSupportedError as err:
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
