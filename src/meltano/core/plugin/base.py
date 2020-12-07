import logging
import yaml
import fnmatch
import copy
from typing import Dict, Union
from collections import namedtuple
from enum import Enum
from typing import Optional, Iterable

from meltano.core.setting_definition import SettingDefinition
from meltano.core.behavior.hookable import HookObject
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior import NameEq
from meltano.core.utils import compact, find_named, NotFound, flatten

logger = logging.getLogger(__name__)


class VariantNotFoundError(Exception):
    def __init__(self, plugin: "PluginDefinition", variant_name):
        self.plugin = plugin
        self.variant_name = variant_name

        message = f"{plugin.type.descriptor.capitalize()} '{plugin.name}' variant '{variant_name}' is not known to Meltano. "
        message += f"Variants: {plugin.list_variant_names()}"

        super().__init__(message)


class YAMLEnum(str, Enum):
    def __str__(self):
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


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
        return self.value[:-1]

    @property
    def verb(self):
        if self is self.__class__.TRANSFORMS:
            return self.singular

        return self.value[:-3]

    @classmethod
    def value_exists(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def cli_arguments(cls):
        args = [type.singular for type in cls]
        args.extend([type for type in cls])
        return args

    @classmethod
    def from_cli_argument(cls, value):
        if not value.endswith("s"):
            value += "s"

        return cls(value)


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

    @property
    def info(self):
        return {"name": self.name}

    @property
    def info_env(self):
        # MELTANO_EXTRACTOR_...
        return flatten({"meltano": {self.type.singular: self.info}}, "env_var")

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.name))


class Variant(NameEq, Canonical):
    ORIGINAL_NAME = "original"

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
            extras=extras,
        )


class PluginDefinition(PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: str,
        hidden: Optional[bool] = None,
        label: Optional[str] = None,
        logo_url: Optional[str] = None,
        description: Optional[str] = None,
        variant: Optional[str] = None,
        variants: Optional[list] = [],
        **extras,
    ):
        if not variants:
            variant = Variant(variant, **extras)

            # Any properties considered "extra" by the variant should be
            # considered extras of the plugin definition.
            extras = variant.extras
            variant.extras = {}

            variants = [variant]

        super().__init__(
            plugin_type,
            name,
            # Attributes will be listed in meltano.yml in this order:
            namespace=namespace,
            hidden=hidden,
            label=label,
            logo_url=logo_url,
            description=description,
            extras=extras,
            variants=list(map(Variant.parse, variants)),
        )

        self.use_variant(variant)

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

    @property
    def info(self):
        return {
            **super().info,
            "namespace": self.namespace,
            "variant": self.current_variant_name or Variant.ORIGINAL_NAME,
        }

    @property
    def current_variant_name(self):
        return self._current_variant_name

    def get_variant(self, variant_name: str) -> Variant:
        try:
            return find_named(self.variants, variant_name)
        except NotFound as err:
            raise VariantNotFoundError(self, variant_name) from err

    def use_variant(self, variant_or_name: Union[str, Variant] = None):
        if variant_or_name is None:
            variant = self.variants[0]
        elif isinstance(variant_or_name, Variant):
            variant = variant_or_name
        elif variant_or_name == Variant.ORIGINAL_NAME:
            try:
                variant = next(v for v in self.variants if v.original)
            except StopIteration:
                variant = self.variants[0]
        else:
            variant = self.get_variant(variant_or_name)

        self._current_variant_name = variant.name

    @property
    def current_variant(self):
        return self.get_variant(self.current_variant_name)

    def list_variant_names(self):
        names = []

        for i, variant in enumerate(self.variants):
            name = variant.name or Variant.ORIGINAL_NAME

            if i == 0:
                name += " (default)"
            elif variant.deprecated:
                name += " (deprecated)"

            names.append(name)

        return ", ".join(names)

    @property
    def all_extras(self):
        return {**self.extras, **self.current_variant.extras}

    def __getattr__(self, attr):
        try:
            return super().__getattr__(attr)
        except AttributeError:
            return getattr(self.current_variant, attr)
