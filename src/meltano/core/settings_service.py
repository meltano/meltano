"""Module for managing settings."""

from __future__ import annotations

import enum
import os
import sys
import typing as t
import warnings
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

import structlog

from meltano.core.setting_definition import SettingKind
from meltano.core.settings_store import SettingValueStore
from meltano.core.utils import EnvVarMissingBehavior, flatten
from meltano.core.utils import expand_env_vars as do_expand_env_vars

if sys.version_info >= (3, 11):
    from enum import StrEnum
    from typing import Self  # noqa: ICN003
else:
    from backports.strenum import StrEnum
    from typing_extensions import Self

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from meltano.core.project import Project
    from meltano.core.setting_definition import EnvVar, SettingDefinition
    from meltano.core.settings_store import SettingsStoreManager

logger = structlog.stdlib.get_logger(__name__)


# sentinel value to use to prevent leaking sensitive data
REDACTED_VALUE = "(redacted)"

# magic string used as feature flag setting for experimental features
EXPERIMENTAL = "experimental"
FEATURE_FLAG_PREFIX = "ff"


class FeatureFlags(StrEnum):
    """Available Meltano Feature Flags."""

    STRICT_ENV_VAR_MODE = enum.auto()
    PLUGIN_LOCKS_REQUIRED = enum.auto()

    @property
    def setting_name(self) -> str:
        """Return the setting name for this feature flag.

        Returns:
            The setting name for this feature flag.
        """
        return f"{FEATURE_FLAG_PREFIX}.{self.value}"


class FeatureNotAllowedException(Exception):
    """A disallowed code path is run."""

    def __init__(self, feature: str) -> None:
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


