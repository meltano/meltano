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
