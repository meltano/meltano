import yaml
import fnmatch
import copy
from typing import Dict, Union
from collections import namedtuple
from enum import Enum
from typing import Optional, Iterable

from meltano.core.behavior.hookable import HookObject
from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior import NameEq
from meltano.core.utils import compact, find_named, NotFound


class YAMLEnum(str, Enum):
    def __str__(self):
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class Profile(NameEq, Canonical):
    def __init__(self, name: str = None, label: str = None, config={}):
        self.name = name
        self.label = label
        self.config = config


Profile.DEFAULT = Profile(name="default", label="Default")


class SettingDefinition(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
        env: str = None,
        kind: str = None,
        value=None,
        label: str = None,
        documentation: str = None,
        description: str = None,
        tooltip: str = None,
        options: list = [],
        oauth: dict = {},
        placeholder: str = None,
        protected=False,
        **attrs,
    ):
        super().__init__(
            name=name,
            env=env,
            kind=kind,
            value=value,
            label=label,
            documentation=documentation,
            description=description,
            tooltip=tooltip,
            options=options,
            oauth=oauth,
            placeholder=placeholder,
            protected=protected,
            **attrs,
        )


class PluginType(YAMLEnum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    TRANSFORMS = "transforms"
    MODELS = "models"
    DASHBOARDS = "dashboards"
    ORCHESTRATORS = "orchestrators"
    TRANSFORMERS = "transformers"

    def __str__(self):
        return self.value

    @property
    def cli_command(self):
        """Makes it singular for `meltano add PLUGIN_TYPE`"""
        return self.value[:-1]

    @classmethod
    def value_exists(cls, value):
        return value in cls._value2member_map_


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

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.name, self.current_profile_name))


class PluginInstall(HookObject, Canonical, PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        pip_url: Optional[str] = None,
        select=set(),
        config={},
        profiles=set(),
        executable: str = None,
        **attrs,
    ):
        super().__init__(plugin_type, name, **attrs)

        self.config = copy.deepcopy(config)
        self.profiles = set(map(Profile.parse, profiles))
        self.select = select
        self.pip_url = pip_url
        self.executable = executable
        self._extras = attrs

    def is_installable(self):
        return self.pip_url is not None

    def is_custom(self):
        try:
            return bool(self.namespace)
        except AttributeError:
            return False

    def get_profile(self, profile_name: str) -> Profile:
        if profile_name == Profile.DEFAULT.name:
            return Profile.DEFAULT

        return find_named(self.profiles, profile_name)

    def use_profile(self, profile_or_name: Union[str, Profile]):
        if profile_or_name is None:
            profile = Profile.DEFAULT
        elif isinstance(profile_or_name, Profile):
            profile = self.get_profile(profile_or_name.name)
        else:
            profile = self.get_profile(profile_or_name)

        self._current_profile_name = profile.name

    @property
    def current_profile(self):
        return self.get_profile(self.current_profile_name)

    @property
    def current_config(self):
        if self.current_profile is Profile.DEFAULT:
            return self.config

        return self.current_profile.config

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
        self.select.add(filter)

    def add_profile(self, name: str, config: dict = None, label: str = None):
        profile = Profile(name=name, config=config, label=label)

        self.profiles.add(profile)
        return profile


class Plugin(Canonical, PluginRef):
    """
    Args:
    name: The unique name for the installed plugin
    pip_url: The pip-compatible installation URI, like `git+https://…` or `-e /path/to/pkg`
    executable: The plugin executable name (default: <name>)
    """

    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: str,
        pip_url: Optional[str] = None,
        settings: list = [],
        settings_group_validation: list = [],
        docs=None,
        description=None,
        capabilities=set(),
        select=set(),
        **attrs,
    ):
        super().__init__(plugin_type, name, **attrs)

        self.namespace = namespace
        self.pip_url = pip_url
        self.settings = list(map(SettingDefinition.parse, settings))
        self.settings_group_validation = list(settings_group_validation)
        self.docs = docs
        self.description = description
        self.capabilities = set(capabilities)
        self.select = set(select)
        self._extras = attrs

    def as_installed(self) -> PluginInstall:
        return PluginInstall(
            self.type,
            self.name,
            pip_url=self.pip_url,
            select=self.select,
            **self._extras,
        )
