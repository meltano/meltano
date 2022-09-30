"""Base class for all Meltano plugins."""

from __future__ import annotations

import logging
import re

import yaml

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior.hookable import HookObject
from meltano.core.setting_definition import SettingDefinition, YAMLEnum
from meltano.core.state_service import STATE_ID_COMPONENT_DELIMITER
from meltano.core.utils import NotFound, find_named

from .command import Command
from .requirements import PluginRequirement

logger = logging.getLogger(__name__)


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
        return "{type} '{name}' variant '{variant}' is not known to Meltano. Variants: {variant_labels}".format(
            type=self.plugin.type.descriptor.capitalize(),
            name=self.plugin.name,
            variant=self.variant_name,
            variant_labels=self.plugin.variant_labels,
        )


class PluginRefNameContainsStateIdDelimiterError(Exception):
    """Occurs when a name in reference to a plugin contains the state ID component delimiter string."""

    def __init__(self, name: str):
        """Create a new exception.

        Args:
            name: The name of the plugin.
        """
        super().__init__(
            f"The plugin name '{name}' cannot contain the state ID component delimiter string '{STATE_ID_COMPONENT_DELIMITER}'"
        )


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class PluginType(YAMLEnum):
    """The type of a plugin."""

    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    TRANSFORMS = "transforms"
    ORCHESTRATORS = "orchestrators"
    TRANSFORMERS = "transformers"
    FILES = "files"
    UTILITIES = "utilities"
    MAPPERS = "mappers"
    MAPPINGS = "mappings"

    def __str__(self) -> str:
        """Return a string representation of the plugin type.

        Returns:
            The string representation of the plugin type.
        """
        return self.value

    @property
    def descriptor(self) -> str:
        """Return the descriptor of the plugin type.

        Returns:
            The descriptor of the plugin type.
        """
        if self is self.__class__.FILES:
            return "file bundle"

        return self.singular

    @property
    def singular(self) -> str:
        """Make singular form for `meltano add PLUGIN_TYPE`.

        Returns:
            The singular form of the plugin type.
        """
        if self is self.__class__.UTILITIES:
            return "utility"

        return self.value[:-1]

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
        if self is self.__class__.MAPPERS:
            return "map"

        return self.value[:-3]

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
        args = [plugin_type.singular for plugin_type in cls]
        args.extend(list(cls))
        return args

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

        raise ValueError(f"{value} is not a valid {cls.__name__}")


class PluginRef(Canonical):
    """A reference to a plugin."""

    def __init__(self, plugin_type: str | PluginType, name: str, **kwargs):
        """Create a new PluginRef.

        Args:
            plugin_type: The type of the plugin.
            name: The name of the plugin.
            kwargs: Additional keyword arguments.

        Raises:
            PluginRefNameContainsStateIdDelimiterError: If the name contains the state ID component delimiter string.
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

    def set_presentation_attrs(self, extras):
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
        name: str = None,
        original: bool | None = None,
        deprecated: bool | None = None,
        docs: str | None = None,
        repo: str | None = None,
        pip_url: str | None = None,
        executable: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        requires: dict[PluginType, list] | None = None,
        env: dict[str, str] | None = None,
        **extras,
    ):
        """Create a new Variant.

        Args:
            name: The name of the variant.
            original: Whether the variant is the original one.
            deprecated: Whether the variant is deprecated.
            docs: The documentation URL.
            repo: The repository URL.
            pip_url: The pip URL.
            executable: The executable name.
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
            executable=executable,
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
        variant: str | None = None,
        variants: list | None = None,
        **extras,
    ):
        """Create a new PluginDefinition.

        Args:
            plugin_type: The type of the plugin.
            name: The name of the plugin.
            namespace: The namespace of the plugin.
            variant: The variant of the plugin.
            variants: The variants of the plugin.
            extras: Additional keyword arguments.
        """
        super().__init__(plugin_type, name)

        self._defaults["label"] = lambda plugin: plugin.name

        def default_logo_url(plugin_def):
            short_name = re.sub(
                r"^(tap|target)-",  # noqa: WPS360
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
        self.set_presentation_attrs(extras)
        self.extras = extras
        self.variants = list(map(Variant.parse, variants))

    def __iter__(self):
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

    def find_variant(self, variant_or_name: str | Variant = None):
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

    def variant_label(self, variant):
        """Return label for specified variant.

        Args:
            variant: The variant.

        Returns:
            The label for the variant.
        """
        variant = self.find_variant(variant)

        label = variant.name or Variant.ORIGINAL_NAME
        if variant == self.variants[0]:
            label = f"{label} (default)"
        elif variant.deprecated:
            label = f"{label} (deprecated)"

        return label

    @property
    def variant_labels(self):
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
            executable=plugin.executable,
            capabilities=plugin.capabilities,
            settings_group_validation=plugin.settings_group_validation,
            settings=plugin.settings,
            commands=plugin.commands,
            requires=plugin.requires,
            env=plugin.env,
            **plugin.extras,
        )


