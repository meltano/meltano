"""Module for managing settings."""
from __future__ import annotations

import logging
import os
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Generator, Iterable

from meltano.core.project import Project
from meltano.core.utils import expand_env_vars as do_expand_env_vars
from meltano.core.utils import flatten

from .setting_definition import SettingDefinition, SettingKind, SettingMissingError
from .settings_store import SettingValueStore

logger = logging.getLogger(__name__)


# sentinel value to use to prevent leaking sensitive data
REDACTED_VALUE = "(redacted)"

# magic string used as feature flag setting for experimental features
EXPERIMENTAL = "experimental"
FEATURE_FLAG_PREFIX = "ff"


class FeatureFlags(Enum):
    """Available Meltano Feature Flags."""

    ENABLE_UVICORN = "enable_uvicorn"
    ENABLE_API_SCHEDULED_JOB_LIST = "enable_api_scheduled_job_list"
    STRICT_ENV_VAR_MODE = "strict_env_var_mode"

    def __str__(self):
        """Return feature name.

        Returns:
            str: Feature name.
        """
        return self.value

    @property
    def setting_name(self) -> str:
        """Return the setting name for this feature flag.

        Returns:
            The setting name for this feature flag.
        """
        return f"{FEATURE_FLAG_PREFIX}.{self.value}"


class FeatureNotAllowedException(Exception):
    """Occurs when a disallowed code path is run."""

    def __init__(self, feature):
        """Instantiate the error.

        Args:
            feature: the feature flag to check
        """
        super().__init__(feature)
        self.feature = feature

    def __str__(self) -> str:
        """Represent the error as a string.

        Returns:
            string representation of the error
        """
        return f"{self.feature} not enabled."


