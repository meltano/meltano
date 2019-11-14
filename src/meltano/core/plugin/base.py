import yaml
import fnmatch
import copy
from typing import Dict, Union
from collections import namedtuple
from enum import Enum
from typing import Optional, Iterable

from meltano.core.behavior.hookable import HookObject
from meltano.core.behavior.canonical import Canonical
from meltano.core.utils import compact, find_named, NotFound


class YAMLEnum(str, Enum):
    def __str__(self):
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


yaml.add_multi_representer(YAMLEnum, YAMLEnum.yaml_representer)


class Profile(Canonical):
    pass


class PluginType(YAMLEnum):
    EXTRACTORS = "extractors"
    LOADERS = "loaders"
    MODELS = "models"
    TRANSFORMERS = "transformers"
    TRANSFORMS = "transforms"
    ORCHESTRATORS = "orchestrators"

    def __str__(self):
        return self.value

    @property
    def cli_command(self):
        """Makes it singular for `meltano add PLUGIN_TYPE`"""
        return self.value[:]

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
        self.name, self._current_profile = self.parse_name(name)

    @classmethod
    def parse_name(cls, name: str):
        name, *profile = name.split("@")
        profile = next(iter(profile), None)

        return (name, profile)

    @property
    def type(self):
        return self._type

    def use_profile(self, profile):
        try:
            # ensure the profile exists
            self._current_profile = find_named(plugin.profiles, plugin_ref.current_profile)
        except NotFound as err:
            raise PluginProfileMissingError(self.name, profile) from err

    @property
    def current_profile(self):
        return self._current_profile

    @property
    def qualified_name(self):
        parts = (self.type, self.name, self.current_profile)

        return ".".join(compact(parts))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.name, self.profile))


class PluginInstall(HookObject, Canonical, PluginRef):
    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        namespace: str = None,
        pip_url: Optional[str] = None,
        select=set(),
        config={},
        profiles=set(),
        executable: str = None,
        **attrs
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

    @property
    def current_config(self):
        if not self.current_profile:
            return self.config

        return find_named(self.profiles, self.current_profile).config

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
        profile = Profile(name=name,
                          config=config,
                          label=label)

        self.profiles.add(profile)
        return profile


class SettingDefinition(Canonical):
    def __init__(self,
                 name: str = None,
                 env: str = None,
                 kind: str = None,
                 value = None,
                 label: str = None,
                 documentation: str = None,
                 description: str = None,
                 tooltip: str = None,
                 options: list = [],
                 protected = False):
        super().__init__(name=name,
                         env=env,
                         kind=kind,
                         value=value,
                         label=label,
                         documentation=documentation,
                         description=description,
                         protected=protected)


    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)



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
        docs=None,
        description=None,
        capabilities=set(),
        **attrs
    ):
        super().__init__(plugin_type, name, **attrs)

        self.namespace = namespace
        self.pip_url = pip_url
        self.settings = list(map(SettingDefinition.parse, settings))
        self.docs = docs
        self.description = description
        self.capabilities = set(capabilities)
        self._extras = attrs

    def as_installed(self) -> PluginInstall:
        return PluginInstall(self.type,
                             self.name,
                             pip_url=self.pip_url,
                             **self._extras)
