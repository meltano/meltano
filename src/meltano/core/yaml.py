"""YAML instance."""

from __future__ import annotations

from ruamel.yaml import YAML

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginType
from meltano.core.setting_definition import SettingKind


def configure_yaml() -> YAML:
    """Configure YAML instance.

    Returns:
        The configured YAML instance.
    """
    yaml = YAML()
    yaml.default_flow_style = False

    yaml.register_class(Canonical)
    yaml.register_class(PluginType)
    yaml.register_class(SettingKind)

    return yaml
