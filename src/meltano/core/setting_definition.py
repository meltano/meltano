from typing import List

from .utils import truthy
from .behavior.canonical import Canonical
from .behavior import NameEq
from .error import Error


class SettingMissingError(Error):
    """Occurs when a setting is missing."""

    def __init__(self, name: str):
        super().__init__(f"Cannot find setting {name}")


class SettingDefinition(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
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
        **attrs,
    ):
        super().__init__(
            # Attributes will be listed in meltano.yml in this order:
            name=name,
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
            _custom=custom,
            **attrs,
        )

        self._verbatim.add("value")

    @classmethod
    def from_key_value(cls, key, value):
        kind = None
        if isinstance(value, bool):
            kind = "boolean"

        return cls(name=key, kind=kind, custom=True)

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

        return value
