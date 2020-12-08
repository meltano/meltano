import pytest

from meltano.core.plugin import PluginDefinition, PluginType, BasePlugin


class TestProjectPluginsService:
    @pytest.fixture
    def subject(self, project_plugins_service):
        return project_plugins_service

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_plugins(self, subject):
        assert all(isinstance(p.parent, BasePlugin) for p in subject.plugins())

    def test_get_plugin(self, subject, tap):
        subject._use_cache = True  # Disabled by defaults in testing

        plugin = subject.get_plugin(tap)
        assert plugin.type == PluginType.EXTRACTORS
        assert plugin.name == tap.name

        assert isinstance(plugin.parent, BasePlugin)
        assert plugin.parent.name == plugin.name

        # Results are cached
        assert subject.get_plugin(tap) is plugin

        subject._use_cache = False
        assert subject.get_plugin(tap) is not plugin

    def test_update_plugin(self, subject, tap):
        # update a tap with a random value
        tap.config["test"] = 42
        outdated = subject.update_plugin(tap)
        assert subject.get_plugin(tap).config["test"] == 42

        # revert back
        subject.update_plugin(outdated)
        assert subject.get_plugin(tap).config == {}
