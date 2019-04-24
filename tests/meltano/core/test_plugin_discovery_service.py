import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin_discovery_service import PluginDiscoveryService


class TestPluginDiscoveryService:
    @pytest.fixture
    def subject(self, plugin_discovery_service):
        return plugin_discovery_service

    @pytest.fixture
    def extraneous_plugin(self, subject):
        subject.discovery["turboencabulators"] = [{"name": "v1", "config": None}]

    @pytest.fixture
    def discovery_yaml(self, subject):
        """Disable the discovery mock"""
        subject._discovery = None

    def test_plugins(self, subject):
        plugins = list(subject.plugins())

        assert subject.discovery
        assert len(plugins) == 6

    @pytest.mark.usefixtures("extraneous_plugin")
    def test_plugins_unknown(self, subject):
        plugins = list(subject.plugins())
        assert len(plugins) == 6

    def test_discovery(self, subject):
        # test for a specific plugin type
        discovery = subject.discover(PluginType.EXTRACTORS)
        assert PluginType.EXTRACTORS in discovery
        assert PluginType.LOADERS not in discovery

        # test for all
        discovery = subject.discover(PluginType.ALL)
        for t in PluginType:
            if t is PluginType.ALL:
                continue

            assert t in discovery
            assert isinstance(discovery[t], list)

    @pytest.mark.usefixtures("discovery_yaml")
    def test_discovery_yaml(self, subject):
        # test for all
        discovery = subject.discover(PluginType.ALL)

        # raw yaml load
        for plugin_type, plugin_defs in subject._discovery.items():
            plugin_type = PluginType(plugin_type)
            plugin_names = [
                plugin["name"]
                for plugin in sorted(plugin_defs, key=lambda k: k["name"])
            ]

            assert plugin_type in discovery
            assert discovery[plugin_type] == plugin_names

    @pytest.mark.usefixtures("extraneous_plugin")
    def test_discovery_unknown(self, subject):
        # test for all
        discovery = subject.discover(PluginType.ALL)

        for t in PluginType:
            if t is PluginType.ALL:
                continue

            assert t in discovery
            assert isinstance(discovery[t], list)
            assert "turboencabulator" not in discovery
