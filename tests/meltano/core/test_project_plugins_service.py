import pytest

from meltano.core.plugin import BasePlugin, PluginDefinition, PluginType
from meltano.core.plugin.error import PluginParentNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin


class TestProjectPluginsService:
    @pytest.fixture
    def subject(self, project_plugins_service):
        return project_plugins_service

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_plugins(self, subject):
        assert all(isinstance(p.parent, BasePlugin) for p in subject.plugins())

    def test_get_plugin(
        self, subject, tap, alternative_tap, inherited_tap, alternative_target
    ):
        subject._use_cache = True  # Disabled by defaults in testing

        # name="tap-mock", variant="meltano"
        plugin = subject.get_plugin(tap)
        assert plugin.type == PluginType.EXTRACTORS
        assert plugin.name == "tap-mock"
        assert plugin.variant == "meltano"
        assert plugin.parent

        # name="tap-mock--singer-io", inherit_from="tap-mock", variant="singer-io"
        alternative_plugin = subject.get_plugin(alternative_tap)
        assert alternative_plugin.type == PluginType.EXTRACTORS
        assert alternative_plugin.name == "tap-mock--singer-io"
        assert alternative_plugin.inherit_from == "tap-mock"
        assert alternative_plugin.variant == "singer-io"
        assert plugin.parent

        # name="tap-mock-inherited", inherit_from="tap-mock"
        inherited_plugin = subject.get_plugin(inherited_tap)
        assert inherited_plugin.type == PluginType.EXTRACTORS
        assert inherited_plugin.name == "tap-mock-inherited"
        assert inherited_plugin.inherit_from == "tap-mock"
        assert plugin.parent

        # name="target-mock-alternative", inherit_from="target-mock"
        alternative_plugin = subject.get_plugin(alternative_target)
        assert alternative_plugin.type == PluginType.LOADERS
        assert alternative_plugin.name == "target-mock-alternative"
        assert alternative_plugin.inherit_from == "target-mock"
        assert plugin.parent

        # Results are cached
        assert subject.get_plugin(tap) is plugin

        subject._use_cache = False
        assert subject.get_plugin(tap) is not plugin

    def test_get_parent(
        self,
        subject,
        tap,
        alternative_tap,
        inherited_tap,
        alternative_target,
        plugin_discovery_service,
    ):
        # name="tap-mock", variant="meltano"
        # Shadows base plugin with correct variant
        assert subject.get_parent(tap) == plugin_discovery_service.find_base_plugin(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant="meltano",
        )

        # name="tap-mock-inherited", inherit_from="tap-mock"
        # Inherits from project plugin
        assert subject.get_parent(inherited_tap) == tap

        # name="tap-mock--singer-io", inherit_from="tap-mock", variant="singer-io"
        # Inherits from base plugin with correct variant
        assert subject.get_parent(
            alternative_tap
        ) == plugin_discovery_service.find_base_plugin(
            plugin_type=PluginType.EXTRACTORS,
            plugin_name="tap-mock",
            variant="singer-io",
        )

        # name="target-mock-alternative", inherit_from="target-mock"
        # Inherits from base plugin because no plugin shadowing the base plugin exists
        assert subject.get_parent(
            alternative_target
        ) == plugin_discovery_service.find_base_plugin(
            plugin_type=PluginType.LOADERS,
            plugin_name="target-mock",
        )

        nonexistent_parent = ProjectPlugin(
            PluginType.EXTRACTORS, name="tap-foo", inherit_from="tap-bar"
        )
        with pytest.raises(PluginParentNotFoundError):
            assert subject.get_parent(nonexistent_parent)

    def test_update_plugin(self, subject, tap):
        # update a tap with a random value
        tap.config["test"] = 42
        outdated = subject.update_plugin(tap)
        assert subject.get_plugin(tap).config["test"] == 42

        # revert back
        subject.update_plugin(outdated)
        assert subject.get_plugin(tap).config == {}