class SettingsService(metaclass=ABCMeta):
    """Abstract base class for managing settings."""

    LOGGING = False
    supports_environments = True

    def __init__(
        self,
        project: Project,
        *,
        show_hidden: bool = True,
        env_override: dict[str, t.Any] | None = None,
        config_override: dict | None = None,
    ):
        """Create a new settings service instance.

        Args:
            project: Meltano project instance.
            show_hidden: Whether to display secret setting values.
            env_override: Optional override environment values.
            config_override:  Optional override configuration values.
        """
        self.project = project
        self.show_hidden = show_hidden
        self.env_override: dict[str, t.Any] = env_override or {}
        self.config_override = config_override or {}
        self._setting_defs: list[SettingDefinition] | None = None

    @property
    @abstractmethod
    def label(self) -> str:
        """Return label.

        Returns:
            Label for the settings service.
        """

    @property
    @abstractmethod
    def docs_url(self) -> str:
        """Return docs URL.

        Returns:
            URL for Meltano doc site.
        """

    @property
    @abstractmethod
    def project_settings_service(self) -> SettingsService:
        """Get a project settings service.

        Returns:
            A ProjectSettingsService
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

    @property
    def inherited_settings_service(self) -> Self | None:
        """Return settings service to inherit configuration from."""
        return None

    @property
    @abstractmethod
    def meltano_yml_config(self) -> dict:
        """Return current configuration in `meltano.yml`."""

    @abstractmethod
    def update_meltano_yml_config(self, config: dict) -> None:
        """Update configuration in `meltano.yml`.

        Args:
            config: updated config
        """

    @abstractmethod
    def process_config(self, config: dict) -> dict:
        """Process configuration dictionary to be used downstream.

        Args:
            config: configuration dictionary to process
        """

    @property
    def flat_meltano_yml_config(self) -> dict:
        """Flatten meltano config.

        Returns:
            the flattened config

        """
        return flatten(self.meltano_yml_config, "dot")

    @property
    def env(self) -> dict[str, t.Any]:
        """Return the environment as a dict.

        Returns:
            the environment as a dict.
        """
        return {**os.environ, **self.env_override}

    def config_with_metadata(
        self,
        *,
        prefix: str | None = None,
        extras: bool | None = None,
        source: SettingValueStore = SettingValueStore.AUTO,
        source_manager: SettingsStoreManager | None = None,
        **kwargs: t.Any,
    ) -> dict[str, t.Any]:
        """Return all config values with associated metadata.

        Args:
            prefix: the prefix for setting names
            extras: extra setting definitions to include
            source: the SettingsStore to use
            source_manager: the SettingsStoreManager to use
            kwargs: additional keyword args to pass during SettingsStoreManager
                instantiation

        Returns:
            dict of config with metadata
        """
        if source_manager:
            # TODO: Ensure only a bulk-enabled manager can be used here
            source_manager.bulk = True  # type: ignore[attr-defined]
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

    def as_dict(
        self,
        *args: t.Any,
        process: bool = False,
        **kwargs: t.Any,
    ) -> dict[str, t.Any]:
        """Return settings without associated metadata.

        Args:
            *args: args to pass to config_with_metadata
            process: Whether to process the config
            **kwargs: additional kwargs to pass to config_with_metadata

        Returns:
            dict of name-value settings pairs
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

    def as_env(self, *args: t.Any, **kwargs: t.Any) -> dict[str, str]:
        """Return settings as an dictionary of environment variables.

        Args:
            *args: args to pass to config_with_metadata
            **kwargs: additional kwargs to pass to config_with_metadata

        Returns:
            settings as environment variables
        """
        env = {}
        for config in self.config_with_metadata(*args, **kwargs).values():
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
        *,
        redacted: bool = False,
        source: SettingValueStore = SettingValueStore.AUTO,
        source_manager: SettingsStoreManager | None = None,
        setting_def: SettingDefinition | None = None,
        expand_env_vars: bool = True,
        redacted_value: str = REDACTED_VALUE,
        **kwargs: t.Any,
    ) -> tuple[t.Any, dict[str, t.Any]]:
        """Get a setting with associated metadata.

        Args:
            name: the name of the setting to get
            redacted: Whether the setting is redacted
            source: the `SettingsStore` to use
            source_manager: the `SettingsStoreManager` to use
            setting_def: get this `SettingDefinition` instead of name
            expand_env_vars: Whether to expand nested environment variables
            redacted_value: the value to use when redacting the setting
            **kwargs: additional keyword args to pass during
                `SettingsStoreManager` instantiation

        Returns:
            a tuple of the setting value and metadata
        """
        setting_def = setting_def or self.find_setting(name)
        if setting_def:
            name = setting_def.name

        self.log(f"Getting setting '{name}'")

        metadata: dict[str, t.Any] = {
            "name": name,
            "source": source,
            "setting": setting_def,
        }

        expandable_env = {**self.project.dotenv_env, **self.env}
        if setting_def and setting_def.is_extra:
            expandable_env.update(
                self.as_env(
                    extras=False,
                    redacted=redacted,
                    source=source,
                    source_manager=source_manager,
                ),
            )

        manager = source_manager or source.manager(self, **kwargs)
        value, get_metadata = manager.get(name, setting_def=setting_def)
        metadata.update(get_metadata)

        # Can't do conventional SettingsService.feature_flag call to check;
        # it would result in circular dependency
        strict_env_var_mode, _ = source.manager(self.project_settings_service).get(
            f"{FEATURE_FLAG_PREFIX}.{FeatureFlags.STRICT_ENV_VAR_MODE}",
            cast_value=True,
        )
        if expand_env_vars and metadata.get("expandable", False):
            metadata["expandable"] = False
            expanded_value = do_expand_env_vars(  # type: ignore[type-var]
                value,
                env=expandable_env,
                if_missing=EnvVarMissingBehavior(int(strict_env_var_mode)),  # type: ignore[arg-type]
            )
            # https://github.com/meltano/meltano/issues/7189#issuecomment-1396112167
            if value and not expanded_value:  # The whole string was missing env vars
                expanded_value = None

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
                for setting_key in (setting_def.name, *setting_def.aliases):
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
                    value = object_value  # type: ignore[assignment]
                    metadata["source"] = object_source

            # Only cast if the setting is not expandable,
            # since we can't cast e.g. $PORT to an integer
            if not metadata.get("expandable", False):
                cast_value = setting_def.cast_value(value)
                if cast_value != value:
                    metadata["uncast_value"] = value
                    value = cast_value

            # we don't want to leak secure informations
            # so we redact all `passwords`
            if redacted and value and setting_def.is_redacted:
                metadata["redacted"] = True
                value = redacted_value

        self.log(f"Got setting {name!r} with metadata: {metadata}")

        if setting_def is None and metadata["source"] is SettingValueStore.DEFAULT:
            warnings.warn(
                (
                    f"Unknown setting {name!r} - the default value "
                    f"`{value!r}` will be used"
                ),
                RuntimeWarning,
                stacklevel=2,
            )

        return value, metadata

    def get_with_source(self, *args: t.Any, **kwargs: t.Any) -> tuple[t.Any, t.Any]:
        """Get a setting value along with its source.

        Args:
            *args: args to pass to get_with_metadata
            **kwargs: kwargs to pass to get_with_metadata

        Returns:
            tuple of setting value and its source
        """
        value, metadata = self.get_with_metadata(*args, **kwargs)
        return value, metadata["source"]

    def get(self, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
        """Get a setting value.

        Args:
            *args: args to pass to get_with_metadata
            **kwargs: kwargs to pass to get_with_metadata

        Returns:
            the setting value
        """
        value, _ = self.get_with_source(*args, **kwargs)
        return value

    def set_with_metadata(
        self,
        path: str | list[str],
        value: t.Any,  # noqa: ANN401
        store: SettingValueStore = SettingValueStore.AUTO,
        *,
        redacted_value: str = REDACTED_VALUE,
        cast_value: bool = True,
        **kwargs: t.Any,
    ) -> tuple[t.Any, dict[str, t.Any]]:
        """Set the value and metadata for a setting.

        Args:
            path: the key for the setting
            value: the value to set the setting to
            store: the store to set the value in
            redacted_value: the value to use when redacting the setting
            cast_value: Whether to cast the setting value to its expected type
            **kwargs: additional keyword args to pass during
                `SettingsStoreManager` instantiation

        Returns:
            the new value and metadata for the setting
        """
        self.log(f"Setting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)

        setting_def = self.find_setting(name)
        if setting_def is None:
            warnings.warn(f"Unknown setting {name!r}", RuntimeWarning, stacklevel=2)

        metadata: dict[str, t.Any] = {
            "name": name,
            "path": path,
            "store": store,
            "setting": setting_def,
        }

        if value == redacted_value:
            metadata["redacted"] = True
            return None, metadata

        if setting_def and cast_value:
            new_value = setting_def.cast_value(value)
            if new_value != value:
                metadata["uncast_value"] = value
                value = new_value

        metadata.update(
            store.manager(self, **kwargs).set(
                name,
                path,
                value,
                setting_def=setting_def,
            ),
        )

        self.log(f"Set setting {name!r} with metadata: {metadata}")
        return value, metadata

    def set(self, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
        """Set the value for a setting.

        Args:
            *args: args to pass to set_with_metadata
            **kwargs: kwargs to pass to set_with_metadata

        Returns:
            the new value for the setting
        """
        value, _ = self.set_with_metadata(*args, **kwargs)
        return value

    def unset(
        self,
        path: list[str] | str,
        store: SettingValueStore = SettingValueStore.AUTO,
        **kwargs: t.Any,
    ) -> dict:
        """Unset a setting.

        Args:
            path: the key for the setting
            store: the store to set the value in
            **kwargs: additional keyword args to pass during
                SettingsStoreManager instantiation

        Returns:
            the metadata for the setting
        """
        self.log(f"Unsetting setting '{path}'")

        if isinstance(path, str):
            path = [path]

        name = ".".join(path)
        setting_def = self.find_setting(name)

        metadata = {
            "name": name,
            "path": path,
            "store": store,
            "setting": setting_def,
            **store.manager(self, **kwargs).unset(name, path, setting_def=setting_def),
        }

        self.log(f"Unset setting {name!r} with metadata: {metadata}")
        return metadata

    def reset(
        self,
        store: SettingValueStore = SettingValueStore.AUTO,
        **kwargs: t.Any,
    ) -> dict:
        """Reset a setting.

        Args:
            store: the store to set the value in
            **kwargs: additional keyword args to pass during
                `SettingsStoreManager` instantiation

        Returns:
            the metadata for the setting
        """
        metadata = {"store": store, **store.manager(self, **kwargs).reset()}
        self.log(f"Reset settings with metadata: {metadata}")
        return metadata

    def definitions(self, *, extras: bool | None = None) -> Iterable[SettingDefinition]:
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
                if not setting.hidden or self.show_hidden
            ]

        if extras is not None:
            return [
                setting
                for setting in self._setting_defs
                if (extras is True and setting.is_extra)
                or (extras is False and not setting.is_extra)
            ]

        return self._setting_defs

    def find_setting(self, name: str) -> SettingDefinition | None:
        """Find a setting by name.

        Args:
            name:the name or alias of the setting to return

        Returns:
            the setting definition matching the given name or None if not found

        Raises:
            SettingMissingError: if the setting is not found

        """
        return next(
            (
                setting
                for setting in self.definitions()
                if setting.name == name or name in setting.aliases
            ),
            None,
        )

    # TODO: The `for_writing` parameter is unused, but referenced elsewhere.
    # Callers should be updated to not use it, and then it should be removed.
    def setting_env_vars(
        self,
        setting_def: SettingDefinition,
        *,
        for_writing: bool = False,  # noqa: ARG002
    ) -> list[EnvVar]:
        """Get environment variables for the given setting definition.

        Args:
            setting_def: The setting definition to get env vars for.
            for_writing: Unused parameter.

        Returns:
            Environment variables for given setting
        """
        return setting_def.env_vars(self.env_prefixes)

    def setting_env(self, setting_def: SettingDefinition) -> str:
        """Get a single environment variable for the given setting definition.

        Args:
            setting_def: the setting definition to get env vars for

        Returns:
            environment variable for given setting
        """
        return self.setting_env_vars(setting_def)[0].key

    def log(self, message: str) -> None:
        """Log the given message.

        Args:
            message: the message to log
        """
        if self.LOGGING:
            logger.debug(message)

    @contextmanager
    def feature_flag(
        self,
        feature: str,
        *,
        raise_error: bool = True,
    ) -> Generator[bool, None, None]:
        """Gate code paths based on feature flags.

        Args:
            feature: the feature flag to check
            raise_error: indicates whether error should be raised

        Yields:
            true if the feature flag is enabled, else false

        Raises:
            FeatureNotAllowedException: if `raise_error` is `True` and feature
                flag is disallowed
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
            yield t.cast("bool", allowed)
        finally:
            if raise_error and not allowed:
                raise FeatureNotAllowedException(feature)
