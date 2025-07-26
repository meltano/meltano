"""YAML instance."""

from __future__ import annotations

import typing as t
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

    from meltano.core.yaml_config import YamlStyleConfig

yaml = YAML()
yaml.default_flow_style = False

# Storage for current YAML style configuration
_current_config: YamlStyleConfig | None = None


def _represent_decimal(dumper: Dumper, node: Decimal) -> ScalarNode:
    """Represent a decimal.Decimal instance in YAML."""
    return dumper.represent_scalar("tag:yaml.org,2002:float", str(node))


yaml.register_class(Canonical)
yaml.register_class(PluginType)
yaml.register_class(SettingKind)
yaml.representer.add_representer(Decimal, _represent_decimal)


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


def configure_yaml_style(config: YamlStyleConfig) -> None:
    """Configure the global YAML instance with style settings."""
    global _current_config
    _current_config = config

    # Apply indentation settings
    yaml.indent(
        mapping=config.indent.mapping,
        sequence=config.indent.sequence,
        offset=config.indent.offset,
    )

    # Apply other formatting settings
    yaml.width = config.width
    yaml.preserve_quotes = config.preserve_quotes

    # Note: compact_sequences would require more complex implementation
    # as it's not a direct ruamel.yaml setting. For now, we store it
    # in case future enhancements need it.


def get_yaml_config() -> YamlStyleConfig | None:
    """Get the current YAML style configuration."""
    return _current_config


def ensure_yaml_configured(
    project_data: CommentedMap | None = None,
    environment_name: str | None = None,
) -> None:
    """Ensure YAML is configured with the latest settings."""
    # Import here to avoid circular imports
    from meltano.core.yaml_config import YamlStyleConfig, load_yaml_style_config

    config = load_yaml_style_config(project_data, environment_name)

    # Only apply configuration if it's different from defaults
    if config != YamlStyleConfig():
        configure_yaml_style(config)


# Alias to provide a clean interface when using this
# module via `from meltano.core import yaml`
dump = yaml.dump
