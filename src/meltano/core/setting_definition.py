import json
from datetime import date, datetime
from enum import Enum
from typing import List

from .behavior import NameEq
from .behavior.canonical import Canonical
from .error import Error
from .utils import flatten, nest_object, to_env_var, truthy, uniques_in

VALUE_PROCESSORS = {
    "nest_object": nest_object,
    "upcase_string": lambda s: s.upper(),
    "stringify": lambda s: s if isinstance(s, str) else json.dumps(s),
}


class EnvVar:
    def __init__(self, definition):
        key = definition
        negated = False

        if definition.startswith("!"):
            key = definition[1:]
            negated = True

        self.key = key
        self.negated = negated

    @property
    def definition(self):
        prefix = "!" if self.negated else ""
        return f"{prefix}{self.key}"

    def get(self, env):
        if self.negated:
            return str(not truthy(env[self.key]))
        else:
            return env[self.key]


class SettingMissingError(Error):
    """Occurs when a setting is missing."""

    def __init__(self, name: str):
        super().__init__(f"Cannot find setting {name}")


class YAMLEnum(str, Enum):
    """Serializable Enum class."""

    def __str__(self):
        """Return as string."""
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj):
        """Represent as yaml."""
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))


class SettingKind(YAMLEnum):
    """Supported setting kinds."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE_ISO8601 = "date_iso8601"
    EMAIL = "email"
    PASSWORD = "password"  # noqa: S105
    OAUTH = "oauth"
    OPTIONS = "options"
    FILE = "file"
    ARRAY = "array"
    OBJECT = "object"
    HIDDEN = "hidden"


class SettingDefinition(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
        aliases: List[str] = [],
        env: str = None,
        env_aliases: List[str] = [],
        kind: SettingKind = None,
        value=None,
        label: str = None,
        documentation: str = None,
        description: str = None,
        tooltip: str = None,
        options: list = [],
        oauth: dict = {},
        placeholder: str = None,
        protected: bool = None,
        env_specific: bool = None,
        custom: bool = False,
        value_processor=None,
        value_post_processor=None,
        **attrs,
    ):
        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            name=name,
            aliases=aliases,
            env=env,
            env_aliases=env_aliases,
            kind=SettingKind(kind) if kind else None,
            value=value,
            label=label,
            documentation=documentation,
            description=description,
            tooltip=tooltip,
            options=options,
            oauth=oauth,
            placeholder=placeholder,
            protected=protected,
            env_specific=env_specific,
            value_processor=value_processor,
            value_post_processor=value_post_processor,
            _custom=custom,
            **attrs,
        )

        self._verbatim.add("value")

    @classmethod
    def from_missing(cls, defs, config, **kwargs):
        flat_config = flatten(config, "dot")

        names = {s.name for s in defs}

        # Create custom setting definitions for unknown keys
        return [
            SettingDefinition.from_key_value(k, v, **kwargs)
            for k, v in flat_config.items()
            if k not in names
        ]

    @classmethod
    def from_key_value(cls, key, value, custom=True, default=False):
        kind = None
        if isinstance(value, bool):
            kind = SettingKind.BOOLEAN
        elif isinstance(value, int):
            kind = SettingKind.INTEGER
        elif isinstance(value, dict):
            kind = SettingKind.OBJECT
        elif isinstance(value, list):
            kind = SettingKind.ARRAY

        attrs = {
            "name": key,
            "kind": kind,
            "custom": custom,
            "value": value if default else None,
        }

        return cls(**attrs)

    @property
    def is_extra(self):
        return self.name.startswith("_")

    @property
    def is_custom(self):
        """Return whether the setting is custom, i.e. user-defined in `meltano.yml`."""
        return self._custom

    @property
    def is_redacted(self):
        return self.kind in {SettingKind.PASSWORD, SettingKind.OAUTH}

    def env_vars(self, prefixes: [str], include_custom=True):
        """Return environment variables with the provided prefixes."""
        env_keys = []

        if self.env and include_custom:
            env_keys.append(self.env)

        env_keys.extend(to_env_var(prefix, self.name) for prefix in prefixes)

        if include_custom:
            env_keys.extend(alias for alias in self.env_aliases)

        return [EnvVar(key) for key in uniques_in(env_keys)]

    def cast_value(self, value):
        if isinstance(value, date) or isinstance(value, datetime):
            value = value.isoformat()

        if isinstance(value, str):
            if self.kind == SettingKind.BOOLEAN:
                return truthy(value)
            elif self.kind == SettingKind.INTEGER:
                return int(value)
            elif self.kind == SettingKind.OBJECT:
                value = json.loads(value)
                if not isinstance(value, dict):
                    raise ValueError(f"JSON value '{value}' is not an object")
            elif self.kind == SettingKind.ARRAY:
                value = json.loads(value)
                if not isinstance(value, list):
                    raise ValueError(f"JSON value '{value}' is not an array")

        processor = self.value_processor
        if value is not None and processor:
            if isinstance(processor, str):
                processor = VALUE_PROCESSORS[processor]
            value = processor(value)

        return value

    def post_process_value(self, value):
        processor = self.value_post_processor
        if value is not None and processor:
            if isinstance(processor, str):
                processor = VALUE_PROCESSORS[processor]
            value = processor(value)

        return value

    def stringify_value(self, value):
        if isinstance(value, str):
            return value

        if not self.kind or self.kind == SettingKind.STRING:
            return str(value)

        return json.dumps(value)
