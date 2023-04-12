"""Meltano Setting Definitions."""

from __future__ import annotations

import ast
import json
import typing as t
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum

from ruamel.yaml import Representer

from meltano.core import utils
from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.error import Error

VALUE_PROCESSORS = {
    "nest_object": utils.nest_object,
    "upcase_string": lambda vlu: vlu.upper(),
    "stringify": lambda vlu: vlu if isinstance(vlu, str) else json.dumps(vlu),
}


class EnvVar:
    """Environment Variable class."""

    def __init__(self, definition: str):
        """Instantiate new EnvVar.

        Args:
            definition: Env var definition.
        """
        key = definition
        negated = False

        if definition.startswith("!"):
            key = definition[1:]
            negated = True

        self.key = key
        self.negated = negated

    @property
    def definition(self) -> str:
        """Return env var definition.

        Returns:
            Env var definition.
        """
        prefix = "!" if self.negated else ""
        return f"{prefix}{self.key}"

    def get(self, env) -> str:
        """Get env value.

        Args:
            env: Env to get value for.

        Returns:
            Env var value for given env var.
        """
        value = env[self.key]
        return str(not utils.truthy(value)) if self.negated else value


class SettingMissingError(Error):
    """A setting is missing."""

    def __init__(self, name: str):
        """Instantiate SettingMissingError.

        Args:
            name: Name of missing setting.
        """
        super().__init__(f"Cannot find setting {name}")


class YAMLEnum(str, Enum):
    """Serializable Enum class."""

    def __str__(self):
        """Return as string.

        Returns:
            This enum in string form.
        """
        return self.value

    @staticmethod
    def yaml_representer(dumper, obj) -> str:
        """Represent as yaml.

        Args:
            dumper: YAML dumper.
            obj: Object to dump.

        Returns:
            Object in yaml string form.
        """
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))

    @classmethod
    def to_yaml(cls, representer: Representer, node: t.Any):
        """Represent as yaml.

        Args:
            representer: YAML representer.
            node: Object to dump.

        Returns:
            Object in yaml string form.
        """
        return representer.represent_scalar("tag:yaml.org,2002:str", str(node))

    @classmethod
    def from_yaml(
        cls,
        constructor,  # noqa: ARG003
        node,
    ):
        """Construct from yaml.

        Args:
            constructor: Class constructor.
            node: YAML node.

        Returns:
            Object from yaml node.
        """
        return cls(node.value)


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


ParseValueExpectedType = t.TypeVar("ParseValueExpectedType")


