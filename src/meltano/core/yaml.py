"""YAML instance."""

from __future__ import annotations

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
from meltano.core.utils import hash_sha256

if t.TYPE_CHECKING:
    import os

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


# Alias to provide a clean interface when using this
# module via `from meltano.core import yaml`
dump = yaml.dump
