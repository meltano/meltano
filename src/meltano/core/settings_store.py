"""Storage Managers for Meltano Configuration."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from enum import Enum
from functools import reduce
from operator import eq
from typing import TYPE_CHECKING, Any

import dotenv
import sqlalchemy
from sqlalchemy.orm import Session

from meltano.core.environment import NoActiveEnvironment
from meltano.core.error import Error
from meltano.core.project import ProjectReadonly
from meltano.core.setting import Setting
from meltano.core.setting_definition import SettingDefinition, SettingMissingError
from meltano.core.utils import flatten, pop_at_path, set_at_path

if TYPE_CHECKING:
    from meltano.core.settings_service import SettingsService


logger = logging.getLogger(__name__)


class ConflictingSettingValueException(Exception):  # noqa: N818
    """Occurs when a setting has multiple conflicting values via aliases."""

    def __init__(self, setting_names):
        """Instantiate the error.

        Args:
            setting_names: the name/aliases where conflicting values are set

        """
        self.setting_names = setting_names
        super().__init__(setting_names)

    def __str__(self) -> str:
        """Represent the error as a string.

        Returns:
            string representation of the error
        """
        return f"Conflicting values for setting found in: {self.setting_names}"


class MultipleEnvVarsSetException(Exception):  # noqa: N818
    """Occurs when a setting value is set via multiple environment variable names."""

    def __init__(self, names):
        """Instantiate the error.

        Args:
            names: the name/aliases where conflicting values are set
        """
        self.names = names
        super().__init__(names)

    def __str__(self) -> str:
        """Represent the error as a string.

        Returns:
            string representation of the error
        """
        return (
            f"Error: Setting value set via multiple environment variables: {self.names}"
        )


class StoreNotSupportedError(Error):
    """Error raised when write actions are performed on a Store that is not writable."""


class SettingValueStore(str, Enum):
    """Setting Value Store.

    Note: The declaration order of stores determins store precedence when using the Auto store manager.
            This is because the `.readables()` and `.writables()` methods return ordered lists that
            the Auto store manager iterates over when retrieveing setting values.
    """

    CONFIG_OVERRIDE = "config_override"
    ENV = "env"
    DOTENV = "dotenv"
    MELTANO_ENV = "meltano_environment"
    MELTANO_YML = "meltano_yml"
    DB = "db"
    INHERITED = "inherited"
    DEFAULT = "default"
    AUTO = "auto"

    @classmethod
    def readables(cls) -> list[SettingValueStore]:
        """Return list of readable SettingValueStore instances.

        Returns:
            An list of readable stores in order of precedence.
        """
        return list(cls)

    @classmethod
    def writables(cls) -> list[SettingValueStore]:
        """Return list of writable SettingValueStore instances.

        Returns:
            An list of writable stores in order of precedence.
        """
        return [store for store in cls if store.writable]

    @property
    def manager(self) -> SettingsStoreManager:
        """Return store manager for this store.

        Returns:
            SettingsStoreManager for this store.
        """
        managers = {  # ordering here is not significant, other than being consistent with the order of precedence.
            self.CONFIG_OVERRIDE: ConfigOverrideStoreManager,
            self.ENV: EnvStoreManager,
            self.DOTENV: DotEnvStoreManager,
            self.MELTANO_ENV: MeltanoEnvStoreManager,
            self.MELTANO_YML: MeltanoYmlStoreManager,
            self.DB: DbStoreManager,
            self.INHERITED: InheritedStoreManager,
            self.DEFAULT: DefaultStoreManager,
            self.AUTO: AutoStoreManager,
        }
        return managers[self]

    @property
    def label(self) -> str:
        """Return printable label.

        Returns:
            Printable label.
        """
        return self.manager.label

    @property
    def writable(self) -> bool:
        """Return if this store is writeable.

        Returns:
            True if store is writable.
        """
        return self.manager.writable

    def overrides(self, source: SettingValueStore) -> bool:
        """Check if given source overrides this instance.

        Args:
            source: SettingValueStore to compare against.

        Returns:
            True if given source takes precedence over this store.
        """
        stores_list = list(self.__class__)
        return stores_list.index(self) < stores_list.index(source)

    def can_overwrite(self, source: SettingValueStore) -> bool:
        """Check if source can overwrite.

        Args:
            source: SettingValueStore instance to check.

        Returns:
            True if instance is overwritable.
        """
        return self.writable and (source is self or self.overrides(source))


class SettingsStoreManager(ABC):
    """Base settings store manager."""

    readable = True
    writable = False

    def __init__(self, settings_service: SettingsService, **kwargs):
        """Initialise settings store manager.

        Args:
            settings_service: SettingsService instance.
            kwargs: Keyword arguments.
        """
        self.settings_service = settings_service
        self.project = self.settings_service.project

    @abstractmethod
    def get(self, name: str, setting_def: SettingDefinition | None = None) -> None:
        """Abstract get method.

        Args:
            name: Setting name.
            setting_def: SettingDefinition instance.
        """

    def set(
        self,
        name: str,
        path: list[str],
        value: Any,
        setting_def: SettingDefinition | None = None,
    ) -> None:
        """Unimplemented set method.

        Args:
            name: Setting name.
            path: Setting path.
            value: New value to set.
            setting_def: SettingDefinition instance.

        Raises:
            NotImplementedError: always.
        """
        raise NotImplementedError

    def unset(
        self,
        name: str,
        path: list[str],
        setting_def: SettingDefinition | None = None,
    ) -> None:
        """Unimplemented unset method.

        Args:
            name: Setting name.
            path: Setting path.
            setting_def: SettingDefinition instance.

        Raises:
            NotImplementedError: always.
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Unimplemented reset method.

        Raises:
            NotImplementedError: always.
        """
        raise NotImplementedError

    def ensure_supported(self, method: str = "get") -> None:
        """Ensure passed method is supported.

        Args:
            method: Method to check if supported.

        Raises:
            StoreNotSupportedError: if method is not "get" a store is not writable.
        """
        if method != "get" and not self.writable:
            raise StoreNotSupportedError

    def log(self, message: str) -> None:
        """Log method.

        Args:
            message: message to log.
        """
        self.settings_service.log(message)


class ConfigOverrideStoreManager(SettingsStoreManager):
    """Config override store manager."""

    label = "a command line flag"

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get value by name from the .env file.

        Args:
            name: Setting name.
            setting_def: Unused. Included to match parent class method signature.

        Returns:
            A tuple the got value and an empty dictionary.
        """
        try:
            value = self.settings_service.config_override[name]
            self.log(f"Read key '{name}' from config override: {value!r}")
            return value, {}
        except KeyError:
            return None, {}


