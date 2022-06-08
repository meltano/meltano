import json

import pytest

from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_lock_service import (
    LockfileAlreadyExistsError,
    PluginLockService,
)
from meltano.core.project import Project


class TestPluginLockService:
    @pytest.fixture
    def subject(
        self,
        project: Project,
        # plugin_discovery_service: PluginDiscoveryService,
    ):
        return PluginLockService(project)

    @pytest.fixture
    def plugin(self):
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
            variant=variant,
        )
        parent_plugin.parent = base_plugin

        plugin = ProjectPlugin(
            base_plugin.type,
            f"{base_plugin.name}--two",
            inherit_from=parent_plugin.name,
        )
        plugin.parent = parent_plugin
        return plugin

    def test_save(
        self,
        subject: PluginLockService,
        project: Project,
        plugin: ProjectPlugin,
    ):
        lock_path = project.plugin_lock_path(
            plugin.definition.type,
            plugin.definition.name,
            plugin.variant.name,
        )
        assert not lock_path.exists()

        subject.save(plugin)
        assert lock_path.exists()

        with lock_path.open() as lock_file:
            lock_json = json.load(lock_file)
            assert lock_json["foo"] == "bar"
            assert lock_json["baz"] == "qux"

        with pytest.raises(LockfileAlreadyExistsError) as exc_info:
            subject.save(plugin)

        assert exc_info.value.plugin == plugin  # noqa: WPS441
