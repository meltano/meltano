"""YAML instance."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML, CommentedMap

from meltano.core.behavior.canonical import Canonical
from meltano.core.discovery_file import DiscoveryFile
from meltano.core.plugin import PluginType
from meltano.core.setting_definition import SettingKind
from meltano.core.utils import hash_sha256

yaml = YAML()
yaml.default_flow_style = False

yaml.register_class(Canonical)
yaml.register_class(PluginType)
yaml.register_class(SettingKind)
yaml.register_class(DiscoveryFile)


@dataclass
class CachedCommentedMap:
    """The hash of the raw bytes of a YAML file, and its parsed content."""

    sha256: str
    data: CommentedMap


cache: dict[os.PathLike, CachedCommentedMap] = {}


def load(path: os.PathLike) -> CommentedMap:
    """Load the specified YAML file with caching.

    The cache is used if both the file path and its content hash match what is stored.

    Parameters:
        path: The path to the YAML file.

    Returns:
        The loaded YAML file.
    """
    path = Path(path).resolve()
    with open(path) as yaml_file:
        hashed = hash_sha256(yaml_file.read())

        if path in cache and cache[path].sha256 == hashed:
            return cache[path].data

        yaml_file.seek(0)
        parsed = yaml.load(yaml_file)

    cache[path] = CachedCommentedMap(hashed, parsed)
    return parsed


# Alias to provide a clean interface when using this module via `from meltano.core import yaml`
dump = yaml.dump