class BaseEnvStoreManager(SettingsStoreManager):
    """Base terminal environment store manager."""

    @property
    @abstractmethod
    def env(self):
        """Abstract environment values property."""

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get value by name from the .env file.

        Args:
            name: Unused. Included to match parent class method signature.
            setting_def: SettingDefinition instance.

        Raises:
            StoreNotSupportedError: if setting_def not passed.
            ConflictingSettingValueException: if multiple conflicting values for the
                same setting are provided.
            MultipleEnvVarsSetException: if multiple environment variables are set for
                the same setting.

        Returns:
            A tuple the got value and a dictionary containing metadata.
        """
        if not setting_def:
            raise StoreNotSupportedError

        vals_with_metadata = []
        for env_var in self.setting_env_vars(setting_def):
            try:
                value = env_var.get(self.env)
                vals_with_metadata.append((value, {"env_var": env_var.key}))
            except KeyError:
                pass

        if len(vals_with_metadata) > 1:
            if reduce(eq, (val for val, _ in vals_with_metadata)):
                raise MultipleEnvVarsSetException(
                    [metadata["env_var"] for _, metadata in vals_with_metadata]
                )
            raise ConflictingSettingValueException(
                [metadata["env_var"] for _, metadata in vals_with_metadata]
            )

        return vals_with_metadata[0] if vals_with_metadata else (None, {})

    def setting_env_vars(self, *args, **kwargs) -> dict:
        """Return setting environment variables.

        Args:
            args: Positional arguments to pass to setting_service setting_env_vars method.
            kwargs: Keyword arguments to pass to setting_service setting_env_vars method.

        Returns:
            A dictionary of setting environment variables.
        """
        return self.settings_service.setting_env_vars(*args, **kwargs)


class EnvStoreManager(BaseEnvStoreManager):
    """Terminal environment store manager."""

    label = "the environment"

    @property
    def env(self):
        """Return values from the calling terminals environment.

        Returns:
            Values found in the calling terminals environment.
        """
        return self.settings_service.env

    def get(self, *args, **kwargs):
        """Get value by name from the .env file.

        Args:
            args: Positional arguments to pass to parent method.
            kwargs: Keyword arguments to pass to parent method.

        Returns:
            A tuple the got value and a dictionary containing metadata.
        """
        value, metadata = super().get(*args, **kwargs)

        if value is not None:
            env_key = metadata["env_var"]
            self.log(f"Read key '{env_key}' from the environment: {value!r}")

        return value, metadata


class DotEnvStoreManager(BaseEnvStoreManager):
    """.env file store manager."""

    label = "`.env`"
    writable = True

    def __init__(self, *args, **kwargs):
        """Initialise a .env file store manager instance.

        Args:
            args: Positional arguments to pass to parent class.
            kwargs: Keyword arguments to pass to parent class.
        """
        super().__init__(*args, **kwargs)
        self._env = None

    def ensure_supported(self, method: str = "get") -> None:
        """Ensure named method is supported and project is not read-only and the passed method is supported.

        Args:
            method: Setting method (get, set, etc.)

        Raises:
            StoreNotSupportedError: if the project is read-only or named method is not "get".
        """
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    @property
    def env(self) -> dict:
        """Return values from the .env file.

        Returns:
            A dictionary of values found in the .env file.
        """
        if self._env is None:
            self._env = self.project.dotenv_env
        return self._env

    def get(self, *args, **kwargs) -> tuple[str, dict]:
        """Get value by name from the .env file.

        Args:
            args: Positional arguments to pass to parent method.
            kwargs: Keyword arguments to pass to parent method.

        Returns:
            A tuple the got value and a dictionary containing metadata.
        """
        value, metadata = super().get(*args, **kwargs)

        if value is not None:
            env_key = metadata["env_var"]
            self.log(f"Read key '{env_key}' from `.env`: {value!r}")

        return value, metadata

    def set(self, name: str, path: list[str], value, setting_def=None):
        """Set value by name in the .env file.

        Args:
            name: Unused. Included to match parent class method signature.
            path: Unused. Included to match parent class method signature.
            value: New value to set.
            setting_def: SettingDefinition.

        Raises:
            StoreNotSupportedError: if setting_def not provided.

        Returns:
            An empty dictionary.
        """
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

    def unset(
        self,
        name: str,
        path: list[str],
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Unset value by SettingDefinition in the .env file.

        Args:
            name: Unused. Included to match parent class method signature.
            path: Unused. Included to match parent class method signature.
            setting_def: SettingDefinition instance.

        Returns:
            An empty dictionary.

        Raises:
            StoreNotSupportedError: if setting_def not passed.
        """
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

    def reset(self) -> dict:
        """Reset all Setting values in this store.

        Returns:
            An empty dictionary.
        """
        with self.update_dotenv() as dotenv_file:
            if dotenv_file.exists():
                dotenv_file.unlink()

        return {}

    @contextmanager
    def update_dotenv(self):
        """Update .env configuration.

        Yields:
            A copy of the current .env configuration dict.

        Raises:
            StoreNotSupportedError: if the project is in read-only mode.
        """
        try:
            with self.project.dotenv_update() as dotenv_file:
                yield dotenv_file
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err) from err

        self._env = None


