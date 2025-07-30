"""YAML instance."""

from __future__ import annotations

import os
import sys
import typing as t
import uuid
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


@dataclass
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


def dump(data: object, stream: t.IO[str] | None = None, **kwargs: object) -> None:
    """Dump YAML with user-configured formatting.

    Args:
        data: The data to dump.
        stream: The stream to dump to.
        **kwargs: Additional keyword arguments passed to yaml.dump.

    Returns:
        The result of yaml.dump.
    """
    yaml_instance = YAML()
    yaml_instance.default_flow_style = False

    if not truthy(os.getenv("MELTANO_DISABLE_USER_YAML_CONFIG", "false")):
        try:
            user_config_service = get_user_config_service()
            settings = user_config_service.yaml_settings()

            indent_raw = settings.get("indent", 2)
            block_seq_indent_raw = settings.get("block_seq_indent", 0)
            sequence_dash_offset_raw = settings.get("sequence_dash_offset")

            indent = indent_raw if isinstance(indent_raw, int) else 2
            block_seq_indent = (
                block_seq_indent_raw if isinstance(block_seq_indent_raw, int) else 0
            )
            sequence_dash_offset = (
                sequence_dash_offset_raw
                if isinstance(sequence_dash_offset_raw, int)
                else max(0, indent - 2)
            )

            yaml_instance.indent(
                mapping=indent,
                sequence=indent + block_seq_indent,
                offset=sequence_dash_offset,
            )

            skip_keys = ("indent", "block_seq_indent", "sequence_dash_offset")
            for key, value in settings.items():
                if key not in skip_keys and hasattr(yaml_instance, key):
                    setattr(yaml_instance, key, value)
        except UserConfigReadError:
            pass

    return yaml_instance.dump(data, stream, **kwargs)
