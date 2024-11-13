"""Base class for all Meltano plugins."""

from __future__ import annotations

import enum
import re
import typing as t
from collections import defaultdict

import yaml
from structlog.stdlib import get_logger

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior.hookable import HookObject
from meltano.core.job_state import STATE_ID_COMPONENT_DELIMITER
from meltano.core.plugin.command import Command
from meltano.core.plugin.requirements import PluginRequirement
from meltano.core.setting_definition import SettingDefinition, SettingKind, YAMLEnum
from meltano.core.utils import NotFound, find_named

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.plugin_invoker import PluginInvoker

logger = get_logger(__name__)


class VariantNotFoundError(Exception):
    """Raised when a variant is not found."""

    def __init__(self, plugin: PluginDefinition, variant_name: str):
        """Create a new VariantNotFoundError.

        Args:
            plugin: The plugin definition.
            variant_name: The name of the variant that was not found.
        """
        self.plugin = plugin
        self.variant_name = variant_name

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            The string representation of the error.
        """
        return (
            f"{self.plugin.type.descriptor.capitalize()} '{self.plugin.name}' "
            f"variant '{self.variant_name}' is not known to Meltano. "
            f"Variants: {self.plugin.variant_labels}"
        )


class PluginRefNameContainsStateIdDelimiterError(Exception):
    """A name in reference to a plugin contains the state ID component delimiter."""

    def __init__(self, name: str):
        """Create a new exception.

        Args:
            name: The name of the plugin.
        """
        super().__init__(
            f"The plugin name '{name}' cannot contain the state ID component "
            f"delimiter string '{STATE_ID_COMPONENT_DELIMITER}'",
        )


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class PluginType(YAMLEnum):
    """The type of a plugin."""

    EXTRACTORS = enum.auto()
    LOADERS = enum.auto()
    TRANSFORMS = enum.auto()
    ORCHESTRATORS = enum.auto()
    TRANSFORMERS = enum.auto()
    FILES = enum.auto()
    UTILITIES = enum.auto()
    MAPPERS = enum.auto()
    MAPPINGS = enum.auto()

    @property
    def descriptor(self) -> str:
        """Return the descriptor of the plugin type.

        Returns:
            The descriptor of the plugin type.
        """
        return "file bundle" if self is self.__class__.FILES else self.singular

    @property
    def singular(self) -> str:
        """Make singular form for `meltano add PLUGIN_TYPE`.

        Returns:
            The singular form of the plugin type.
        """
        return "utility" if self is self.__class__.UTILITIES else self.value[:-1]

    @property
    def verb(self) -> str:
        """Make verb form.

        Returns:
            The verb form of the plugin type.
        """
        if self is self.__class__.TRANSFORMS:
            return self.singular
        if self is self.__class__.UTILITIES:
            return "utilize"
        return "map" if self is self.__class__.MAPPERS else self.value[:-3]

    @property
    def discoverable(self) -> bool:
        """Whether this plugin type is discoverable on the Hub.

        Returns:
            Whether this plugin type is discoverable on the Hub.
        """
        return self is not self.__class__.MAPPINGS

    @classmethod
    def value_exists(cls, value: str) -> bool:
        """Check if a plugin type exists.

        Args:
            value: The plugin type to check.

        Returns:
            True if the plugin type exists, False otherwise.
        """
        return value in cls._value2member_map_

    @classmethod
    def cli_arguments(cls) -> list:
        """Return the list of plugin types that can be used as CLI arguments.

        Returns:
            The list of plugin types that can be used as CLI arguments.
        """
        return [
            getattr(plugin_type, plugin_type_name)
            for plugin_type in cls
            for plugin_type_name in ("singular", "value")
        ]

    @classmethod
    def from_cli_argument(cls, value: str) -> PluginType:
        """Get the plugin type from a CLI argument.

        Args:
            value: The CLI argument.

        Returns:
            The plugin type.

        Raises:
            ValueError: If the plugin type does not exist.
        """
        for plugin_type in cls:
            if value in {plugin_type.value, plugin_type.singular}:
                return plugin_type

        raise ValueError(f"{value!r} is not a valid {cls.__name__}")  # noqa: EM102

    @classmethod
    def plurals(cls) -> list[str]:
        """Return the list of plugin plural names.

        Returns:
            The list of plugin plurals.
        """
        return [plugin_type.value for plugin_type in cls]


class PluginRef(Canonical):
    """A reference to a plugin."""

    name: str

    def __init__(self, plugin_type: str | PluginType, name: str, **kwargs):  # noqa: ANN003
        """Create a new PluginRef.

        Args:
            plugin_type: The type of the plugin.
            name: The name of the plugin.
            kwargs: Additional keyword arguments.

        Raises:
            PluginRefNameContainsStateIdDelimiterError: If the name contains
                the state ID component delimiter string.
        """
        if STATE_ID_COMPONENT_DELIMITER in name:
            raise PluginRefNameContainsStateIdDelimiterError(name)

        self._type = (
            plugin_type
            if isinstance(plugin_type, PluginType)
            else PluginType(plugin_type)
        )

        super().__init__(name=name, **kwargs)

    @property
    def type(self) -> PluginType:
        """Return the type of the plugin.

        Returns:
            The type of the plugin.
        """
        return self._type

    @property
    def plugin_dir_name(self) -> str:
        """Return the plugin directory name.

        Returns:
            The plugin directory name.
        """
        return self.name

    def __eq__(self, other: PluginRef) -> bool:
        """Compare two plugin references.

        Args:
            other: The other plugin reference.

        Returns:
            True if the plugin references are equal, False otherwise.
        """
        return self.name == other.name and self.type == other.type

    def __hash__(self) -> int:
        """Return the hash of the plugin reference.

        Returns:
            The hash of the plugin reference.
        """
        return hash((self.type, self.name))

    def set_presentation_attrs(self, extras) -> None:  # noqa: ANN001
        """Set the presentation attributes of the plugin reference.

        Args:
            extras: The presentation attributes.
        """
        self.update(
            hidden=extras.pop("hidden", None),
            label=extras.pop("label", None),
            logo_url=extras.pop("logo_url", None),
            description=extras.pop("description", None),
        )


class Variant(NameEq, Canonical):
    """A variant of a plugin."""

    ORIGINAL_NAME = "original"
    DEFAULT_NAME = "default"

    def __init__(
        self,
        name: str | None = None,
        original: bool | None = None,
        deprecated: bool | None = None,
        docs: str | None = None,
        repo: str | None = None,
        pip_url: str | None = None,
        python: str | None = None,
        executable: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        requires: dict[PluginType, list] | None = None,
        env: dict[str, str] | None = None,
        **extras,  # noqa: ANN003
    ):
        """Create a new Variant.

        Args:
            name: The name of the variant.
            original: Whether the variant is the original one.
            deprecated: Whether the variant is deprecated.
            docs: The documentation URL.
            repo: The repository URL.
            pip_url: The pip URL.
            python: The path to the Python executable to use, or name to find on the
                $PATH. Defaults to the Python executable running Meltano.
            executable: The executable name.
            description: The description of the plugin.
            logo_url: The logo URL of the plugin.
            capabilities: The capabilities of the variant.
            settings_group_validation: The settings group validation.
            settings: The settings of the variant.
            commands: The commands of the variant.
            requires: Other plugins this plugin depends on.
            env: Environment variables to inject into plugins runtime context.
            extras: Additional keyword arguments.
        """
        super().__init__(
            name=name,
            original=original,
            deprecated=deprecated,
            docs=docs,
            repo=repo,
            pip_url=pip_url,
            python=python,
            executable=executable,
            description=description,
            logo_url=logo_url,
            capabilities=list(capabilities or []),
            settings_group_validation=list(settings_group_validation or []),
            settings=list(map(SettingDefinition.parse, settings or [])),
            commands=Command.parse_all(commands),
            requires=PluginRequirement.parse_all(requires),
            env=env or {},
            extras=extras,
        )


class PluginDefinition(PluginRef):
    """A plugin definition."""

    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: str,
        *,
        python: str | None = None,
        variant: str | None = None,
        variants: list | None = None,
        is_default_variant: bool | None = None,
        **extras,  # noqa: ANN003
    ):
        """Create a new PluginDefinition.

        Args:
            plugin_type: The type of the plugin.
            name: The name of the plugin.
            namespace: The namespace of the plugin.
            python: The path to the Python executable to use, or name to find on the
                $PATH. Defaults to the Python executable running Meltano.
            variant: The variant of the plugin.
            variants: The variants of the plugin.
            is_default_variant: Whether the variant is the default one.
            extras: Additional keyword arguments.
        """
        super().__init__(plugin_type, name)

        self._defaults["label"] = lambda plugin: plugin.name

        def default_logo_url(plugin_def) -> str:  # noqa: ANN001
            short_name = re.sub(
                r"^(tap|target)-",
                "",
                plugin_def.name,
            )
            return f"/static/logos/{short_name}-logo.png"

        self._defaults["logo_url"] = default_logo_url

        if not variants:
            variant = Variant(variant, **extras)

            # Any properties considered "extra" by the variant should be
            # considered extras of the plugin definition.
            extras = variant.extras
            variant.extras = {}

            variants = [variant]

        # Attributes will be listed in meltano.yml in this order:
        self.namespace = namespace
        self.python = python
        self.set_presentation_attrs(extras)
        self.extras = extras
        self.variants = [Variant.parse(x) for x in variants]
        self.is_default_variant = is_default_variant

    def __iter__(self):  # noqa: ANN204
        """Iterate over the variants of the plugin definition.

        Yields:
            The variants of the plugin definition.
        """
        for attr, value in super().__iter__():
            if attr == "variants" and len(value) == 1:
                # If there is only a single variant, its properties can be
                # nested in the plugin definition
                for variant_k, variant_v in value[0]:
                    if variant_k == "name":
                        variant_k = "variant"

                    yield (variant_k, variant_v)
            else:
                yield (attr, value)

    def get_variant(self, variant_name: str) -> Variant:
        """Get the variant with the given name.

        Args:
            variant_name: The name of the variant.

        Returns:
            The variant with the given name.

        Raises:
            VariantNotFoundError: If the variant is not found.
        """
        try:
            return find_named(self.variants, variant_name)
        except NotFound as err:
            raise VariantNotFoundError(self, variant_name) from err

    def find_variant(self, variant_or_name: str | Variant | None = None):  # noqa: ANN201
        """Find the variant with the given name or variant.

        Args:
            variant_or_name: The variant or name of the variant.

        Returns:
            The variant with the given name or variant.
        """
        if isinstance(variant_or_name, Variant):
            return variant_or_name

        if variant_or_name is None or variant_or_name == Variant.DEFAULT_NAME:
            return self.variants[0]

        if variant_or_name == Variant.ORIGINAL_NAME:
            try:
                return next(variant for variant in self.variants if variant.original)
            except StopIteration:
                return self.variants[0]

        return self.get_variant(variant_or_name)

    def variant_label(self, variant):  # noqa: ANN001, ANN201
        """Return label for specified variant.

        Args:
            variant: The variant.

        Returns:
            The label for the variant.
        """
        variant = self.find_variant(variant)

        label = variant.name or Variant.ORIGINAL_NAME

        if variant == self.variants[0] and self.is_default_variant is not False:
            return f"{label} (default)"

        if variant.deprecated:
            return f"{label} (deprecated)"

        return label

    @property
    def variant_labels(self):  # noqa: ANN201
        """Return labels for supported variants.

        Returns:
            The labels for the supported variants.
        """
        return ", ".join([self.variant_label(variant) for variant in self.variants])

    @classmethod
    def from_standalone(
        cls: type[PluginDefinition],
        plugin: StandalonePlugin,
    ) -> PluginDefinition:
        """Create a new PluginDefinition from a StandalonePlugin.

        Args:
            plugin: The plugin.

        Returns:
            The new PluginDefinition.
        """
        return cls(
            plugin.plugin_type,
            plugin.name,
            plugin.namespace,
            variant=plugin.variant,
            # Extras
            label=plugin.label,
            docs=plugin.docs,
            repo=plugin.repo,
            pip_url=plugin.pip_url,
            python=plugin.python,
            executable=plugin.executable,
            description=plugin.description,
            logo_url=plugin.logo_url,
            capabilities=plugin.capabilities,
            settings_group_validation=plugin.settings_group_validation,
            settings=plugin.settings,
            commands=plugin.commands,
            requires=plugin.requires,
            env=plugin.env,
            **plugin.extras,
        )


class BasePlugin(HookObject):
    """A base plugin."""

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = []

    def __init__(self, plugin_def: PluginDefinition, variant: Variant):
        """Create a new BasePlugin.

        Args:
            plugin_def: The plugin definition.
            variant: The variant.
        """
        super().__init__()

        self._plugin_def = plugin_def
        self._variant = variant

    def __eq__(self, other: BasePlugin) -> bool:
        """Compare two plugins.

        Args:
            other: The other plugin.

        Returns:
            True if the plugins are equal, False otherwise.
        """
        return self._plugin_def == other._plugin_def and self._variant == other._variant

    def __hash__(self) -> int:
        """Return the hash of the plugin.

        Returns:
            The hash of the plugin.
        """
        return hash((self._plugin_def, self._variant))

    def __iter__(self):  # noqa: ANN204
        """Iterate over the settings of the plugin.

        Yields:
            The settings of the plugin.
        """
        yield from self._plugin_def

    def __getattr__(self, attr: str):  # noqa: ANN204
        """Get the value of the setting.

        Args:
            attr: The name of the setting.

        Returns:
            The value of the setting.
        """
        try:
            return getattr(self._plugin_def, attr)
        except AttributeError:
            return getattr(self._variant, attr)

    @property
    def variant(self) -> str:
        """Return the variant name.

        Returns:
            The variant name.
        """
        return self._variant.name

    @property
    def executable(self) -> str:
        """Return the plugin executable.

        Returns:
            The executable name.
        """
        return self._variant.executable or self._plugin_def.name

    @property
    def extras(self):  # noqa: ANN201
        """Return the plugin extras.

        Returns:
            The extras.
        """
        return {**self._plugin_def.extras, **self._variant.extras}

    @property
    def all_commands(self):  # noqa: ANN201
        """Return a dictionary of supported commands.

        Returns:
            A dictionary of supported commands.
        """
        return self._variant.commands

    @property
    def test_commands(self) -> dict[str, Command]:
        """Return a the test command for this plugin.

        Returns:
            The test command for this plugin.
        """
        return {
            name: command
            for name, command in self.all_commands.items()
            if name.startswith("test")
        }

    @property
    def all_settings(self):  # noqa: ANN201
        """Return a list of settings.

        Returns:
            A list of settings.
        """
        return self._variant.settings

    @property
    def extra_settings(self):  # noqa: ANN201
        """Return the extra settings for this plugin.

        Returns:
            The extra settings for this plugin.
        """
        defaults = {f"_{name}": value for name, value in self.extras.items()}

        existing_settings = []
        for setting in self.EXTRA_SETTINGS:
            default_value = defaults.get(setting.name)
            if default_value is not None:
                setting = setting.with_attrs(value=default_value)

            existing_settings.append(setting)

        # Create setting definitions for unknown defaults,
        # including flattened keys of default nested object items
        existing_settings.extend(
            SettingDefinition.from_missing(
                existing_settings,
                defaults,
                custom=False,
                default=True,
            ),
        )

        return existing_settings

    @property
    def all_requires(self):  # noqa: ANN201
        """Return a list of requires.

        Returns:
            A list of requires.
        """
        return self._variant.requires

    def env_prefixes(
        self,
        *,
        for_writing: bool = False,  # noqa: ARG002
    ) -> list[str]:
        """Return environment variable prefixes to use for settings.

        Args:
            for_writing: Whether to return environment variable prefixes for writing.

        Returns:
            The environment variable prefixes.
        """
        return [self.name, self.namespace]

    def is_installable(self) -> bool:
        """Return whether the plugin is installable.

        Returns:
            True if the plugin is installable, False otherwise.
        """
        return self.pip_url is not None

    def is_invokable(self) -> bool:
        """Return whether the plugin is invokable.

        Returns:
            Whether the plugin is invokable.
        """
        return self.is_installable() or self.executable is not None

    def is_configurable(self) -> bool:
        """Return whether the plugin is configurable.

        Returns:
            True if the plugin is configurable, False otherwise.
        """
        return True

    def should_add_to_file(self) -> bool:
        """Return whether the plugin should be added to the config file.

        Returns:
            True if the plugin should be added to the config file, False otherwise.
        """
        return True

    def exec_args(  # noqa: D417
        self,
        plugin_invoker: PluginInvoker,  # noqa: ARG002
    ) -> list[str | Path]:
        """Return the arguments to pass to the plugin runner.

        Args:
            files: The files to pass to the plugin runner.

        Returns:
            The arguments to pass to the plugin runner.
        """
        return []

    @property
    def config_files(self) -> dict[str, str]:
        """Return a list of stubbed files created for this plugin.

        Returns:
            A list of stubbed files created for this plugin.
        """
        return {}

    @property
    def output_files(self) -> dict[str, str]:
        """Return a list of stubbed files created for this plugin.

        Returns:
            A list of stubbed files created for this plugin.
        """
        return {}

    def process_config(self, config: dict) -> dict:
        """Process the config for this plugin.

        Args:
            config: The config to process.

        Returns:
            The processed config.
        """
        return config

    @property
    def definition(self) -> PluginDefinition:
        """Return the plugin definition.

        Returns:
            The plugin definition.
        """
        return self._plugin_def


class StandalonePlugin(Canonical):
    """A standalone plugin definition representing a single variant."""

    def __init__(
        self,
        plugin_type: str,
        name: str,
        namespace: str,
        variant: str | None = None,
        label: str | None = None,
        docs: str | None = None,
        repo: str | None = None,
        pip_url: str | None = None,
        python: str | None = None,
        executable: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        requires: dict[PluginType, list] | None = None,
        env: dict[str, str] | None = None,
        **extras,  # noqa: ANN003
    ):
        """Create a locked plugin.

        Args:
            plugin_type: The plugin type.
            name: The name of the plugin.
            namespace: The namespace of the plugin.
            variant: The variant of the plugin.
            label: The label of the plugin.
            docs: The documentation URL of the plugin.
            repo: The repository URL of the plugin.
            pip_url: The pip URL of the plugin.
            python: The path to the Python executable to use, or name to find on the
                $PATH. Defaults to the Python executable running Meltano.
            executable: The executable of the plugin.
            description: The description of the plugin.
            logo_url: The logo URL of the plugin.
            capabilities: The capabilities of the plugin.
            settings_group_validation: The settings group validation of the plugin.
            settings: The settings of the plugin.
            commands: The commands of the plugin.
            requires: Other plugins this plugin depends on.
            env: Environment variables to inject into plugins runtime context.
            extras: Additional attributes to set on the plugin.
        """
        super().__init__(
            plugin_type=PluginType(plugin_type),
            name=name,
            namespace=namespace,
            variant=variant,
            label=label,
            docs=docs,
            repo=repo,
            pip_url=pip_url,
            python=python,
            executable=executable,
            description=description,
            logo_url=logo_url,
            capabilities=capabilities or [],
            settings_group_validation=settings_group_validation or [],
            settings=list(map(SettingDefinition.parse, settings or [])),
            commands=Command.parse_all(commands),
            requires=PluginRequirement.parse_all(requires),
            env=env or {},
            extras=extras,
        )

        deprecated_kind_replacements = {
            SettingKind.HIDDEN: "hidden: true",
            SettingKind.PASSWORD: "sensitive: true",
        }

        settings_by_deprecated_kind = defaultdict(list)

        for s in self.settings:
            if s.kind in deprecated_kind_replacements:
                settings_by_deprecated_kind[s.kind].append(s)

        if settings_by_deprecated_kind:
            for kind, settings in settings_by_deprecated_kind.items():
                logger.warning(
                    f"`kind: {kind}` is deprecated for setting definitions"  # noqa: G003
                    + (
                        f" in favour of `{deprecated_kind_replacements[kind]}`"
                        if deprecated_kind_replacements[kind]
                        else ""
                    )
                    + ", and is currently in use by the following settings of "
                    + f"{self.plugin_type.singular} '{self.name}': "
                    + ", ".join([f"'{s.name}'" for s in settings])
                    + ". "
                    + "Please open an issue or pull request to update the plugin "
                    + "definition on Meltano Hub at "
                    + f"https://github.com/meltano/hub/blob/main/_data/meltano/{self.plugin_type}/{self.name}/{self.variant}.yml.",
                )

    @classmethod
    def from_variant(  # noqa: ANN206
        cls: type[StandalonePlugin],
        variant: Variant,
        plugin_def: PluginDefinition,
    ):
        """Create a locked plugin from a variant and plugin definition.

        Args:
            variant: The variant to create the plugin from.
            plugin_def: The plugin definition to create the plugin from.

        Returns:
            A locked plugin definition.
        """
        return cls(
            plugin_type=plugin_def.type,
            name=plugin_def.name,
            namespace=plugin_def.namespace,
            variant=variant.name,
            label=plugin_def.label,
            docs=variant.docs,
            repo=variant.repo,
            pip_url=variant.pip_url,
            python=plugin_def.python,
            executable=variant.executable,
            description=variant.description,
            logo_url=variant.logo_url,
            capabilities=variant.capabilities,
            settings_group_validation=variant.settings_group_validation,
            settings=variant.settings,
            commands=variant.commands,
            requires=variant.requires,
            env=variant.env,
            **{**plugin_def.extras, **variant.extras},
        )