class MeltanoYmlStoreManager(SettingsStoreManager):
    """Meltano.yml Store Manager."""

    label = "`meltano.yml`"
    writable = True

    def __init__(self, *args, **kwargs):
        """Initialise MeltanoYmlStoreManager instance.

        Args:
            args: Positional arguments to pass to parent class.
            kwargs: Keyword arguments to pass to parent class.
        """
        super().__init__(*args, **kwargs)
        self._flat_config = None

    def ensure_supported(self, method: str = "get") -> None:
        """Ensure named method is supported and project is not read-only and an environment is active.

        Args:
            method: Setting method (get, set, etc.)

        Raises:
            StoreNotSupportedError: if the project is read-only or named method is not "get".
        """
        if method != "get" and self.project.readonly:
            raise StoreNotSupportedError(ProjectReadonly())

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get value by name from the system database.

        Args:
            name: Setting name.
            setting_def: SettingDefinition.

        Returns:
            A tuple the got value and a dictionary containing metadata.

        Raises:
            ConflictingSettingValueException: if multiple conflicting values for the same setting are provided.
        """
        keys = [setting_def.name, *setting_def.aliases] if setting_def else [name]
        flat_config = self.flat_config
        vals_with_metadata = []
        for key in keys:
            try:
                value = flat_config[key]
            except KeyError:
                continue

            self.log(f"Read key '{key}' from `meltano.yml`: {value!r}")
            vals_with_metadata.append((value, {"key": key, "expandable": True}))

        if len(vals_with_metadata) > 1 and not reduce(
            eq, (val for val, _ in vals_with_metadata)
        ):
            raise ConflictingSettingValueException(
                metadata["key"] for _, metadata in vals_with_metadata
            )

        return vals_with_metadata[0] if vals_with_metadata else (None, {})

    def set(
        self,
        name: str,
        path: list[str],
        value: Any,
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Set value by name in the Meltano YAML File.

        Args:
            name: Setting name.
            path: Setting path.
            value: New value to set.
            setting_def: SettingDefinition.

        Returns:
            An empty dictionary.
        """
        keys_to_unset = (
            [setting_def.name, *setting_def.aliases] if setting_def else [name]
        )
        paths_to_unset = [key for key in keys_to_unset if "." in key]

        if len(path) == 1:
            # No need to unset `name`, since it will be overridden anyway
            keys_to_unset.remove(name)
        elif name.split(".") == path:
            # No need to unset `name` as path, since it will be overridden anyway
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

    def unset(
        self,
        name: str,
        path: list[str],
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Unset value by name in the Meltano YAML file.

        Args:
            name: Setting name.
            path: Setting path.
            setting_def: SettingDefinition instance.

        Returns:
            An empty dictionary.
        """
        keys_to_unset = [name]
        if setting_def:
            keys_to_unset = [setting_def.name, *setting_def.aliases]

        paths_to_unset = [key for key in keys_to_unset if "." in key]

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

    def reset(self) -> dict:
        """Reset all Setting values in this store.

        Returns:
            An empty dictionary.
        """
        with self.update_config() as config:
            config.clear()
        return {}

    @property
    def flat_config(self) -> dict:
        """Get dictionary of flattened configuration.

        Returns:
            A dictionary of flattened configuration.
        """
        if self._flat_config is None:
            self._flat_config = self.settings_service.flat_meltano_yml_config
        return self._flat_config

    @contextmanager
    def update_config(self):
        """Update Meltano YAML configuration.

        Yields:
            A copy of the current YAML configuration dict.

        Raises:
            StoreNotSupportedError: if the project is in read-only mode.
        """
        config = deepcopy(self.settings_service.meltano_yml_config)
        yield config

        try:
            self.settings_service.update_meltano_yml_config(config)
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err) from err

        self._flat_config = None

        # This is not quite the right place for this, but we need to create
        # setting defs for missing keys again when `meltano.yml` changes
        self.settings_service._setting_defs = None  # noqa: WPS437


class MeltanoEnvStoreManager(MeltanoYmlStoreManager):
    """Configuration stored in an environment within `meltano.yml`."""

    label = "the active environment in `meltano.yml`"

    def __init__(self, *args, **kwargs):
        """Initialise MeltanoEnvStoreManager instance.

        Args:
            args: Positional arguments to pass to parent class.
            kwargs: Keyword arguments to pass to parent class.
        """
        super().__init__(*args, **kwargs)
        self.ensure_supported()

    @property
    def flat_config(self) -> dict[str, Any]:
        """Get dictionary of flattened configuration.

        Returns:
            A dictionary of flattened configuration.
        """
        if self._flat_config is None:
            self._flat_config = flatten(self.settings_service.environment_config, "dot")
        return self._flat_config

    def ensure_supported(self, method: str = "get"):
        """Ensure project is not read-only and an environment is active.

        Args:
            method: Setting method (get, set, etc.)

        Raises:
            StoreNotSupportedError: if the project is read-only or no environment is active.
        """
        super().ensure_supported(method)
        if not self.settings_service.supports_environments:
            raise StoreNotSupportedError(
                "Project config cannot be stored in an Environment."
            )
        if self.settings_service.project.active_environment is None:
            raise StoreNotSupportedError(NoActiveEnvironment())

    @contextmanager
    def update_config(self) -> None:
        """Update Meltano Environment configuration.

        Yields:
            A copy of the current environment configuration dict.

        Raises:
            StoreNotSupportedError: if the project is in read-only mode.
        """
        config = deepcopy(self.settings_service.environment_config)
        yield config

        try:
            self.settings_service.update_meltano_environment_config(config)
        except ProjectReadonly as err:
            raise StoreNotSupportedError(err) from err

        self._flat_config = None

        # This is not quite the right place for this, but we need to create
        # setting defs for missing keys again when `meltano.yml` changes
        self.settings_service._setting_defs = None  # noqa: WPS437


class DbStoreManager(SettingsStoreManager):
    """Store manager for settings stored in the system database."""

    label = "the system database"
    writable = True

    def __init__(
        self, *args, bulk: bool = False, session: Session | None = None, **kwargs
    ):
        """Initialise DbStoreManager.

        Args:
            args: Positional arguments to pass to parent class.
            bulk:  Flag to determine whether parent metadata is returned alongside child.
            session: SQLAlchemy Session to use when querying the system database.
            kwargs: Keyword arguments to pass to parent class.
        """
        super().__init__(*args, **kwargs)
        self.session = session
        self.ensure_supported()
        self.bulk = bulk
        self._all_settings = None

    def ensure_supported(self, method: str = "get") -> None:
        """Return True if passed method is supported by this store.

        Args:
            method: Unused. Included to match parent class method signature.

        Raises:
            StoreNotSupportedError: if database session is not provided.
        """
        if not self.session:
            raise StoreNotSupportedError("No database session provided")

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get value by name from the system database.

        Args:
            name: Setting name.
            setting_def: Unused. Included to match parent class method signature.

        Returns:
            A tuple the got value and an empty dictionary.
        """
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

    def set(
        self,
        name: str,
        path: list[str],
        value: Any,
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Set value by name in the system database.

        Args:
            name: Setting name.
            path: Unused. Included to match parent class method signature.
            value: New value to set.
            setting_def: Unused. Included to match parent class method signature.

        Returns:
            An empty dictionary.
        """
        setting = Setting(
            namespace=self.namespace, name=name, value=value, enabled=True
        )
        self.session.merge(setting)
        self.session.commit()

        self._all_settings = None

        self.log(f"Set key '{name}' in system database: {value!r}")
        return {}

    def unset(
        self,
        name: str,
        path: list[str],
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Unset value by name in the system database store.

        Args:
            name: Setting name.
            path: Unused. Included to match parent class method signature.
            setting_def: Unused. Included to match parent class method signature.

        Returns:
            An empty dictionary.
        """
        self.session.query(Setting).filter_by(
            namespace=self.namespace, name=name
        ).delete()
        self.session.commit()

        self._all_settings = None

        self.log(f"Deleted key '{name}' from system database")
        return {}

    def reset(self) -> dict:
        """Reset all Setting values in this store.

        Returns:
            An empty dictionary.
        """
        self.session.query(Setting).filter_by(namespace=self.namespace).delete()
        self.session.commit()

        self._all_settings = None

        return {}

    @property
    def namespace(self) -> str:
        """Return the current SettingService namespace.

        Returns:
            The current SettingService namespace
        """
        return self.settings_service.db_namespace

    @property
    def all_settings(self) -> dict[str, Setting]:
        """
        Fetch all settings from the system database for this namespace that are enabled.

        Returns:
            A dictionary of Setting models.
        """
        if self._all_settings is None:
            self._all_settings = {
                setting.name: setting.value
                for setting in self.session.query(Setting)
                .filter_by(namespace=self.namespace, enabled=True)
                .all()
            }
        return self._all_settings


class InheritedStoreManager(SettingsStoreManager):
    """Store manager for settings inherited from a parent plugin."""

    label = "inherited"

    def __init__(
        self, settings_service: SettingsService, *args, bulk: bool = False, **kwargs
    ):
        """Initialize inherited store manager.

        Args:
            settings_service: SettingsService instance.
            args: Positional arguments to pass to parent class.
            bulk: Flag to determine whether parent metadata is returned alongside child.
            kwargs: Keyword arguments to pass to parent class.
        """
        super().__init__(settings_service, *args, **kwargs)
        self._kwargs = {**kwargs, "expand_env_vars": False}
        self.bulk = bulk
        self._config_with_metadata = None

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get a Setting value by name and SettingDefinition.

        Args:
            name: Setting name.
            setting_def: SettingDefinition.

        Returns:
            A tuple containing the got value and accompanying metadata dictionary.

        Raises:
            StoreNotSupportedError: if no setting_def is passed.
        """
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
    def inherited_settings_service(self) -> SettingsService:
        """Return settings service to inherit configuration from.

        Returns:
            A SettingsService to inherit configuration from.
        """
        return self.settings_service.inherited_settings_service

    @property
    def config_with_metadata(self) -> dict:
        """Return all inherited config and metadata.

        Returns:
            A dictionary containing config and metadata.
        """
        if self._config_with_metadata is None:
            self._config_with_metadata = (
                self.inherited_settings_service.config_with_metadata(**self._kwargs)
            )
        return self._config_with_metadata

    def get_with_metadata(self, name: str) -> tuple[str, dict]:
        """Return inherited config and metadata for the named setting.

        Args:
            name: Setting name.

        Returns:
            A tuple containing the got value and accompanying metadata dictionary.
        """
        if self.bulk:
            metadata = self.config_with_metadata[name]
            return metadata["value"], metadata

        return self.inherited_settings_service.get_with_metadata(name, **self._kwargs)


class DefaultStoreManager(SettingsStoreManager):
    """Store manager for defaults supplied by the SettingDefinition."""

    label = "the default"

    def get(
        self, name: str, setting_def: SettingDefinition | None = None
    ) -> tuple[str, dict]:
        """Get a Setting value by name and SettingDefinition.

        Args:
            name: Setting name.
            setting_def: SettingDefinition.

        Returns:
            A tuple containing the got value and accompanying metadata dictionary.
        """
        value = None
        metadata = {}
        if setting_def:
            value = setting_def.value
            if value is not None:
                self.log(f"Read key '{name}' from default: {value!r}")
                return value, {"expandable": True}
        # As default is lowest in our order of precedence, we want it to always return
        # a value, even if it is None.
        return value, metadata


class AutoStoreManager(SettingsStoreManager):
    """Automatic store manager, for determining the appropriate store based on current context."""

    label = "the system database, `meltano.yml`, and `.env`"
    writable = True

    def __init__(self, *args, cache: bool = True, **kwargs):
        """Initialise AutoStoreManager.

        Args:
            args: Positional arguments to pass to parent class.
            cache: Cache store manager instances for fast retrieval.
            kwargs: Keyword arguments to pass to parent class.
        """
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
    def sources(self) -> list[SettingValueStore]:
        """Return a list of readable SettingValueStore.

        Returns:
            A list of readable SettingValueStore
        """
        sources = SettingValueStore.readables()
        sources.remove(SettingValueStore.AUTO)
        return sources

    @property
    def stores(self) -> list[SettingValueStore]:
        """Return a list of writable SettingValueStore.

        Returns:
            A list of writable SettingValueStore
        """
        stores = SettingValueStore.writables()
        stores.remove(SettingValueStore.AUTO)
        return stores

    def ensure_supported(self, store, method="set"):
        """Return if a given store is supported for the given method.

        Args:
            store: The store to check.
            method: The method to check for the given store.

        Returns:
            True if store supports method.
        """
        try:
            manager = self.manager_for(store)
            manager.ensure_supported(method)
            return True
        except StoreNotSupportedError:
            return False

    def auto_store(  # noqa: WPS231 # Too complex
        self,
        name: str,
        setting_def: SettingDefinition | None = None,
    ) -> SettingValueStore | None:
        """Get first valid writable SettingValueStore instance for a Setting.

        Args:
            name: Setting name.
            setting_def: SettingDefinition. If None is passed, one will be discovered using `self.find_setting(name)`.

        Returns:
            A SettingValueStore, if found, else None.
        """
        setting_def = setting_def or self.find_setting(name)

        # only the system database is available in readonly mode
        if self.project.readonly:
            if self.ensure_supported(store=SettingValueStore.DB):
                return SettingValueStore.DB
            return None

        # value is a secret
        if setting_def and setting_def.is_redacted:
            if self.ensure_supported(store=SettingValueStore.DOTENV):
                return SettingValueStore.DOTENV
            elif self.ensure_supported(store=SettingValueStore.DB):
                return SettingValueStore.DB
            # ensure secrets don't leak into other stores
            return None

        # value is env-specific
        if setting_def and setting_def.env_specific:
            if self.ensure_supported(store=SettingValueStore.DOTENV):
                return SettingValueStore.DOTENV

        # no active meltano environment
        if not self.project.active_environment:
            # return root `meltano.yml`
            if self.ensure_supported(store=SettingValueStore.MELTANO_YML):
                return SettingValueStore.MELTANO_YML
            # fall back to dotenv
            elif self.ensure_supported(store=SettingValueStore.DOTENV):
                return SettingValueStore.DOTENV
            # fall back to meltano system db
            elif self.ensure_supported(store=SettingValueStore.DB):
                return SettingValueStore.DB
            return None

        # any remaining config routed to meltano environment
        if self.ensure_supported(store=SettingValueStore.MELTANO_ENV):
            return SettingValueStore.MELTANO_ENV
        # fall back to root `meltano.yml`
        # this is required for Meltano settings, which cannot be stored in an Environment
        if self.ensure_supported(store=SettingValueStore.MELTANO_YML):
            return SettingValueStore.MELTANO_YML
        # fall back to dotenv
        elif self.ensure_supported(store=SettingValueStore.DOTENV):
            return SettingValueStore.DOTENV
        # fall back to meltano system db
        elif self.ensure_supported(store=SettingValueStore.DB):
            return SettingValueStore.DB
        return None

    def get(
        self, name: str, setting_def: SettingDefinition | None = None, **kwargs
    ) -> tuple[str, dict]:
        """Get a Setting value by name and SettingDefinition.

        Args:
            name: Setting name.
            setting_def: SettingDefinition. If none is passed, one will be discovered using `self.find_setting(name)`.
            kwargs: Additional keword arguments to pass to `manager.get()`

        Returns:
            A tuple containing the got value and accompanying metadata dictionary.
        """
        setting_def = setting_def or self.find_setting(name)

        metadata = {}
        value = None
        found_source = None

        for source in self.sources:
            try:
                manager = self.manager_for(source)
            except StoreNotSupportedError:
                continue

            try:
                value, metadata = manager.get(name, setting_def=setting_def, **kwargs)
            except StoreNotSupportedError:
                continue

            found_source = source

            if value is not None:
                break

        metadata["source"] = found_source

        auto_store = self.auto_store(name, setting_def=setting_def)
        if auto_store:
            metadata["auto_store"] = auto_store
            metadata["overwritable"] = auto_store.can_overwrite(found_source)

        return value, metadata

    def set(self, name: str, path: list[str], value, setting_def=None) -> dict:
        """Set a Setting by name, path and (optionally) SettingDefinition.

        Args:
            name: Setting name.
            path: Setting path.
            value: New Setting value.
            setting_def: SettingDefinition. If none is passed, one will be discovered using `self.find_setting(name)`.

        Returns:
            A dictionary of metadata pertaining to the set operation.

        Raises:
            StoreNotSupportedError: exception encountered when attempting to write to store.
        """
        setting_def = setting_def or self.find_setting(name)
        store = self.auto_store(name, setting_def=setting_def)
        logger.debug(f"AutoStoreManager returned store '{store}'")
        if store is None:
            raise StoreNotSupportedError("No storage method available")

        # May raise StoreNotSupportedError, but that's good.
        manager = self.manager_for(store)
        metadata = manager.set(name, path, value, setting_def=setting_def)
        metadata["store"] = store
        return metadata

    def unset(
        self,
        name: str,
        path: list[str],
        setting_def: SettingDefinition | None = None,
    ) -> dict:
        """Unset value, by name, path and SettingDefinition, in all stores.

        Args:
            name: Setting name.
            path: Setting path.
            setting_def: SettingDefinition. If none is passed, one will be discovered using `self.find_setting(name)`.

        Returns:
            A metadata dictionary containing details of the last value unset.

        Raises:
            error: exception encountered when trying to write to a store.
        """
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

    def reset(self) -> dict:
        """Reset all stores.

        Returns:
            An empty dictionary.
        """
        for store in self.stores:
            try:
                manager = self.manager_for(store)
                manager.reset()
            except StoreNotSupportedError:
                pass

        return {}

    def find_setting(self, name: str) -> SettingDefinition | None:
        """Find a setting by name.

        Args:
            name: Name of the Setting to find.

        Returns:
            A matching SettingDefinition, if found, else None.
        """
        try:
            return self.settings_service.find_setting(name)
        except SettingMissingError:
            return None
