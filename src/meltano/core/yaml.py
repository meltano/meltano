"""YAML instance."""

from __future__ import annotations

import os
import sys
import typing as t
import uuid
from contextlib import suppress
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from ruamel.yaml import YAML

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginType
from meltano.core.setting_definition import SettingKind
from meltano.core.user_config import UserConfigReadError, get_user_config_service
from meltano.core.utils import hash_sha256, truthy

if t.TYPE_CHECKING:
    from ruamel.yaml import CommentedMap, Dumper, ScalarNode

yaml = YAML()
yaml.default_flow_style = False
yaml.width = sys.maxsize  # Prevent line wrapping entirely


def _represent_decimal(dumper: Dumper, node: Decimal) -> ScalarNode:
    """Represent a decimal.Decimal instance in YAML."""
    return dumper.represent_scalar("tag:yaml.org,2002:float", str(node))


def _represent_uuid(dumper: Dumper, node: uuid.UUID) -> ScalarNode:
    """Represent a uuid.UUID instance in YAML."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(node))


yaml.register_class(Canonical)
yaml.register_class(PluginType)
yaml.register_class(SettingKind)
yaml.representer.add_representer(Decimal, _represent_decimal)
yaml.representer.add_representer(uuid.UUID, _represent_uuid)


@dataclass(slots=True)
class CachedCommentedMap:
    """The hash of the raw bytes of a YAML file, and its parsed content."""

    sha256: str
    data: CommentedMap


cache: dict[os.PathLike[str], CachedCommentedMap] = {}


def load(path: os.PathLike[str]) -> CommentedMap:
    """Load the specified YAML file with caching.

    The cache is used if both the file path and its content hash match what is stored.

    Parameters:
        path: The path to the YAML file.

    Returns:
        The loaded YAML file.
    """
    path = Path(path).resolve()
    with path.open() as yaml_file:
        hashed = hash_sha256(yaml_file.read())

        if path in cache and cache[path].sha256 == hashed:
            return cache[path].data

        yaml_file.seek(0)
        parsed = yaml.load(yaml_file)

    cache[path] = CachedCommentedMap(hashed, parsed)
    return parsed


def _apply_user_configuration(yaml_instance: YAML) -> None:
    """Apply user configuration to YAML instance if enabled."""
    if not truthy(os.getenv("MELTANO_DISABLE_USER_YAML_CONFIG", "false")):
        with suppress(UserConfigReadError):
            settings = get_user_config_service().yaml
            yaml_instance.indent(
                mapping=settings.indent,
                sequence=settings.indent + settings.block_seq_indent,
                offset=settings.sequence_dash_offset,
            )


def _create_configured_yaml_instance() -> YAML:
    """Create a YAML instance with user configuration applied.

    Returns:
        A configured YAML instance.
    """
    yaml_instance = YAML()
    yaml_instance.default_flow_style = False
    yaml_instance.width = yaml.width

    yaml_instance.representer.yaml_representers = deepcopy(
        yaml.representer.yaml_representers
    )
    yaml_instance.representer.yaml_multi_representers = deepcopy(
        yaml.representer.yaml_multi_representers
    )

    _apply_user_configuration(yaml_instance)

    return yaml_instance


def dump(data: object, stream: t.IO[str] | None = None, **kwargs: object) -> str | None:
    """Dump YAML with user-configured formatting.

    Args:
        data: The data to dump.
        stream: The stream to dump to. If None, returns YAML as string.
        **kwargs: Additional keyword arguments passed to yaml.dump.

    Returns:
        YAML string if stream is None, otherwise None.
    """
    yaml_instance = _create_configured_yaml_instance()

    if stream is None:
        from io import StringIO

        stream = StringIO()
        yaml_instance.dump(data, stream, **kwargs)
        return stream.getvalue()

    yaml_instance.dump(data, stream, **kwargs)
    return None