class BasePlugin(HookObject):  # noqa: WPS214
    """A base plugin."""

    EXTRA_SETTINGS = []

    def __init__(self, plugin_def: PluginDefinition, variant: Variant):
        """Create a new BasePlugin.

        Args:
            plugin_def: The plugin definition.
            variant: The variant.
        """
        super().__init__()

        self._plugin_def = plugin_def
        self._variant = variant

    def __eq__(self, other: BasePlugin):
        """Compare two plugins.

        Args:
            other: The other plugin.

        Returns:
            True if the plugins are equal, False otherwise.
        """
        return (
            self._plugin_def == other._plugin_def  # noqa: WPS437
            and self._variant == other._variant  # noqa: WPS437
        )

    def __hash__(self) -> int:
        """Return the hash of the plugin.

        Returns:
            The hash of the plugin.
        """
        return hash((self._plugin_def, self._variant))

    def __iter__(self):
        """Iterate over the settings of the plugin.

        Yields:
            The settings of the plugin.
        """
        yield from self._plugin_def

    def __getattr__(self, attr: str):
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
    def extras(self):
        """Return the plugin extras.

        Returns:
            The extras.
        """
        return {**self._plugin_def.extras, **self._variant.extras}

    @property
    def all_commands(self):
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
    def all_settings(self):
        """Return a list of settings.

        Returns:
            A list of settings.
        """
        return self._variant.settings

    @property
    def extra_settings(self):
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
                existing_settings, defaults, custom=False, default=True
            )
        )

        return existing_settings

    @property
    def all_requires(self):
        """Return a list of requires.

        Returns:
            A list of requires.
        """
        return self._variant.requires

    def env_prefixes(self, for_writing=False) -> list[str]:
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
            True if the plugin is invokable, False otherwise.
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

    def exec_args(self, files: dict):
        """Return the arguments to pass to the plugin runner.

        Args:
            files: The files to pass to the plugin runner.

        Returns:
            The arguments to pass to the plugin runner.
        """
        return []

    @property
    def config_files(self):
        """Return a list of stubbed files created for this plugin.

        Returns:
            A list of stubbed files created for this plugin.
        """
        return {}

    @property
    def output_files(self):
        """Return a list of stubbed files created for this plugin.

        Returns:
            A list of stubbed files created for this plugin.
        """
        return {}

    def process_config(self, config):
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
        plugin_type: PluginType,
        name: str,
        namespace: str,
        variant: str = None,
        label: str = None,
        docs: str | None = None,
        repo: str | None = None,
        pip_url: str | None = None,
        executable: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        requires: dict[PluginType, list] | None = None,
        env: dict[str, str] | None = None,
        **extras,
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
            executable: The executable of the plugin.
            capabilities: The capabilities of the plugin.
            settings_group_validation: The settings group validation of the plugin.
            settings: The settings of the plugin.
            commands: The commands of the plugin.
            requires: Other plugins this plugin depends on.
            env: Environment variables to inject into plugins runtime context.
            extras: Additional attributes to set on the plugin.
        """
        super().__init__(
            plugin_type=plugin_type,
            name=name,
            namespace=namespace,
            variant=variant,
            label=label,
            docs=docs,
            repo=repo,
            pip_url=pip_url,
            executable=executable,
            capabilities=capabilities or [],
            settings_group_validation=settings_group_validation or [],
            settings=list(map(SettingDefinition.parse, settings or [])),
            commands=Command.parse_all(commands),
            requires=PluginRequirement.parse_all(requires),
            env=env or {},
            extras=extras,
        )

    @classmethod
    def from_variant(
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
            executable=variant.executable,
            capabilities=variant.capabilities,
            settings_group_validation=variant.settings_group_validation,
            settings=variant.settings,
            commands=variant.commands,
            requires=variant.requires,
            env=variant.env,
            **{**plugin_def.extras, **variant.extras},
        )
