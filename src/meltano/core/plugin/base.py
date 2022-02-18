"""Base class for all Meltano plugins."""

import logging
import re
from typing import Dict, Optional, Union

import yaml

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior.hookable import HookObject
from meltano.core.setting_definition import SettingDefinition, YAMLEnum
from meltano.core.utils import NotFound, find_named

from .command import Command

logger = logging.getLogger(__name__)


class VariantNotFoundError(Exception):
    def __init__(self, plugin: "PluginDefinition", variant_name):
        self.plugin = plugin
        self.variant_name = variant_name

    def __str__(self):
        return "{type} '{name}' variant '{variant}' is not known to Meltano. Variants: {variant_labels}".format(
            type=self.plugin.type.descriptor.capitalize(),
            name=self.plugin.name,
            variant=self.variant_name,
            variant_labels=self.plugin.variant_labels,
        )


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class PluginType(YAMLEnum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    TRANSFORMS = "transforms"
    MODELS = "models"
    DASHBOARDS = "dashboards"
    ORCHESTRATORS = "orchestrators"
    TRANSFORMERS = "transformers"
    FILES = "files"
    UTILITIES = "utilities"
    MAPPERS = "mappers"
    MAPPINGS = "mappings"

    def __str__(self):
        return self.value

    @property
    def descriptor(self):
        if self is self.__class__.FILES:
            return "file bundle"

        return self.singular

    @property
    def singular(self):
        """Makes it singular for `meltano add PLUGIN_TYPE`"""
        if self is self.__class__.UTILITIES:
            return "utility"

        return self.value[:-1]

    @property
    def verb(self):
        if self is self.__class__.TRANSFORMS:
            return self.singular
        if self is self.__class__.UTILITIES:
            return "utilize"
        if self is self.__class__.MAPPERS:
            return "map"

        return self.value[:-3]

    @classmethod
    def value_exists(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def cli_arguments(cls):
        args = [plugin_type.singular for plugin_type in cls]
        args.extend([plugin_type for plugin_type in cls])
        return args

    @classmethod
    def from_cli_argument(cls, value):
        for plugin_type in cls:
            if value in {plugin_type.value, plugin_type.singular}:
                return plugin_type

        raise ValueError(f"{value} is not a valid {cls.__name__}")


class PluginRef(Canonical):
    def __init__(self, plugin_type: Union[str, PluginType], name: str, **kwargs):
        self._type = (
            plugin_type
            if isinstance(plugin_type, PluginType)
            else PluginType(plugin_type)
        )

        super().__init__(name=name, **kwargs)

    @property
    def type(self):
        return self._type

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.name))

    def set_presentation_attrs(self, extras):
        self.update(
            hidden=extras.pop("hidden", None),
            label=extras.pop("label", None),
            logo_url=extras.pop("logo_url", None),
            description=extras.pop("description", None),
        )


class Variant(NameEq, Canonical):
    ORIGINAL_NAME = "original"
    DEFAULT_NAME = "default"

    def __init__(
        self,
        name: str = None,
        original: Optional[bool] = None,
        deprecated: Optional[bool] = None,
        docs: Optional[str] = None,
        repo: Optional[str] = None,
        pip_url: Optional[str] = None,
        executable: Optional[str] = None,
        capabilities: Optional[list] = [],
        settings_group_validation: Optional[list] = [],
        settings: Optional[list] = [],
        commands: Optional[dict] = None,
        **extras,
    ):
        super().__init__(
            name=name,
            original=original,
            deprecated=deprecated,
            docs=docs,
            repo=repo,
            pip_url=pip_url,
            executable=executable,
            capabilities=list(capabilities),
            settings_group_validation=list(settings_group_validation),
            settings=list(map(SettingDefinition.parse, settings)),
            commands=Command.parse_all(commands),
            extras=extras,
        )


class PluginDefinition(PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: str,
        variant: Optional[str] = None,
        variants: Optional[list] = [],
        **extras,
    ):
        super().__init__(plugin_type, name)

        self._defaults["label"] = lambda p: p.name

        def default_logo_url(plugin):
            short_name = re.sub(r"^(tap|target)-", "", plugin.name)
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
        for k, v in super().__iter__():
            if k == "variants" and len(v) == 1:
                # If there is only a single variant, its properties can be
                # nested in the plugin definition
                for variant_k, variant_v in v[0]:
                    if variant_k == "name":
                        variant_k = "variant"

                    yield (variant_k, variant_v)
            else:
                yield (k, v)

    def get_variant(self, variant_name: str) -> Variant:
        try:
            return find_named(self.variants, variant_name)
        except NotFound as err:
            raise VariantNotFoundError(self, variant_name) from err

    def find_variant(self, variant_or_name: Union[str, Variant] = None):
        if isinstance(variant_or_name, Variant):
            return variant_or_name

        if variant_or_name is None or variant_or_name == Variant.DEFAULT_NAME:
            return self.variants[0]

        if variant_or_name == Variant.ORIGINAL_NAME:
            try:
                return next(v for v in self.variants if v.original)
            except StopIteration:
                return self.variants[0]

        return self.get_variant(variant_or_name)

    def variant_label(self, variant):
        """Return label for specified variant."""
        variant = self.find_variant(variant)

        label = variant.name or Variant.ORIGINAL_NAME
        if variant == self.variants[0]:
            label = f"{label} (default)"
        elif variant.deprecated:
            label = f"{label} (deprecated)"

        return label

    @property
    def variant_labels(self):
        """Return labels for supported variants."""
        return ", ".join([self.variant_label(variant) for variant in self.variants])


class BasePlugin(HookObject):
    EXTRA_SETTINGS = []

    def __init__(self, plugin_def: PluginDefinition, variant: Variant):
        super().__init__()

        self._plugin_def = plugin_def
        self._variant = variant

    def __eq__(self, other):
        return (
            self._plugin_def == other._plugin_def  # noqa: WPS437
            and self._variant == other._variant  # noqa: WPS437
        )

    def __hash__(self):
        return hash((self._plugin_def, self._variant))

    def __iter__(self):
        yield from self._plugin_def

    def __getattr__(self, attr):
        try:
            return getattr(self._plugin_def, attr)
        except AttributeError:
            return getattr(self._variant, attr)

    @property
    def variant(self):
        return self._variant.name

    @property
    def executable(self):
        return self._variant.executable or self._plugin_def.name

    @property
    def extras(self):
        return {**self._plugin_def.extras, **self._variant.extras}

    @property
    def all_commands(self):
        """Return a dictonary of supported commands."""
        return self._variant.commands

    @property
    def test_commands(self) -> Dict[str, Command]:
        """Return a the test command for this plugin."""
        return {
            name: command
            for name, command in self.all_commands.items()
            if name.startswith("test")
        }

    @property
    def extra_settings(self):
        defaults = {f"_{k}": v for k, v in self.extras.items()}

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

    def env_prefixes(self, for_writing=False):
        """Return environment variable prefixes to use for settings."""
        return [self.name, self.namespace]

    def is_installable(self):
        return self.pip_url is not None

    def is_invokable(self):
        return self.is_installable() or self.executable is not None

    def is_configurable(self):
        return True

    def should_add_to_file(self):
        return True

    @property
    def runner(self):
        return None

    def exec_args(self, files: Dict):
        return []

    @property
    def config_files(self):
        """Return a list of stubbed files created for this plugin."""
        return dict()

    @property
    def output_files(self):
        return dict()

    def process_config(self, config):
        return config
