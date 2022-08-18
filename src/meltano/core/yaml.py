"""YAML instance."""

from __future__ import annotations

from ruamel.yaml import YAML

from meltano.core.behavior.canonical import Canonical
from meltano.core.discovery_file import DiscoveryFile
from meltano.core.plugin import PluginType
from meltano.core.setting_definition import SettingKind

yaml = YAML()
yaml.default_flow_style = False

yaml.register_class(Canonical)
yaml.register_class(PluginType)
yaml.register_class(SettingKind)
yaml.register_class(DiscoveryFile)
