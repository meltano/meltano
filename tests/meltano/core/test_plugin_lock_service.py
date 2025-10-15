from __future__ import annotations

import json
import typing as t

import pytest

from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLockService,
)

if t.TYPE_CHECKING:
    from meltano.core.project import Project


@pytest.fixture
def plugin():
    plugin_definition = PluginDefinition(
        PluginType.EXTRACTORS,
        name="tap-locked",
        namespace="tap_locked",
        foo="bar",
        variants=[
            {
                "name": "meltano",
                "pip_url": "meltano-tap-locked",
                "repo": "https://gitlab.com/meltano/tap-locked",
                "baz": "qux",
            },
            {
                "name": "singer-io",
                "original": True,
                "deprecated": True,
                "pip_url": "tap-locked",
                "repo": "https://github.com/singer-io/tap-locked",
            },
        ],
    )
    variant = plugin_definition.find_variant("meltano")
    base_plugin = BasePlugin(plugin_definition, variant)

    parent_plugin = ProjectPlugin(
        base_plugin.type,
        base_plugin.name,
        variant="meltano",
    )
    parent_plugin.parent = base_plugin

    plugin = ProjectPlugin(
        base_plugin.type,
        f"{base_plugin.name}--two",
        inherit_from=parent_plugin.name,
    )
    plugin.parent = parent_plugin
    return plugin


class TestPluginLockService:
    @pytest.fixture
    def subject(self, project: Project):
        return PluginLockService(project)

    def test_save(self, subject: PluginLockService, plugin: ProjectPlugin) -> None:
        plugin_lock_path = subject.plugin_lock_path(
            plugin=plugin,
            variant_name=plugin.variant,
        )
        assert not plugin_lock_path.exists()

        subject.save(plugin)
        assert plugin_lock_path.exists()

        with plugin_lock_path.open() as lock_file:
            lock_json = json.load(lock_file)
            assert lock_json["foo"] == "bar"
            assert lock_json["baz"] == "qux"

        with pytest.raises(LockfileAlreadyExistsError):
            subject.save(plugin)
