import pytest

from meltano.core.plugin.base import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin_lock_service import PluginLockService
from meltano.core.project import Project


class TestPluginLockService:
    @pytest.fixture
    def subject(
        self,
        project: Project,
        # plugin_discovery_service: PluginDiscoveryService,
    ):
        return PluginLockService(project)

    def test_save(self, subject: PluginLockService, project: Project):
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
        plugin = BasePlugin(plugin_definition, variant)
        assert plugin.variant == "meltano"

        lock_path = project.plugin_lock_path(plugin.type, plugin.name, "meltano")
        assert not lock_path.exists()

        subject.save(plugin)
        assert lock_path.exists()
