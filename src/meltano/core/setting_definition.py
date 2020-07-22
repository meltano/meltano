import json
from typing import List

from .utils import truthy, flatten, nest_object
from .behavior.canonical import Canonical
from .behavior import NameEq
from .error import Error

VALUE_PROCESSORS = {"nest_object": nest_object}


class SettingMissingError(Error):
    """Occurs when a setting is missing."""

    def __init__(self, name: str):
        super().__init__(f"Cannot find setting {name}")


class SettingDefinition(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
        aliases: List[str] = [],
        env: str = None,
        env_aliases: List[str] = [],
        kind: str = None,
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
        **attrs,
    ):
        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            name=name,
            aliases=aliases,
            env=env,
            env_aliases=env_aliases,
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
            env_specific=env_specific,
            value_processor=value_processor,
            _custom=custom,
            **attrs,
        )

        self._verbatim.add("value")

    @classmethod
    def from_missing(cls, defs, config, **kwargs):
        flat_config = flatten(config, "dot")

        names = set(s.name for s in defs)

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
            kind = "boolean"

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
    def is_redacted(self):
        return self.kind in ("password", "oauth")

    @property
    def env_alias_getters(self):
        getters = {}

        for alias in self.env_aliases:
            key = alias

            if alias.startswith("!") and self.kind == "boolean":
                key = alias[1:]
                getter = lambda env, key=key: str(not truthy(env[key]))
            else:
                getter = lambda env, key=alias: env[key]

            getters[key] = getter

        return getters

    def cast_value(self, value):
        if isinstance(value, str):
            if self.kind == "boolean":
                return truthy(value)
            elif self.kind == "integer":
                return int(value)
            elif self.kind == "object":
                value = json.loads(value)
                if not isinstance(value, dict):
                    raise ValueError(f"JSON value '{value}' is not an object")
            elif self.kind == "array":
                value = json.loads(value)
                if not isinstance(value, list):
                    raise ValueError(f"JSON value '{value}' is not an array")

        processor = self.value_processor
        if value is not None and processor:
            if isinstance(processor, str):
                processor = VALUE_PROCESSORS[processor]
            value = processor(value)

        return value
