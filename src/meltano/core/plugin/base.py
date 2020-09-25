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


class Profile(NameEq, Canonical):
    def __init__(self, name: str = None, label: str = None, config={}, **extras):
        super().__init__(name=name, label=label, config=config, extras=extras)


Profile.DEFAULT = Profile(name="default", label="Default")


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


class PluginRef:
    def __init__(self, plugin_type: Union[str, PluginType], name: str):
        self._type = (
            plugin_type
            if isinstance(plugin_type, PluginType)
            else PluginType(plugin_type)
        )
        self.name, self._current_profile_name = self.parse_name(name)

    @classmethod
    def parse_name(cls, name: str):
        name, *profile_name = name.split("@")
        profile_name = next(iter(profile_name), Profile.DEFAULT.name)

        return (name, profile_name)

    @property
    def type(self):
        return self._type

    @property
    def current_profile_name(self):
        return self._current_profile_name

    @property
    def full_name(self):
        return f"{self.name}@{self.current_profile_name}"

    @property
    def qualified_name(self):
        parts = (self.type, self.name, self.current_profile_name)

        return ".".join(compact(parts))

    @property
    def info(self):
        return {"name": self.name, "profile": self.current_profile_name}

    @property
    def info_env(self):
        # MELTANO_EXTRACTOR_...
        return flatten({"meltano": {self.type.singular: self.info}}, "env_var")

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.name, self.current_profile_name))


class ProjectPlugin(HookObject, Canonical, PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: Optional[str] = None,
        custom_definition: Optional["PluginDefinition"] = None,
        variant: Optional[str] = None,
        pip_url: Optional[str] = None,
        config: Optional[dict] = {},
        profiles: Optional[list] = [],
        **extras,
    ):
        if namespace:
            custom_definition = PluginDefinition(
                plugin_type, name, namespace, variant=variant, pip_url=pip_url, **extras
            )
            extras = {}

        if custom_definition:
            # Any properties considered "extra" by the embedded plugin definition
            # should be considered extras of the project plugin, since they are
            # the current values, not default values.
            extras = {**custom_definition.extras, **extras}
            custom_definition.extras = {}

        super().__init__(
            plugin_type,
            name,
            # Attributes will be listed in meltano.yml in this order:
            custom_definition=custom_definition,
            variant=variant,
            pip_url=pip_url,
            config=copy.deepcopy(config),
            extras=extras,
            profiles=list(map(Profile.parse, profiles)),
        )

        self._flattened.add("custom_definition")

    def is_installable(self):
        return self.pip_url is not None

    def is_invokable(self):
        return self.is_installable()

    def is_configurable(self):
        return True

    def should_add_to_file(self, project):
        return True

    @property
    def runner(self):
        return None

    @property
    def extra_settings(self):
        return []

    def is_custom(self):
        return self.custom_definition is not None

    def get_profile(self, profile_name: str) -> Profile:
        if profile_name == Profile.DEFAULT.name:
            return Profile.DEFAULT

        return find_named(self.profiles, profile_name)

    def use_profile(self, profile_or_name: Union[str, Profile]):
        if profile_or_name is None:
            profile = Profile.DEFAULT
        elif isinstance(profile_or_name, Profile):
            profile = profile_or_name
        else:
            profile = self.get_profile(profile_or_name)

        self._current_profile_name = profile.name

    @property
    def current_profile(self):
        return self.get_profile(self.current_profile_name)

    @property
    def current_config(self):
        return (
            self.config
            if self.current_profile is Profile.DEFAULT
            else self.current_profile.config
        )

    @property
    def current_extras(self):
        return (
            self.extras
            if self.current_profile is Profile.DEFAULT
            else self.current_profile.extras
        )

    def exec_args(self, files: Dict):
        return []

    @property
    def config_files(self):
        """Return a list of stubbed files created for this plugin."""
        return dict()

    @property
    def output_files(self):
        return dict()

    def add_select_filter(self, filter: str):
        select = self.extras.get("select", [])
        select.append(filter)
        self.extras["select"] = select

    def add_profile(self, name: str, config: dict = None, label: str = None):
        profile = Profile(name=name, config=config, label=label)

        self.profiles.append(profile)
        return profile

    def process_config(self, config):
        return config


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


class PluginDefinition(Canonical, PluginRef):
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

    def get_variant(self, variant_name: str) -> Profile:
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
        return getattr(self.current_variant, attr)

    def in_project(self, custom=False) -> ProjectPlugin:
        return ProjectPlugin(
            self.type,
            self.name,
            variant=self.current_variant_name,
            pip_url=self.pip_url,
            custom_definition=(self if custom else None),
        )
