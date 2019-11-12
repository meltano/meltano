import yaml
import fnmatch
from typing import Dict, Union
from collections import namedtuple
from enum import Enum
from typing import Optional, Iterable

from meltano.core.behavior.hookable import HookObject
from meltano.core.behavior.canonical import Canonical
from meltano.core.utils import compact, find_named


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
    ALL = "all"

    def __str__(self):
        return self.value

    @property
    def cli_command(self):
        """Makes it singular for `meltano add PLUGIN_TYPE`"""
        if self is self.__class__.ALL:
            raise NotImplemented()

        return self.value[:-1]

    @classmethod
    def value_exists(cls, value):
        return value in cls._value2member_map_


class PluginRef:
    def __init__(self, plugin_type: Union[str, PluginType], name: str):
        self.type = (
            plugin_type
            if isinstance(plugin_type, PluginType)
            else PluginType(plugin_type)
        )
        self.canonical_name, self.profile = self.parse_name(name)

    @classmethod
    def parse_name(cls, name: str):
        name, *profile = name.split("@")
        profile = next(iter(profile), None)

        return (name, profile)

    @property
    def qualified_name(self):
        parts = (self.type, self.canonical_name, self.profile)

        return ".".join(compact(parts))

    @property
    def name(self):
        parts = (self.canonical_name, self.profile)

        return "@".join(compact(parts))

    def __eq__(self, other):
        import pdb; pdb.set_trace()
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.type, self.canonical_name, self.profile))


class PluginInstall(HookObject, Canonical, PluginRef):
    _extras = {}

    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        pip_url: Optional[str] = None,
        select=set(),
        config={},
        profiles=[],
        **_extras
    ):
        super().__init__(plugin_type, name)

        self.config = Canonical.parse(config)
        self.profiles = list(map(Profile.parse, profiles))
        self.select = select
        self.pip_url = pip_url
        self._extras=_extras

    def installable(self):
        return self.pip_url is not None

    @property
    def current_config(self):
        if not self.profile:
            return self.config

        return find_named(self.profiles, self.profile)

    @property
    def executable(self):
        return self._extras.get("executable", self.canonical_name)

    @property
    def select(self):
        return self._select or {"*.*"}

    @select.setter
    def select(self, patterns):
        self._select = set(patterns)

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
        self._select.add(filter)

    def add_profile(self, name: str, config: dict = None, label: str = None):
        profile = Profile(name=name,
                          config=config,
                          label=label)

        self._profiles.append(profile)
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
        docs=None,
        description=None,
        capabilities=set(),
        **extras
    ):
        super().__init__(plugin_type, name)

        self.namespace = namespace
        self.pip_url = pip_url
        self.settings = settings
        self.docs = docs
        self.description = description
        self.capabilities = set(capabilities)
        self._extras = extras or {}

    def as_installed(self) -> PluginInstall:
        return PluginInstall(self.type, self.name, pip_url=self.pip_url, **self._extras)
