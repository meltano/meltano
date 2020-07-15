import sqlalchemy
import logging
import dotenv
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from contextlib import contextmanager

from .utils import set_at_path, pop_at_path, expand_env_vars
from .error import Error
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
        expanded_value = expand_env_vars(value, env=self.settings_service.env)
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

    @property
    def env(self):
        return dotenv.dotenv_values(self.project.dotenv)

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
        with self.project.dotenv_update() as dotenv_file:
            yield dotenv_file


class MeltanoYmlStoreManager(SettingsStoreManager):
    label = "`meltano.yml`"
    writable = True

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

        self.settings_service._update_meltano_yml_config()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._kwargs = {"settings_service": self.settings_service, **kwargs}

    @property
    def sources(self):
        sources = SettingValueStore.readables()
        sources.remove(SettingValueStore.AUTO)
        return sources

    def get(self, name: str):
        metadata = {}
        value = None

        for source in self.sources:
            try:
                manager = source.manager(**self._kwargs)
                value, metadata = manager.get(name)
            except StoreNotSupportedError:
                continue

            if value is not None:
                break

        metadata["source"] = source
        return value, metadata