class SettingDefinition(NameEq, Canonical):
    """Meltano SettingDefinition class."""

    def __init__(
        self,
        name: str | None = None,
        aliases: list[str] | None = None,
        env: str | None = None,
        env_aliases: list[str] | None = None,
        kind: SettingKind | None = None,
        value=None,
        label: str | None = None,
        documentation: str | None = None,
        description: str | None = None,
        tooltip: str | None = None,
        options: list | None = None,
        oauth: dict | None = None,
        placeholder: str | None = None,
        protected: bool | None = None,
        env_specific: bool | None = None,
        custom: bool = False,
        value_processor=None,
        value_post_processor=None,
        **attrs,
    ):
        """Instantiate new SettingDefinition.

        Args:
            name: Setting name.
            aliases: Setting alias names.
            env: Setting target environment variable.
            env_aliases: Deprecated. Used to delegate alternative environment
                variables for overriding this setting's value.
            kind: Setting kind.
            value: Setting value.
            label: Setting label.
            documentation: Setting docs url.
            description: Setting description.
            tooltip: A phrase to provide additional information on this setting.
            options: Setting options.
            oauth: Setting OAuth provider details.
            placeholder: A placeholder value for this setting.
            protected: A protected setting cannot be changed from the UI.
            env_specific: Flag for environment-specific setting.
            custom: Custom setting flag.
            value_processor: Used with `kind: object` to pre-process the keys
                in a particular way.
            value_post_processor: Used with `kind: object` to post-process the
                keys in a particular way.
            attrs: Keyword arguments to pass to parent class.
        """
        aliases = aliases or []
        env_aliases = env_aliases or []
        options = options or []
        oauth = oauth or {}

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

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation of this setting.
        """
        return f"<SettingDefinition {self.name} ({self.kind})>"

    @classmethod
    def from_missing(cls, defs: t.Iterable[SettingDefinition], config: dict, **kwargs):
        """Create SettingDefinition instances for missing settings.

        Args:
            defs: Know setting definitions.
            config: Config dict.
            kwargs: Keyword arguments to pass to new SettingDefinition instances.

        Returns:
            A list of created custom SettingDefinition instances.
        """
        flat_config = utils.flatten(config, "dot")

        names = {setting.name for setting in defs}

        # Create custom setting definitions for unknown keys
        return [
            SettingDefinition.from_key_value(key, value, **kwargs)
            for key, value in flat_config.items()
            if key not in names
        ]

    @classmethod
    def from_key_value(
        cls,
        key: str,
        value: t.Any,
        custom: bool = True,
        default: t.Any | bool = False,
    ):
        """Create SettingDefinition instance from key-value pair.

        Args:
            key: Key.
            value: Value.
            custom: Custom setting flag.
            default: Default setting value.

        Returns:
            A SettingDefinition instance.
        """
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
    def is_extra(self) -> bool:
        """Return whether setting is a config extra.

        See https://docs.meltano.com/reference/command-line-interface#how-to-use-plugin-extras

        Returns:
            True if setting is a config extra.
        """  # noqa: E501
        return self.name.startswith("_")

    @property
    def is_custom(self) -> bool:
        """Return whether the setting is custom, i.e. user-defined in `meltano.yml`.

        Returns:
            True if the setting is custom (user defined).
        """
        return self._custom

    @property
    def is_redacted(self) -> bool:
        """Return whether the setting value is redacted.

        Returns:
            True if setting value is redacted.
        """
        return self.kind in {SettingKind.PASSWORD, SettingKind.OAUTH}

    def env_vars(
        self,
        prefixes: list[str],
        include_custom: bool = True,
        for_writing: bool = False,
    ) -> list[EnvVar]:
        """Return environment variables with the provided prefixes.

        Args:
            prefixes: Env var prefixes to prepend.
            include_custom: Include custom env vars from `env_aliases`.
            for_writing: Include target env var from `env`.

        Returns:
            A list of EnvVar instances for this setting definition.
        """
        env_keys = []

        if self.env and for_writing:
            # this ensures we only write to specified `env:`
            env_keys.append(self.env)

        env_keys.extend(utils.to_env_var(prefix, self.name) for prefix in prefixes)
        if not for_writing:
            # read from setting name aliases
            for alias in self.aliases:
                env_keys.extend(utils.to_env_var(prefix, alias) for prefix in prefixes)

        if include_custom:
            env_keys.extend(self.env_aliases)

        return [EnvVar(key) for key in utils.uniques_in(env_keys)]

    @staticmethod
    def _parse_value(
        unparsed: str,
        expected_type_name: str,
        expected_type: type[ParseValueExpectedType],
    ) -> ParseValueExpectedType:
        """Parse a JSON string.

        Parsing is attempted first with `json.loads`, and then with
        `ast.literal_eval` as a fallback. It is used as a fallback because it
        correctly parses most inputs that `json.loads` can parse, but is more
        liberal about what it accepts. For example, `json.loads` requires
        double quotes for strings, but `ast.literal_eval` can use either single
        or double quotes.

        Args:
            unparsed: The JSON string.
            expected_type_name: The name of the expected type, e.g. "array".
                Used in the error message if parsing fails or the type is not
                as expected.
            expected_type: The Python type class of the expected type. Used to
                ensure that the parsed value is of the expected type.

        Raises:
            parse_error: Parsing failed, or the parsed value had an unexpected type.

        Returns:
            The parsed value.
        """
        parse_error = ValueError(
            f"Failed to parse JSON {expected_type_name} from string: {unparsed!r}",
        )
        try:
            parsed = json.loads(unparsed)
        except json.JSONDecodeError:
            try:  # noqa: WPS505
                parsed = ast.literal_eval(unparsed)
            except (
                ValueError,
                TypeError,
                SyntaxError,
                MemoryError,
                RecursionError,
            ) as ex:
                raise parse_error from ex
        if not isinstance(parsed, expected_type):
            raise parse_error
        return parsed

    def cast_value(self, value: t.Any) -> t.Any:  # noqa: C901
        """Cast given value.

        Args:
            value: Value to cast.

        Returns:
            Value cast according to specified setting definition kind.
        """
        value = value.isoformat() if isinstance(value, (date, datetime)) else value

        if isinstance(value, str):
            if self.kind == SettingKind.BOOLEAN:
                return utils.truthy(value)
            elif self.kind == SettingKind.INTEGER:
                return int(value)
            elif self.kind == SettingKind.OBJECT:
                value = dict(
                    self._parse_value(value, "object", Mapping),  # type: ignore
                )
            elif self.kind == SettingKind.ARRAY:
                value = list(
                    self._parse_value(value, "array", Sequence),  # type: ignore
                )

        processor = self.value_processor
        if value is not None and processor:
            if isinstance(processor, str):
                processor = VALUE_PROCESSORS[processor]
            value = processor(value)

        return value

    def post_process_value(self, value: t.Any) -> t.Any:
        """Post-process given value.

        Args:
            value: Value to post-process.

        Returns:
            Value post-processed according to any post-processors specified for this
            setting definition.
        """
        processor = self.value_post_processor
        if value is not None and processor:
            if isinstance(processor, str):
                processor = VALUE_PROCESSORS[processor]
            value = processor(value)

        return value

    def stringify_value(self, value: t.Any) -> str:
        """Return value in string form.

        Args:
            value: Value to stringify

        Returns:
            String form of the passed value.
        """
        if isinstance(value, str):
            return value

        if not self.kind or self.kind == SettingKind.STRING:
            return str(value)

        return json.dumps(value)