class SettingsService(ABC):  # noqa: WPS214
    """Abstract base class for managing settings."""

    LOGGING = False
    supports_environments = True

    def __init__(
        self,
        project: Project,
        show_hidden: bool = True,
        env_override: dict = None,
        config_override: dict = None,
    ):
        """Create a new settings service object.

        Args:
            project: Meltano project object.
            show_hidden: Whether to display secret setting values.
            env_override: Optional override environment values.
            config_override:  Optional override configuration values.
        """
        self.project = project

        self.show_hidden = show_hidden

        self.env_override = env_override or {}

        self.config_override = config_override or {}

        self._setting_defs = None

    @property
    @abstractmethod
    def label(self):
        """Return label.

        Returns:
            Label for the settings service.
        """

    @property
    @abstractmethod
    def docs_url(self):
        """Return docs URL.

        Returns:
            URL for Meltano doc site.
        """

    @property
    def env_prefixes(self) -> list[str]:
        """Return prefixes for setting environment variables.

        Returns:
            prefixes for settings environment variables
        """
        return ["meltano"]

    @property
    @abstractmethod
    def db_namespace(self) -> str:
        """Return namespace for setting value records in system database."""

    @property
    @abstractmethod
    def setting_definitions(self) -> list[SettingDefinition]:
        """Return definitions of supported settings."""

    @property  # noqa: B027
    def inherited_settings_service(self):
        """Return settings service to inherit configuration from."""

    @property
    @abstractmethod
    def meltano_yml_config(self) -> dict:
        """Return current configuration in `meltano.yml`."""

    @abstractmethod
    def update_meltano_yml_config(self, config):
        """Update configuration in `meltano.yml`.

        Args:
            config: updated config
        """

    @abstractmethod
    def process_config(self):
        """Process configuration dictionary to be used downstream."""

    @property
    def flat_meltano_yml_config(self):
        """Flatten meltano config.

        Returns:
            the flattened config

        """
        return flatten(self.meltano_yml_config, "dot")

    @property
    def env(self):
        """Return the environment as a dict.

        Returns:
            the environment as a dict.
        """
        return {**os.environ, **self.env_override}

    @classmethod
    def unredact(cls, values: dict) -> dict:
        """Remove any redacted values in a dictionary.

        Args:
            values: the dictionary to remove redacted values from

        Returns:
            the unredacted dictionary
        """
        return {key: val for key, val in values.items() if val != REDACTED_VALUE}

    def config_with_metadata(
        self,
        prefix=None,
        extras=None,
        source=SettingValueStore.AUTO,
        source_manager=None,
        **kwargs,
    ):
        """Return all config values with associated metadata.

        Args:
            prefix: the prefix for setting names
            extras: extra setting definitions to include
            source: the SettingsStore to use
            source_manager: the SettingsStoreManager to use
            kwargs: additional keyword args to pass during SettingsStoreManager instantiation

        Returns:
            dict of config with metadata
        """
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

            config[setting_def.name[len(prefix) :] if prefix else setting_def.name] = {
                **metadata,
                "value": value,
            }

        return config

    def as_dict(self, *args, process=False, **kwargs) -> dict:
        """Return settings without associated metadata.

        Args:
            *args: args to pass to config_with_metadata
            process: whether or not to process the config
            **kwargs: additional kwargs to pass to config_with_metadata

        Returns:
            dict of namew-value settings pairs
        """
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

    def as_env(self, *args, **kwargs) -> dict[str, str]:
        """Return settings as an dictionary of environment variables.

        Args:
            *args: args to pass to config_with_metadata
            **kwargs: additional kwargs to pass to config_with_metadata

        Returns:
            settings as environment variables
        """
        env = {}
        for _, config in self.config_with_metadata(*args, **kwargs).items():
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

    def get_with_metadata(  # noqa: WPS210, WPS615
        self,
        name: str,
        redacted=False,
        source=SettingValueStore.AUTO,
        source_manager=None,
        setting_def=None,
        expand_env_vars=True,
        **kwargs,
    ):
        """Get a setting with associated metadata.

        Args:
            name: the name of the setting to get
            redacted: whether or not the setting is redacted
            source: the SettingsStore to use
            source_manager: the SettingsStoreManager to use
            setting_def: get this SettingDefinition instead of name
            expand_env_vars: whether or not to expand nested environment variables
            **kwargs: additional keyword args to pass during SettingsStoreManager instantiation

        Returns:
            a tuple of the setting value and metadata
        """
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

        # Can't do conventional SettingsService.feature_flag call to check;
        # it would result in circular dependency
        env_var_strict_mode, _ = manager.get(
            f"{FEATURE_FLAG_PREFIX}.{FeatureFlags.STRICT_ENV_VAR_MODE}"
        )
        if expand_env_vars and metadata.get("expandable", False):
            metadata["expandable"] = False
            expanded_value = do_expand_env_vars(
                value, env=expandable_env, raise_if_missing=env_var_strict_mode
            )

            if expanded_value != value:
                metadata["expanded"] = True
                metadata["unexpanded_value"] = value
                value = expanded_value

        if setting_def:
            # Expand flattened config values if the root value is the default
            # or inherited empty object.
            if setting_def.kind == SettingKind.OBJECT and (
                metadata["source"]
                in {SettingValueStore.DEFAULT, SettingValueStore.INHERITED}
            ):
                object_value = {}
                object_source = metadata["source"]
                for setting_key in [  # noqa: WPS335
                    setting_def.name,
                    *setting_def.aliases,
                ]:
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

        self.log(f"Got setting {name!r} with metadata: {metadata}")

        if setting_def is None and metadata["source"] is SettingValueStore.DEFAULT:
            warnings.warn(
                f"Unknown setting {name!r} - the default value `{value!r}` will be used",
                RuntimeWarning,
            )

        return value, metadata

    def get_with_source(self, *args, **kwargs):
        """Get a setting value along with its source.

        Args:
            *args: args to pass to get_with_metadata
            **kwargs: kwargs to pass to get_with_metadata

        Returns:
            tuple of setting value and its source
        """
        value, metadata = self.get_with_metadata(*args, **kwargs)
        return value, metadata["source"]

    def get(self, *args, **kwargs):
        """Get a setting value.

        Args:
            *args: args to pass to get_with_metadata
            **kwargs: kwargs to pass to get_with_metadata

        Returns:
            the setting value
        """
        value, _ = self.get_with_source(*args, **kwargs)
        return value

    def set_with_metadata(  # noqa: WPS615, WPS210
        self, path: str | list[str], value, store=SettingValueStore.AUTO, **kwargs
    ):
        """Set the value and metadata for a setting.

        Args:
            path: the key for the setting
            value: the value to set the setting to
            store: the store to set the value in
            **kwargs: additional keyword args to pass during SettingsStoreManager instantiation

        Returns:
            the new value and metadata for the setting
        """
        self.log(f"Setting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            warnings.warn(f"Unknown setting {name!r}", RuntimeWarning)
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

        metadata.update(
            store.manager(self, **kwargs).set(
                name, path, value, setting_def=setting_def
            )
        )

        self.log(f"Set setting {name!r} with metadata: {metadata}")
        return value, metadata

    def set(self, *args, **kwargs):
        """Set the value for a setting.

        Args:
            *args: args to pass to set_with_metadata
            **kwargs: kwargs to pass to set_with_metadata

        Returns:
            the new value for the setting
        """
        value, _ = self.set_with_metadata(*args, **kwargs)
        return value

    def unset(self, path: list[str], store=SettingValueStore.AUTO, **kwargs):
        """Unset a setting.

        Args:
            path: the key for the setting
            store: the store to set the value in
            **kwargs: additional keyword args to pass during SettingsStoreManager instantiation

        Returns:
            the metadata for the setting
        """
        self.log(f"Unsetting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        try:
            setting_def = self.find_setting(name)
        except SettingMissingError:
            setting_def = None

        metadata = {
            "name": name,
            "path": path,
            "store": store,
            "setting": setting_def,
            **store.manager(self, **kwargs).unset(name, path, setting_def=setting_def),
        }

        self.log(f"Unset setting {name!r} with metadata: {metadata}")
        return metadata

    def reset(self, store=SettingValueStore.AUTO, **kwargs):
        """Reset a setting.

        Args:
            store: the store to set the value in
            **kwargs: additional keyword args to pass during SettingsStoreManager instantiation

        Returns:
            the metadata for the setting
        """
        metadata = {"store": store}

        manager = store.manager(self, **kwargs)
        reset_metadata = manager.reset()
        metadata.update(reset_metadata)

        self.log(f"Reset settings with metadata: {metadata}")
        return metadata

    def definitions(self, extras=None) -> Iterable[dict]:
        """Return setting definitions along with extras.

        Args:
            extras: additional settings to return

        Returns:
            list of setting definitions
        """
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
        """Find a setting by name.

        Args:
            name:the name or alias of the setting to return

        Returns:
            the setting definition matching the given name

        Raises:
            SettingMissingError: if the setting is not found

        """
        try:
            return next(
                setting
                for setting in self.definitions()
                if setting.name == name or name in setting.aliases
            )
        except StopIteration as err:
            raise SettingMissingError(name) from err

    def setting_env_vars(self, setting_def, for_writing=False):
        """Get environment variables for the given setting definition.

        Args:
            setting_def: the setting definition to get env vars for
            for_writing: unused but referenced elsewhere # TODO: clean up refs at some point

        Returns:
            environment variables for given setting
        """
        return setting_def.env_vars(self.env_prefixes)

    def setting_env(self, setting_def):
        """Get a single environment variable for the given setting definition.

        Args:
            setting_def: the setting definition to get env vars for

        Returns:
            environment variable for given setting
        """
        return self.setting_env_vars(setting_def)[0].key

    def log(self, message):
        """Log the given message.

        Args:
            message: the message to log
        """
        if self.LOGGING:
            logger.debug(message)

    @contextmanager
    def feature_flag(
        self, feature: str, raise_error: bool = True
    ) -> Generator[bool, None, None]:
        """Gate code paths based on feature flags.

        Args:
            feature: the feature flag to check
            raise_error: indicates whether error should be raised

        Yields:
            true if the feature flag is enabled, else false

        Raises:
            FeatureNotAllowedException: if raise_error is True and feature flag is disallowed
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Unknown setting", RuntimeWarning)

            # experimental is a top-level setting
            if feature == EXPERIMENTAL:
                allowed = self.get(EXPERIMENTAL) or False
            # other feature flags are nested under feature flag
            else:
                allowed = self.get(f"{FEATURE_FLAG_PREFIX}.{feature}") or False

        try:
            yield allowed
        finally:
            if raise_error and not allowed:
                raise FeatureNotAllowedException(feature)
